from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Iterable

from .protocol import (
    CAPABILITY_UNAVAILABLE_EXIT_CODE,
    CONTINUATION_UNAVAILABLE_EXIT_CODE,
)


TERMINAL_STATES = {
    "verified_outcome",
    "real_blocker",
    "needs_authorization",
    "no_progress",
}
ALL_STATES = TERMINAL_STATES | {"in_progress"}
EXIT_CODES = {
    "verified_outcome": 0,
    "no_progress": 2,
    "needs_authorization": 3,
    "real_blocker": 4,
    "adapter_error": 5,
}
TASK_ID_PATTERN = re.compile(r"T\d{3}")


def parse_adapter_command(raw: str) -> list[str]:
    try:
        command = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("adapter command must be a JSON array") from error
    if not isinstance(command, list) or not command or not all(
        isinstance(part, str) and part for part in command
    ):
        raise ValueError("adapter command must be a non-empty JSON array of strings")
    return command


def _validate_turn(value: object) -> dict:
    if not isinstance(value, dict):
        raise ValueError("adapter result must be a JSON object")
    state = value.get("terminal_state")
    if state not in ALL_STATES:
        raise ValueError(f"unsupported terminal_state: {state!r}")
    summary = value.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("adapter result requires a non-empty summary")
    normalized = dict(value)
    normalized.setdefault("evidence_refs", [])
    normalized.setdefault("requested_user_instruction", False)
    normalized.setdefault("progress_made", state == "verified_outcome")
    normalized.setdefault("progress_fingerprint", "")
    normalized.setdefault("root_cause", "")
    normalized.setdefault("context_loaded", [])
    normalized.setdefault("rubric_scores", {})
    if isinstance(normalized["rubric_scores"], list):
        normalized["rubric_scores"] = {
            str(item["criterion"]): item["score"]
            for item in normalized["rubric_scores"]
            if isinstance(item, dict) and "criterion" in item and "score" in item
        }
    if not isinstance(normalized["rubric_scores"], dict):
        raise ValueError("rubric_scores must be an object or criterion-score array")
    normalized.setdefault("commands_run", [])
    normalized.setdefault("observations", [])
    normalized.setdefault("modified_files", [])
    normalized.setdefault("adapter_metadata", {})
    task_id = normalized.get("task_id", "")
    if task_id and (
        not isinstance(task_id, str) or not TASK_ID_PATTERN.fullmatch(task_id)
    ):
        raise ValueError("task_id must use the T### format")
    route = normalized.get("session_route")
    if route is not None:
        if not task_id:
            raise ValueError("session_route requires the completed task_id")
        if not isinstance(route, dict):
            raise ValueError("session_route must be an object")
        batch_id = route.get("batch_id")
        if not isinstance(batch_id, str) or not re.fullmatch(r"B\d{3}", batch_id):
            raise ValueError("session_route.batch_id must use the B### format")
        next_task = route.get("task_id")
        if not isinstance(next_task, str) or not TASK_ID_PATTERN.fullmatch(next_task):
            raise ValueError("session_route.task_id must use the T### format")
        mode = route.get("mode")
        if mode not in {"fresh", "continue"}:
            raise ValueError("session_route.mode must be fresh or continue")
        from_task = route.get("from_task")
        if mode == "continue":
            if not isinstance(from_task, str) or not TASK_ID_PATTERN.fullmatch(
                from_task
            ):
                raise ValueError(
                    "continue session_route requires from_task in T### format"
                )
        elif from_task is not None:
            raise ValueError("fresh session_route must not declare from_task")
    preflight = normalized.get("capability_preflight")
    if preflight is not None:
        if state != "in_progress":
            raise ValueError("capability_preflight requires in_progress")
        if not isinstance(preflight, dict):
            raise ValueError("capability_preflight must be an object")
        if preflight.get("phase") != "final_verification":
            raise ValueError(
                "capability_preflight.phase must be final_verification"
            )
        capabilities = preflight.get("required_capabilities")
        if (
            not isinstance(capabilities, list)
            or not capabilities
            or any(
                not isinstance(item, str)
                or not re.fullmatch(r"[a-z][a-z0-9_-]*", item)
                for item in capabilities
            )
            or len(capabilities) != len(set(capabilities))
        ):
            raise ValueError(
                "capability_preflight.required_capabilities must contain unique capability ids"
            )
    return normalized


