from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Iterable


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
    return normalized


def _continuation_prompt(previous: dict) -> str:
    return (
        "Resume the original request in the same session from its durable state. "
        "Return the next result using the required response schema.\n\n"
        f"Previous internal checkpoint: {previous['summary']}\n"
    )


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
    trajectory = []
    visible_user_interventions = 0
    no_progress_streak = 0
    previous_root_cause = None
    previous_progress_fingerprint = ""
    resume_token = ""
    next_prompt = prompt

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
                if completed.returncode != 0:
                    raise RuntimeError(
                        f"adapter exited {completed.returncode}: {completed.stderr.strip()}"
                    )
                if not turn_result_path.exists():
                    raise RuntimeError("adapter did not write FEATURE_EXECUTION_RESULT_FILE")
                turn = _validate_turn(
                    json.loads(turn_result_path.read_text(encoding="utf-8"))
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
            }
            trajectory.append(turn_record)

            state = turn["terminal_state"]
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

            next_prompt = _continuation_prompt(turn)

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