def _workflow_scope_roots(workspace: Path, prompt: str) -> list[Path]:
    implementations = [
        path
        for path in workspace.rglob("IMPLEMENTATION.md")
        if path.is_file() and not path.is_symlink() and ".git" not in path.parts
    ]
    target = re.search(r"Target batch:\s*(B\d{3})", prompt, flags=re.IGNORECASE)
    if target:
        batch_id = target.group(1)
        matched = [
            path.parent
            for path in implementations
            if re.search(
                rf"(?m)^Batch:\s*`?{re.escape(batch_id)}`?\s*$",
                path.read_text(encoding="utf-8"),
            )
        ]
        if len(matched) != 1:
            raise ValueError(
                f"Target batch {batch_id} does not resolve to exactly one IMPLEMENTATION.md"
            )
        return matched
    if len(implementations) == 1:
        return [implementations[0].parent]
    active = [
        path.parent
        for path in implementations
        if re.search(
            r"(?m)^Status:\s*`?(?:active|failed_validation|blocked)`?\s*$",
            path.read_text(encoding="utf-8"),
        )
    ]
    if len(active) == 1:
        return active
    if implementations:
        raise ValueError(
            "workflow scope is ambiguous; supply Target batch: B###"
        )
    return []


def _scoped_files(workspace: Path, roots: list[Path], filename: str) -> list[Path]:
    if roots:
        return [path for root in roots if (path := root / filename).is_file()]
    candidates = [
        path
        for path in workspace.rglob(filename)
        if path.is_file() and not path.is_symlink() and ".git" not in path.parts
    ]
    return candidates if len(candidates) == 1 else []


def _executable_next_actions(workspace: Path, roots: list[Path]) -> list[str]:
    actions = []
    for path in _scoped_files(workspace, roots, "PROGRESS_STATE.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(
                r"\s*(?:[-*]\s*)?Executable next action:\s*(.+?)\s*$",
                line,
                flags=re.IGNORECASE,
            )
            if match and match.group(1).lower() not in {"none", "not applicable"}:
                actions.append(f"{path.relative_to(workspace)}: {match.group(1)}")
    return actions


def _declared_validation_capabilities(
    workspace: Path, roots: list[Path]
) -> list[str]:
    capabilities = set()
    for path in _scoped_files(workspace, roots, "IMPLEMENTATION.md"):
        for raw in re.findall(
            r"(?m)^\s*required_capabilities:\s*\[([^]]+)\]\s*$",
            path.read_text(encoding="utf-8"),
        ):
            for item in raw.split(","):
                capability = item.strip().strip("'\"")
                if re.fullmatch(r"[a-z][a-z0-9_-]*", capability):
                    capabilities.add(capability)
    return sorted(capabilities)


def _all_declared_tasks_finished(workspace: Path, roots: list[Path]) -> bool:
    statuses = []
    for path in _scoped_files(workspace, roots, "IMPLEMENTATION.md"):
        text = path.read_text(encoding="utf-8")
        statuses.extend(
            re.findall(
                r"(?mi)^\s*T\d{3}\s+status:\s*([a-z_]+)(?:;.*)?\s*$",
                text,
            )
        )
        statuses.extend(
            match.group(1)
            for match in re.finditer(
                r"(?ms)^\s*- id:\s*T\d{3}\s*$.*?^\s+status:\s*([a-z_]+)\s*$",
                text,
            )
        )
    return bool(statuses) and all(
        status in {"done", "superseded"} for status in statuses
    )


def _continuation_prompt(previous: dict) -> str:
    return (
        "Resume the original request in the same session from its durable state. "
        "Return the next result using the required response schema.\n\n"
        f"Previous internal checkpoint: {previous['summary']}\n"
    )


def _fresh_task_prompt(original_prompt: str, task_id: str, reason: str = "") -> str:
    fallback = (
        f" The requested continuation was unavailable ({reason}); record that "
        "fallback truthfully in durable progress evidence."
        if reason
        else ""
    )
    return (
        f"{original_prompt}\n\n"
        f"Start task {task_id} in a fresh provider session.{fallback} "
        "Do not rely on prior conversation history. Reconstruct the minimum "
        "necessary context from PROGRESS_STATE.md, the selected task and "
        "Execution policy in IMPLEMENTATION.md, its feature_refs in FEATURE.md, "
        "AGENTS.md, routed references and skills, and repository code/tests. "
        "Preserve all lifecycle, validation, traceability, authorization, and "
        "security gates. Return the next result using the required response schema.\n"
    )


def _planned_session_contracts(workspace: Path) -> list[dict]:
    contracts = []
    for path in workspace.rglob("IMPLEMENTATION.md"):
        if not path.is_file() or path.is_symlink() or ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        batch = re.search(r"(?m)^Batch:\s*`?(B\d{3})`?\s*$", text)
        if not batch:
            continue
        task_matches = list(re.finditer(r"(?m)^- id: (T\d{3})\s*$", text))
        if not task_matches:
            continue
        task_ids = [match.group(1) for match in task_matches]
        sessions = {}
        statuses = {}
        dependencies = {}
        for index, match in enumerate(task_matches):
            end = (
                task_matches[index + 1].start()
                if index + 1 < len(task_matches)
                else len(text)
            )
            block = text[match.end() : end]
            status = re.search(r"(?m)^  status:\s*([a-z_]+)\s*$", block)
            if status:
                statuses[match.group(1)] = status.group(1)
            dependency_block = re.search(
                r"(?ms)^  dependencies:\s*(?:\[\])?\s*\n?"
                r"(?P<body>(?:^    - T\d{3}\s*$\n?)*)",
                block,
            )
            dependencies[match.group(1)] = (
                re.findall(r"(?m)^    - (T\d{3})\s*$", dependency_block.group("body"))
                if dependency_block
                else []
            )
            session = re.search(
                r"(?ms)^  session:\s*\n(?P<body>(?:^    .*\n?)*)", block
            )
            if not session:
                continue
            body = session.group("body")
            mode = re.search(r"(?m)^    mode:\s*(fresh|continue)\s*$", body)
            from_task = re.search(r"(?m)^    from_task:\s*(T\d{3})\s*$", body)
            if mode:
                sessions[match.group(1)] = {
                    "mode": mode.group(1),
                    "from_task": from_task.group(1) if from_task else "",
                }
        contracts.append(
            {
                "path": str(path),
                "batch_id": batch.group(1),
                "task_ids": task_ids,
                "statuses": statuses,
                "dependencies": dependencies,
                "sessions": sessions,
            }
        )
    return contracts


def _validate_planned_session_route(
    *, workspace: Path, completed_task: str, route: dict
) -> None:
    candidates = []
    for contract in _planned_session_contracts(workspace):
        if contract["batch_id"] != route["batch_id"]:
            continue
        task_ids = contract["task_ids"]
        if completed_task not in task_ids or route["task_id"] not in task_ids:
            continue
        planned = contract["sessions"].get(route["task_id"])
        if planned:
            candidates.append((contract, planned))
    matches = [
        contract
        for contract, planned in candidates
        if planned["mode"] == route["mode"]
        and planned.get("from_task", "") == route.get("from_task", "")
        and contract["statuses"].get(completed_task) == "done"
        and contract["statuses"].get(route["task_id"])
        in {"planned", "in_progress", "failed_validation", "blocked"}
        and all(
            contract["statuses"].get(dependency) == "done"
            for dependency in contract["dependencies"].get(route["task_id"], [])
        )
        and (
            route["mode"] == "fresh"
            or contract["statuses"].get(route["from_task"]) == "done"
        )
        and (
            route["mode"] == "fresh"
            or contract["task_ids"].index(route["from_task"])
            < contract["task_ids"].index(route["task_id"])
        )
    ]
    if len(matches) != 1:
        raise ValueError(
            "session_route does not match one unambiguous durable task contract"
        )


def _resolve_session_route(
    route: dict, session_tokens_by_task: dict[str, str]
) -> tuple[str, bool, dict]:
    requested_mode = route["mode"]
    requested_from = route.get("from_task", "")
    routing = {
        "batch_id": route["batch_id"],
        "next_task": route["task_id"],
        "requested_mode": requested_mode,
        "requested_from_task": requested_from,
        "effective_mode": requested_mode,
        "fallback_reason": "",
    }
    if requested_mode == "fresh":
        return "", True, routing
    token = session_tokens_by_task.get(
        f"{route['batch_id']}:{requested_from}", ""
    )
    if token:
        return token, False, routing
    routing["effective_mode"] = "fresh"
    routing["fallback_reason"] = "source_session_unavailable"
    return "", True, routing


def run_outcome_loop(
    *,
    workspace: Path,
    prompt: str,
    adapter_command: Iterable[str],
    max_turns: int = 24,
    adapter_timeout_seconds: int = 1800,
    case_id: str = "",
    blueprint: Path | None = None,
) -> tuple[dict, int]:
    if max_turns < 1:
        raise ValueError("max_turns must be at least 1")
    if adapter_timeout_seconds < 1:
        raise ValueError("adapter_timeout_seconds must be at least 1")
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    try:
        scope_roots = _workflow_scope_roots(workspace, prompt)
    except ValueError as error:
        return (
            {
                "schema_version": 1,
                "terminal_state": "adapter_error",
                "summary": str(error),
                "internal_turns": 0,
                "visible_user_interventions": 0,
                "trajectory": [],
            },
            EXIT_CODES["adapter_error"],
        )
    declared_capabilities = _declared_validation_capabilities(
        workspace, scope_roots
    )
    repair_preparation_required = bool(
        declared_capabilities
        and _all_declared_tasks_finished(workspace, scope_roots)
    )
    trajectory = []
    visible_user_interventions = 0
    no_progress_streak = 0
    previous_root_cause = None
    previous_progress_fingerprint = ""
    resume_token = ""
    next_prompt = prompt
    session_tokens_by_task: dict[str, str] = {}
    session_start = {
        "requested_mode": "fresh",
        "effective_mode": "fresh",
        "fallback_reason": "initial_session",
    }
    required_capabilities: list[str] = []
    capability_preflight_completed = False
    final_preflight_active = False
    if repair_preparation_required:
        required_capabilities = ["filesystem"]
        next_prompt = (
            f"{prompt}\n\n"
            "Enter finalization repair preparation only. Complete every safe, "
            "authorized, independent in-scope repair that does not require final "
            "batch validation. Do not run batch validation and do not mutate "
            "batch, source-item, or final task lifecycle owners. When the repair "
            "list is empty, return in_progress with capability_preflight for the "
            "declared final-verification capabilities: "
            + ", ".join(declared_capabilities)
        )

    with tempfile.TemporaryDirectory(prefix="feature-execution-") as temp_directory:
        temp_root = Path(temp_directory)
        for turn_index in range(1, max_turns + 1):
            prompt_path = temp_root / f"turn-{turn_index}-prompt.txt"
            turn_result_path = temp_root / f"turn-{turn_index}-result.json"
            prompt_path.write_text(next_prompt, encoding="utf-8")
            environment = {
                **os.environ,
                "FEATURE_EXECUTION_WORKSPACE": str(workspace),
                "FEATURE_EXECUTION_PROMPT_FILE": str(prompt_path),
                "FEATURE_EXECUTION_RESULT_FILE": str(turn_result_path),
                "FEATURE_EXECUTION_TURN_INDEX": str(turn_index),
                "FEATURE_EXECUTION_CASE_ID": case_id,
                "FEATURE_EXECUTION_RESUME_TOKEN": resume_token,
                "FEATURE_EXECUTION_REQUIRED_CAPABILITIES": json.dumps(
                    required_capabilities
                ),
            }
            if blueprint is not None:
                environment["FEATURE_EXECUTION_BLUEPRINT"] = str(blueprint.resolve())

            try:
                completed = subprocess.run(
                    list(adapter_command),
                    cwd=workspace,
                    env=environment,
                    text=True,
                    capture_output=True,
                    timeout=adapter_timeout_seconds,
                    check=False,
                )
                if (
                    completed.returncode == CONTINUATION_UNAVAILABLE_EXIT_CODE
                    and resume_token
                ):
                    fallback_task = str(session_start.get("task_id", ""))
                    if not TASK_ID_PATTERN.fullmatch(fallback_task):
                        raise RuntimeError(
                            "adapter reported unavailable continuation without a "
                            "routed task id"
                        )
                    prompt_path.write_text(
                        _fresh_task_prompt(
                            prompt,
                            fallback_task,
                            "provider_continuation_unavailable",
                        ),
                        encoding="utf-8",
                    )
                    environment["FEATURE_EXECUTION_RESUME_TOKEN"] = ""
                    completed = subprocess.run(
                        list(adapter_command),
                        cwd=workspace,
                        env=environment,
                        text=True,
                        capture_output=True,
                        timeout=adapter_timeout_seconds,
                        check=False,
                    )
                    resume_token = ""
                    if trajectory and "session_routing" in trajectory[-1]:
                        trajectory[-1]["session_routing"]["effective_mode"] = "fresh"
                        trajectory[-1]["session_routing"][
                            "fallback_reason"
                        ] = "provider_continuation_unavailable"
                    session_start = {
                        **session_start,
                        "effective_mode": "fresh",
                        "fallback_reason": "provider_continuation_unavailable",
                    }
                if completed.returncode == CAPABILITY_UNAVAILABLE_EXIT_CODE:
                    detail = completed.stderr.strip() or (
                        "selected adapter profile lacks a required final-verification capability"
                    )
                    executable_next = _executable_next_actions(
                        workspace, scope_roots
                    )
                    if executable_next:
                        trajectory.append(
                            {
                                "turn": turn_index,
                                "terminal_state": "in_progress",
                                "summary": (
                                    "capability blocker rejected while executable "
                                    "repair actions remain"
                                ),
                                "progress_made": False,
                                "progress_fingerprint": "",
                                "new_progress_evidence": False,
                                "root_cause": "premature_capability_preflight",
                                "requested_user_instruction": False,
                                "evidence_refs": [],
                                "context_loaded": [],
                                "rubric_scores": {},
                                "commands_run": [],
                                "observations": executable_next,
                                "modified_files": [],
                                "adapter_metadata": {},
                                "task_id": "",
                                "session_start": session_start,
                                "capability_preflight_completed": False,
                                "terminal_state_rejected": {
                                    "reason": "executable_next_action_remains",
                                    "actions": executable_next,
                                },
                            }
                        )
                        required_capabilities = []
                        capability_preflight_completed = False
                        final_preflight_active = False
                        next_prompt = (
                            "Capability preflight was premature because safe "
                            "executable repair actions remain. Complete them before "
                            "requesting final-verification capability preflight.\n\n"
                            + "\n".join(executable_next)
                        )
                        continue
                    outcome = {
                        "schema_version": 1,
                        "terminal_state": "real_blocker",
                        "summary": (
                            detail
                            + "; no alternate capable adapter or execution profile "
                            "is configured for this run"
                        ),
                        "evidence_refs": [
                            "capability_preflight:no_alternate_profile_configured"
                        ],
                        "internal_turns": turn_index - 1,
                        "visible_user_interventions": visible_user_interventions,
                        "resume_token": resume_token,
                        "trajectory": trajectory,
                    }
                    return outcome, EXIT_CODES["real_blocker"]
                if completed.returncode != 0:
                    raise RuntimeError(
                        f"adapter exited {completed.returncode}: {completed.stderr.strip()}"
                    )
                if not turn_result_path.exists():
                    raise RuntimeError("adapter did not write FEATURE_EXECUTION_RESULT_FILE")
                turn = _validate_turn(
                    json.loads(turn_result_path.read_text(encoding="utf-8"))
                )
                if final_preflight_active and required_capabilities:
                    capability_preflight_completed = True
                if (
                    turn.get("session_route") is not None
                    and turn["terminal_state"] == "in_progress"
                ):
                    _validate_planned_session_route(
                        workspace=workspace,
                        completed_task=str(turn.get("task_id", "")),
                        route=turn["session_route"],
                    )
            except (
                OSError,
                RuntimeError,
                ValueError,
                json.JSONDecodeError,
                subprocess.TimeoutExpired,
            ) as error:
                outcome = {
                    "schema_version": 1,
                    "terminal_state": "adapter_error",
                    "summary": str(error),
                    "internal_turns": turn_index,
                    "visible_user_interventions": visible_user_interventions,
                    "trajectory": trajectory,
                }
                return outcome, EXIT_CODES["adapter_error"]

            resume_token = str(turn.get("resume_token", resume_token))
            task_id = str(turn.get("task_id", ""))
            if (
                turn.get("requested_user_instruction")
                and turn["terminal_state"] == "in_progress"
            ):
                visible_user_interventions += 1

            root_cause = turn.get("root_cause") or ""
            progress_fingerprint = turn.get("progress_fingerprint") or ""
            new_progress_evidence = bool(
                turn.get("progress_made")
                and progress_fingerprint
                and progress_fingerprint != previous_progress_fingerprint
            )
            if turn["terminal_state"] == "in_progress" and not new_progress_evidence:
                if previous_root_cause in {None, root_cause}:
                    no_progress_streak += 1
                else:
                    no_progress_streak = 1
                previous_root_cause = root_cause
            else:
                no_progress_streak = 0
                previous_root_cause = root_cause or None
            if progress_fingerprint:
                previous_progress_fingerprint = progress_fingerprint

            turn_record = {
                "turn": turn_index,
                "terminal_state": turn["terminal_state"],
                "summary": turn["summary"],
                "progress_made": bool(turn.get("progress_made")),
                "progress_fingerprint": progress_fingerprint,
                "new_progress_evidence": new_progress_evidence,
                "root_cause": root_cause,
                "requested_user_instruction": bool(
                    turn.get("requested_user_instruction")
                ),
                "evidence_refs": turn.get("evidence_refs", []),
                "context_loaded": turn.get("context_loaded", []),
                "rubric_scores": turn.get("rubric_scores", {}),
                "commands_run": turn.get("commands_run", []),
                "observations": turn.get("observations", []),
                "modified_files": turn.get("modified_files", []),
                "adapter_metadata": turn.get("adapter_metadata", {}),
                "task_id": task_id,
                "session_start": session_start,
                "capability_preflight": turn.get("capability_preflight"),
                "capability_preflight_completed": capability_preflight_completed,
            }
            route = turn.get("session_route")
            route_starts_fresh = False
            if route is not None and turn["terminal_state"] == "in_progress":
                if task_id and resume_token:
                    session_tokens_by_task[
                        f"{route['batch_id']}:{task_id}"
                    ] = resume_token
                resume_token, route_starts_fresh, routing = _resolve_session_route(
                    route, session_tokens_by_task
                )
                turn_record["session_routing"] = routing
            elif route is not None:
                turn_record["session_routing"] = {
                    "ignored": True,
                    "reason": "terminal_gate_takes_precedence",
                }
                route = None
            trajectory.append(turn_record)

            state = turn["terminal_state"]
            forced_next_prompt = ""
            executable_next = _executable_next_actions(workspace, scope_roots)
            if state in TERMINAL_STATES and executable_next:
                state = "in_progress"
                turn_record["terminal_state_rejected"] = {
                    "reason": "executable_next_action_remains",
                    "actions": executable_next,
                }
                forced_next_prompt = (
                    "The terminal response was rejected because PROGRESS_STATE.md "
                    "still records a safe executable next action. Execute every "
                    "remaining in-scope action before returning a terminal result.\n\n"
                    + "\n".join(executable_next)
                )
            declared_capabilities = _declared_validation_capabilities(
                workspace, scope_roots
            )
            if (
                state == "verified_outcome"
                and declared_capabilities
                and not capability_preflight_completed
            ):
                state = "in_progress"
                turn_record["terminal_state_rejected"] = {
                    "reason": "final_verification_capability_preflight_missing",
                    "required_capabilities": declared_capabilities,
                }
                forced_next_prompt = (
                    "The verified outcome was rejected because declared local "
                    "validation capabilities were not preflighted. Return an "
                    "in_progress capability_preflight for final_verification with "
                    "exactly these required capabilities before final validation "
                    "or lifecycle closure: "
                    + ", ".join(declared_capabilities)
                )
            if state in TERMINAL_STATES:
                outcome = {
                    "schema_version": 1,
                    "terminal_state": state,
                    "summary": turn["summary"],
                    "evidence_refs": turn.get("evidence_refs", []),
                    "internal_turns": turn_index,
                    "visible_user_interventions": visible_user_interventions,
                    "resume_token": resume_token,
                    "trajectory": trajectory,
                }
                return outcome, EXIT_CODES[state]

            preflight = turn.get("capability_preflight")
            if preflight is not None:
                if sorted(preflight["required_capabilities"]) != declared_capabilities:
                    outcome = {
                        "schema_version": 1,
                        "terminal_state": "adapter_error",
                        "summary": (
                            "capability_preflight does not match declared validation "
                            "capabilities"
                        ),
                        "internal_turns": turn_index,
                        "visible_user_interventions": visible_user_interventions,
                        "trajectory": trajectory,
                    }
                    return outcome, EXIT_CODES["adapter_error"]
                required_capabilities = sorted(
                    preflight["required_capabilities"]
                )
                capability_preflight_completed = False
                final_preflight_active = True
                repair_preparation_required = False
                forced_next_prompt = (
                    "Capability preflight passed for the selected adapter profile. "
                    "Continue final verification without changing its declared "
                    "scope, then mutate lifecycle owners only after required proof "
                    "is recorded."
                )
            elif repair_preparation_required:
                forced_next_prompt = (
                    "Remain in finalization repair preparation. Do not run batch "
                    "validation or mutate final lifecycle owners. Complete any "
                    "remaining independent repair; when none remains, return an "
                    "in_progress capability_preflight with exactly: "
                    + ", ".join(declared_capabilities)
                )

            if no_progress_streak >= 3:
                outcome = {
                    "schema_version": 1,
                    "terminal_state": "no_progress",
                    "summary": "three consecutive same-root-cause cycles made no progress",
                    "evidence_refs": turn.get("evidence_refs", []),
                    "internal_turns": turn_index,
                    "visible_user_interventions": visible_user_interventions,
                    "resume_token": resume_token,
                    "trajectory": trajectory,
                }
                return outcome, EXIT_CODES["no_progress"]

            if forced_next_prompt:
                next_prompt = forced_next_prompt
                session_start = {
                    "requested_mode": "continue",
                    "effective_mode": "continue",
                    "fallback_reason": "within_task",
                }
            elif route is None:
                next_prompt = _continuation_prompt(turn)
                session_start = {
                    "requested_mode": "continue",
                    "effective_mode": "continue",
                    "fallback_reason": "within_task",
                }
            elif route_starts_fresh:
                routing = turn_record["session_routing"]
                next_prompt = _fresh_task_prompt(
                    prompt, routing["next_task"], routing["fallback_reason"]
                )
                session_start = {
                    "requested_mode": routing["requested_mode"],
                    "effective_mode": "fresh",
                    "fallback_reason": routing["fallback_reason"] or "planned_fresh",
                    "task_id": routing["next_task"],
                }
            else:
                next_prompt = _continuation_prompt(turn)
                session_start = {
                    "requested_mode": "continue",
                    "effective_mode": "continue",
                    "fallback_reason": "",
                    "from_task": route["from_task"],
                    "task_id": route["task_id"],
                }

    outcome = {
        "schema_version": 1,
        "terminal_state": "no_progress",
        "summary": f"maximum internal turns reached: {max_turns}",
        "evidence_refs": [],
        "internal_turns": max_turns,
        "visible_user_interventions": visible_user_interventions,
        "resume_token": resume_token,
        "trajectory": trajectory,
    }
    return outcome, EXIT_CODES["no_progress"]
