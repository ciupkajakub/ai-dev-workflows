from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile

from .harness import run_outcome_loop


DIMENSIONS = (
    "outcome_correctness",
    "autonomous_continuity",
    "repair_behavior",
    "downstream_impact_coverage",
    "ui_observable_quality",
    "evidence_status_truthfulness",
    "context_artifact_efficiency",
    "safety_scope_control",
    "usability_without_steering",
    "regression_evaluability",
)

HARD_GATES = (
    "lifecycle_traceability",
    "validation_blocks_completion",
    "authorization_boundary",
    "no_unnecessary_pause",
    "evidence_grounding",
    "repair_and_close",
    "validation_scope",
    "safe_watchdogs",
    "zero_false_claims",
    "consumer_recall",
    "autonomous_repair",
    "low_user_intervention",
    "ui_quality",
    "artifact_efficiency",
    "context_routing",
)

EXPECTED_TERMINAL_STATES = {
    "verified_outcome",
    "real_blocker",
    "needs_authorization",
    "no_progress",
}


def _safe_relative_path(raw: str) -> PurePosixPath:
    value = PurePosixPath(raw)
    if value.is_absolute() or ".." in value.parts:
        raise ValueError(f"unsafe fixture path: {raw}")
    return value


def _write_starting_files(workspace: Path, files: dict[str, str]) -> None:
    for raw_path, content in files.items():
        relative = _safe_relative_path(raw_path)
        target = workspace.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _validate_paths(case: dict) -> None:
    for raw_path in case.get("starting_files", {}):
        _safe_relative_path(raw_path)
    expected = case.get("expected", {})
    for field in ("required_files", "forbidden_files", "unchanged_files"):
        for raw_path in expected.get(field, []):
            _safe_relative_path(raw_path)
    for field in ("required_content", "forbidden_content", "line_limits"):
        for raw_path in expected.get(field, {}):
            _safe_relative_path(raw_path)


def _validate_verifier_commands(case: dict) -> None:
    for command in case.get("expected", {}).get("verifier_commands", []):
        if not isinstance(command, list) or not command or not all(
            isinstance(part, str) and part for part in command
        ):
            raise ValueError(
                f"case {case.get('id', 'unknown')} verifier_commands must contain "
                "non-empty string arrays"
            )


def load_eval_suite(
    path: Path, *, minimum_cases: int = 18, require_full_coverage: bool = True
) -> dict:
    suite = json.loads(path.read_text(encoding="utf-8"))
    revision = suite.get("case_set_revision")
    cases = suite.get("cases")
    if not isinstance(revision, str) or not revision.strip():
        raise ValueError("eval suite requires a non-empty case_set_revision")
    if not isinstance(cases, list) or len(cases) < minimum_cases:
        raise ValueError(f"eval suite requires at least {minimum_cases} cases")

    seen_ids = set()
    covered_dimensions = set()
    covered_gates = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"case {index} must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", case_id):
            raise ValueError(f"case {index} has an invalid id")
        if case_id in seen_ids:
            raise ValueError(f"duplicate case id: {case_id}")
        seen_ids.add(case_id)
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ValueError(f"case {case_id} requires a prompt")
        if not isinstance(case.get("starting_files", {}), dict):
            raise ValueError(f"case {case_id} starting_files must be an object")
        expected = case.get("expected")
        if not isinstance(expected, dict):
            raise ValueError(f"case {case_id} requires expected checks")
        if expected.get("terminal_state") not in EXPECTED_TERMINAL_STATES:
            raise ValueError(f"case {case_id} has an invalid expected terminal_state")
        _validate_paths(case)
        _validate_verifier_commands(case)
        dimensions = case.get("dimensions")
        if not isinstance(dimensions, list) or not dimensions:
            raise ValueError(f"case {case_id} requires dimensions")
        unknown_dimensions = set(dimensions) - set(DIMENSIONS)
        if unknown_dimensions:
            raise ValueError(
                f"case {case_id} has unknown dimensions: {sorted(unknown_dimensions)}"
            )
        gates = case.get("hard_gates")
        if not isinstance(gates, list) or not gates:
            raise ValueError(f"case {case_id} requires hard_gates")
        unknown_gates = set(gates) - set(HARD_GATES)
        if unknown_gates:
            raise ValueError(f"case {case_id} has unknown hard gates: {sorted(unknown_gates)}")
        covered_dimensions.update(dimensions)
        covered_gates.update(gates)

    if require_full_coverage:
        missing_dimensions = set(DIMENSIONS) - covered_dimensions
        missing_gates = set(HARD_GATES) - covered_gates
        if missing_dimensions:
            raise ValueError(f"eval suite misses dimensions: {sorted(missing_dimensions)}")
        if missing_gates:
            raise ValueError(f"eval suite misses hard gates: {sorted(missing_gates)}")
    return suite


def _initialize_git(workspace: Path) -> str:
    subprocess.run(
        ["git", "init", "--quiet"], cwd=workspace, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "add", "--all"], cwd=workspace, check=True, capture_output=True
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Feature Execution Eval",
            "-c",
            "user.email=eval@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "fixture baseline",
        ],
        cwd=workspace,
        check=True,
        capture_output=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=workspace,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _retain_trial_evidence(
    *,
    workspace: Path,
    evidence_root: Path,
    case_id: str,
    trial_number: int,
    fixture_commit: str,
    outcome: dict,
    external_judgment: dict | None,
) -> dict:
    target = evidence_root / case_id / f"trial-{trial_number}"
    target.mkdir(parents=True, exist_ok=True)
    manifest = []
    for path in sorted(workspace.rglob("*")):
        if not path.is_file() or ".git" in path.relative_to(workspace).parts:
            continue
        relative = str(path.relative_to(workspace))
        manifest.append(
            {
                "path": relative,
                "size": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    manifest_path = target / "workspace-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    patch_path = target / "changes.patch"
    patch = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--no-color", fixture_commit, "--"],
        cwd=workspace,
        check=False,
        capture_output=True,
        text=True,
    ).stdout
    patch_path.write_text(patch, encoding="utf-8")
    status_path = target / "git-status.txt"
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=workspace,
        check=False,
        capture_output=True,
        text=True,
    ).stdout
    status_path.write_text(status, encoding="utf-8")

    copied = []
    files_root = target / "files"
    evidence_references = list(outcome.get("evidence_refs", []))
    if external_judgment:
        evidence_references.extend(external_judgment.get("evidence_refs", []))
    for raw_reference in evidence_references:
        reference = Path(str(raw_reference))
        if not reference.is_absolute():
            reference = workspace / reference
        try:
            resolved = reference.resolve()
            resolved.relative_to(workspace.resolve())
        except (OSError, ValueError):
            continue
        if not resolved.is_file() or resolved.stat().st_size > 10 * 1024 * 1024:
            continue
        files_root.mkdir(exist_ok=True)
        prefix = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:10]
        destination = files_root / f"{prefix}-{resolved.name}"
        shutil.copy2(resolved, destination)
        copied.append(str(destination.resolve()))

    return {
        "manifest": str(manifest_path.resolve()),
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "patch": str(patch_path.resolve()),
        "patch_sha256": hashlib.sha256(patch_path.read_bytes()).hexdigest(),
        "git_status": str(status_path.resolve()),
        "referenced_files": copied,
    }


def _run_verifier_commands(case: dict, workspace: Path) -> tuple[list[dict], list[str]]:
    results = []
    failures = []
    timeout = int(case.get("verifier_timeout_seconds", 30))
    for command in case.get("expected", {}).get("verifier_commands", []):
        try:
            completed = subprocess.run(
                command,
                cwd=workspace,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            result = {
                "command": command,
                "exit_code": completed.returncode,
                "stdout": completed.stdout[-2000:],
                "stderr": completed.stderr[-2000:],
            }
            if completed.returncode != 0:
                failures.append(f"verifier_failed:{json.dumps(command)}")
        except subprocess.TimeoutExpired:
            result = {
                "command": command,
                "exit_code": None,
                "stdout": "",
                "stderr": f"timed out after {timeout} seconds",
            }
            failures.append(f"verifier_timed_out:{json.dumps(command)}")
        results.append(result)
    return results, failures


def _run_external_judge(
    *,
    case: dict,
    outcome: dict,
    workspace: Path,
    judge_command: list[str] | None,
    judge_label: str,
    trial_number: int,
) -> tuple[dict | None, list[str]]:
    if not case.get("external_judgment_required"):
        return None, []
    if not judge_command:
        return None, ["external_judge_not_configured"]
    with tempfile.TemporaryDirectory(prefix="feature-execution-judge-") as directory:
        root = Path(directory)
        case_path = root / "case.json"
        outcome_path = root / "outcome.json"
        result_path = root / "judgment.json"
        case_path.write_text(json.dumps(case, indent=2), encoding="utf-8")
        outcome_path.write_text(json.dumps(outcome, indent=2), encoding="utf-8")
        environment = {
            **os.environ,
            "FEATURE_EXECUTION_WORKSPACE": str(workspace),
            "FEATURE_EXECUTION_CASE_FILE": str(case_path),
            "FEATURE_EXECUTION_OUTCOME_FILE": str(outcome_path),
            "FEATURE_EXECUTION_JUDGE_RESULT_FILE": str(result_path),
            "FEATURE_EXECUTION_CASE_ID": case["id"],
            "FEATURE_EXECUTION_TRIAL": str(trial_number),
        }
        try:
            completed = subprocess.run(
                judge_command,
                cwd=workspace,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                timeout=int(case.get("judge_timeout_seconds", 300)),
            )
        except subprocess.TimeoutExpired:
            return None, ["external_judge_timed_out"]
        if completed.returncode != 0 or not result_path.exists():
            return None, [f"external_judge_failed:{completed.returncode}"]
        try:
            judgment = json.loads(result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None, ["external_judge_invalid_json"]
        scores = judgment.get("rubric_scores")
        if not isinstance(scores, dict) or not all(
            isinstance(name, str) and isinstance(score, (int, float))
            for name, score in scores.items()
        ):
            return None, ["external_judge_invalid_scores"]
        judgment["label"] = judge_label
        return judgment, []


def _file_expectations(
    workspace: Path, expected: dict, starting_files: dict[str, str]
) -> list[str]:
    failures = []
    for raw_path in expected.get("required_files", []):
        path = workspace.joinpath(*_safe_relative_path(raw_path).parts)
        if not path.exists():
            failures.append(f"missing_required_file:{raw_path}")
    for raw_path in expected.get("forbidden_files", []):
        path = workspace.joinpath(*_safe_relative_path(raw_path).parts)
        if path.exists():
            failures.append(f"forbidden_file_present:{raw_path}")
    for raw_path in expected.get("unchanged_files", []):
        path = workspace.joinpath(*_safe_relative_path(raw_path).parts)
        if raw_path not in starting_files:
            failures.append(f"protected_file_not_in_fixture:{raw_path}")
        elif not path.exists() or path.read_text(encoding="utf-8") != starting_files[raw_path]:
            failures.append(f"changed_protected_file:{raw_path}")
    for raw_path, patterns in expected.get("required_content", {}).items():
        path = workspace.joinpath(*_safe_relative_path(raw_path).parts)
        if not path.exists():
            failures.append(f"missing_content_file:{raw_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            if re.search(pattern, text, flags=re.MULTILINE) is None:
                failures.append(f"missing_content:{raw_path}:{pattern}")
    for raw_path, patterns in expected.get("forbidden_content", {}).items():
        path = workspace.joinpath(*_safe_relative_path(raw_path).parts)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            if re.search(pattern, text, flags=re.MULTILINE) is not None:
                failures.append(f"forbidden_content:{raw_path}:{pattern}")
    for raw_path, limit in expected.get("line_limits", {}).items():
        path = workspace.joinpath(*_safe_relative_path(raw_path).parts)
        if not path.exists():
            failures.append(f"missing_line_limit_file:{raw_path}")
            continue
        actual = len(path.read_text(encoding="utf-8").splitlines())
        if actual > int(limit):
            failures.append(f"line_limit:{raw_path}:{actual}>{limit}")
    return failures


def _evaluate_case(
    case: dict,
    outcome: dict,
    workspace: Path,
    external_judgment: dict | None = None,
) -> tuple[bool, list[str]]:
    expected = case.get("expected", {})
    failures = []
    if outcome["terminal_state"] != expected.get("terminal_state"):
        failures.append(
            f"terminal_state:{outcome['terminal_state']}!={expected.get('terminal_state')}"
        )
    if outcome["internal_turns"] > int(expected.get("max_internal_turns", 24)):
        failures.append("too_many_internal_turns")
    if outcome["visible_user_interventions"] > int(
        expected.get("max_visible_user_interventions", 0)
    ):
        failures.append("avoidable_user_intervention")
    failures.extend(
        _file_expectations(workspace, expected, case.get("starting_files", {}))
    )

    for pattern in expected.get("required_summary", []):
        if re.search(pattern, outcome.get("summary", ""), flags=re.IGNORECASE) is None:
            failures.append(f"missing_summary:{pattern}")
    for pattern in expected.get("forbidden_summary", []):
        if re.search(pattern, outcome.get("summary", ""), flags=re.IGNORECASE) is not None:
            failures.append(f"forbidden_summary:{pattern}")

    commands = [
        command.get("command", "")
        for turn in outcome.get("trajectory", [])
        for command in turn.get("commands_run", [])
        if isinstance(command, dict)
    ]
    rendered_commands = "\n".join(commands)
    for pattern in expected.get("required_commands", []):
        if re.search(pattern, rendered_commands, flags=re.IGNORECASE) is None:
            failures.append(f"missing_command:{pattern}")
    for pattern in expected.get("forbidden_commands", []):
        if re.search(pattern, rendered_commands, flags=re.IGNORECASE) is not None:
            failures.append(f"forbidden_command:{pattern}")

    if external_judgment is not None:
        rendered_evidence = "\n".join(
            [str(external_judgment.get("summary", ""))]
            + [str(item) for item in external_judgment.get("evidence_refs", [])]
        )
    else:
        rendered_evidence = "\n".join(
            [outcome.get("summary", ""), rendered_commands]
            + [
                str(item)
                for turn in outcome.get("trajectory", [])
                for field in ("evidence_refs", "observations")
                for item in turn.get(field, [])
            ]
        )
    for pattern in expected.get("required_evidence", []):
        if re.search(pattern, rendered_evidence, flags=re.IGNORECASE) is None:
            failures.append(f"missing_evidence:{pattern}")

    required_context = set(expected.get("required_context", []))
    forbidden_context = set(expected.get("forbidden_context", []))
    loaded_context = {
        item
        for item in required_context | forbidden_context
        if item in rendered_commands
    }
    for item in sorted(required_context - loaded_context):
        failures.append(f"missing_context:{item}")
    for item in sorted(forbidden_context & loaded_context):
        failures.append(f"forbidden_context:{item}")

    required_rubric = expected.get("rubric_minimums", {})
    observed_rubric = {}
    if case.get("external_judgment_required"):
        if external_judgment is None:
            failures.append("external_judgment_required")
        else:
            observed_rubric.update(external_judgment.get("rubric_scores", {}))
    else:
        for turn in outcome.get("trajectory", []):
            observed_rubric.update(turn.get("rubric_scores", {}))
    for criterion, minimum in required_rubric.items():
        score = observed_rubric.get(criterion)
        if score is None:
            failures.append(f"missing_rubric:{criterion}")
        elif float(score) < float(minimum):
            failures.append(f"rubric_below_minimum:{criterion}:{score}<{minimum}")
    return not failures, failures


def _blueprint_metadata(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    revision_match = re.search(r"^Blueprint revision:\s*`([^`]+)`", text, re.MULTILINE)
    schema_match = re.search(r"^Workflow schema:\s*`([^`]+)`", text, re.MULTILINE)
    return {
        "path": str(path.resolve()),
        "revision": revision_match.group(1) if revision_match else "unknown",
        "workflow_schema": schema_match.group(1) if schema_match else "unknown",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _dimension_results(trials: list[dict]) -> dict:
    results = {}
    for dimension in DIMENSIONS:
        relevant = [trial for trial in trials if dimension in trial["dimensions"]]
        passed = sum(1 for trial in relevant if trial["passed"])
        total = len(relevant)
        results[dimension] = {
            "score": round(10 * passed / total, 2) if total else None,
            "passed": passed,
            "total": total,
        }
    return results


def _hard_gate_results(trials: list[dict]) -> dict:
    gate_names = sorted(
        {gate for trial in trials for gate in trial.get("hard_gates", [])}
    )
    return {
        gate: {
            "passed": all(
                trial["passed"] for trial in trials if gate in trial.get("hard_gates", [])
            ),
            "passed_trials": sum(
                1
                for trial in trials
                if gate in trial.get("hard_gates", []) and trial["passed"]
            ),
            "total": sum(1 for trial in trials if gate in trial.get("hard_gates", [])),
        }
        for gate in gate_names
    }


def _acceptance_failures(
    *,
    behavioral_agent: bool,
    dimensions: dict,
    hard_gates: dict,
    configuration: dict,
) -> list[str]:
    failures = []
    if not behavioral_agent:
        failures.append("adapter_not_behavioral")
    failures.extend(_configuration_failures(configuration, ""))
    if configuration.get("external_judgment_required"):
        judge = configuration.get("judge")
        if not judge:
            failures.append("external_judge_not_configured")
        elif judge.get("label") in {None, "", "unknown"}:
            failures.append("configuration_unknown:judge")
        elif judge.get("command_sha256") == configuration.get("adapter", {}).get(
            "command_sha256"
        ):
            failures.append("external_judge_not_independent")
    for name, result in dimensions.items():
        if result["score"] is None:
            failures.append(f"dimension_unknown:{name}")
        elif result["score"] < 9:
            failures.append(f"dimension_below_9:{name}")
    for name, result in hard_gates.items():
        if not result["passed"]:
            failures.append(f"hard_gate_failed:{name}")
    return failures


def _case_variance(trials: list[dict]) -> dict:
    results = {}
    for case_id in sorted({trial["case_id"] for trial in trials}):
        case_trials = [trial for trial in trials if trial["case_id"] == case_id]
        turns = [trial["outcome"]["internal_turns"] for trial in case_trials]
        passed = sum(1 for trial in case_trials if trial["passed"])
        results[case_id] = {
            "passed": passed,
            "total": len(case_trials),
            "pass_rate": round(passed / len(case_trials), 4),
            "internal_turns": {
                "minimum": min(turns),
                "maximum": max(turns),
                "mean": round(sum(turns) / len(turns), 2),
            },
            "visible_user_interventions": sum(
                trial["outcome"]["visible_user_interventions"]
                for trial in case_trials
            ),
        }
    return results


def _reference_adapter_verified(
    adapter_command: list[str],
    trials: list[dict],
    model: str,
    effort: str,
    tools: str,
) -> tuple[bool, dict]:
    reference = Path(__file__).resolve().parents[1] / "adapters" / "codex_exec.py"
    command_paths = []
    for part in adapter_command:
        path = Path(part).expanduser()
        if path.exists():
            command_paths.append(path.resolve())
    reference_selected = reference.resolve() in command_paths
    turns = [
        turn
        for trial in trials
        for turn in trial.get("outcome", {}).get("trajectory", [])
    ]
    attested = bool(turns) and all(
        turn.get("adapter_metadata", {}).get("behavioral_agent") is True
        and turn.get("adapter_metadata", {}).get("command_evidence_source")
        == "codex_jsonl_events"
        and turn.get("adapter_metadata", {}).get("model") == model
        and turn.get("adapter_metadata", {}).get("effort") == effort
        and turn.get("adapter_metadata", {}).get("tools") == tools
        for turn in turns
    )
    return reference_selected and attested, {
        "reference_adapter_selected": reference_selected,
        "all_turns_attested": attested,
        "reference_adapter_sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
    }


def run_eval_suite(
    *,
    suite_path: Path,
    adapter_command: list[str],
    blueprint: Path,
    configuration_label: str,
    trials_per_case: int,
    report_dir: Path,
    behavioral_agent: bool,
    model: str,
    effort: str,
    tools: str,
    harness_label: str,
    judge_command: list[str] | None,
    judge_label: str,
) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", configuration_label):
        raise ValueError(
            "configuration label must contain only letters, numbers, dot, dash, "
            "or underscore"
        )
    suite = load_eval_suite(
        suite_path,
        minimum_cases=18 if behavioral_agent else 1,
        require_full_coverage=behavioral_agent,
    )
    cases = suite["cases"]
    if trials_per_case < 1:
        raise ValueError("trials must be at least 1")

    report_dir.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    evidence_root = report_dir / f"{configuration_label}-{run_id}-evidence"
    trial_results = []
    expected_blueprint_digest = hashlib.sha256(blueprint.read_bytes()).hexdigest()
    for case in cases:
        for trial_number in range(1, trials_per_case + 1):
            with tempfile.TemporaryDirectory(prefix=f"eval-{case['id']}-") as directory:
                workspace = Path(directory) / "workspace"
                workspace.mkdir()
                _write_starting_files(workspace, case.get("starting_files", {}))
                candidate_blueprint = (
                    workspace / ".feature-execution" / "candidate-blueprint.md"
                )
                candidate_blueprint.parent.mkdir(parents=True)
                shutil.copy2(blueprint, candidate_blueprint)
                candidate_blueprint.chmod(0o444)
                fixture_commit = _initialize_git(workspace)
                outcome, _exit_code = run_outcome_loop(
                    workspace=workspace,
                    prompt=case["prompt"],
                    adapter_command=adapter_command,
                    case_id=case["id"],
                    blueprint=candidate_blueprint,
                    max_turns=int(case.get("max_turns", 24)),
                    adapter_timeout_seconds=int(case.get("timeout_seconds", 1800)),
                )
                external_judgment, judge_failures = _run_external_judge(
                    case=case,
                    outcome=outcome,
                    workspace=workspace,
                    judge_command=judge_command,
                    judge_label=judge_label,
                    trial_number=trial_number,
                )
                passed, failures = _evaluate_case(
                    case, outcome, workspace, external_judgment
                )
                failures.extend(judge_failures)
                verifier_results, verifier_failures = _run_verifier_commands(
                    case, workspace
                )
                failures.extend(verifier_failures)
                passed = not failures
                if (
                    not candidate_blueprint.exists()
                    or hashlib.sha256(candidate_blueprint.read_bytes()).hexdigest()
                    != expected_blueprint_digest
                ):
                    failures.append("candidate_blueprint_modified")
                    passed = False
                retained_evidence = _retain_trial_evidence(
                    workspace=workspace,
                    evidence_root=evidence_root,
                    case_id=case["id"],
                    trial_number=trial_number,
                    fixture_commit=fixture_commit,
                    outcome=outcome,
                    external_judgment=external_judgment,
                )
                trial_results.append(
                    {
                        "case_id": case["id"],
                        "trial": trial_number,
                        "dimensions": case.get("dimensions", []),
                        "hard_gates": case.get("hard_gates", []),
                        "passed": passed,
                        "failures": failures,
                        "outcome": outcome,
                        "verifier_results": verifier_results,
                        "external_judgment": external_judgment,
                        "retained_evidence": retained_evidence,
                    }
                )

    dimensions = _dimension_results(trial_results)
    hard_gates = _hard_gate_results(trial_results)
    behavioral_agent_verified, adapter_provenance = _reference_adapter_verified(
        adapter_command, trial_results, model, effort, tools
    )
    effective_behavioral_agent = behavioral_agent and behavioral_agent_verified
    configuration = {
        "label": configuration_label,
        "blueprint": _blueprint_metadata(blueprint),
        "model": model,
        "effort": effort,
        "tools": tools,
        "harness": harness_label,
        "adapter": {
            "executable": Path(adapter_command[0]).name,
            "command_sha256": hashlib.sha256(
                json.dumps(adapter_command).encode("utf-8")
            ).hexdigest(),
            "provenance": adapter_provenance,
        },
        "judge": (
            {
                "label": judge_label,
                "executable": Path(judge_command[0]).name,
                "command_sha256": hashlib.sha256(
                    json.dumps(judge_command).encode("utf-8")
                ).hexdigest(),
            }
            if judge_command
            else None
        ),
        "external_judgment_required": any(
            case.get("external_judgment_required") for case in cases
        ),
        "behavioral_agent": effective_behavioral_agent,
        "behavioral_agent_asserted": behavioral_agent,
        "trials_per_case": trials_per_case,
    }
    absolute_bar_failures = _acceptance_failures(
        behavioral_agent=effective_behavioral_agent,
        dimensions=dimensions,
        hard_gates=hard_gates,
        configuration=configuration,
    )
    trials_total = len(trial_results)
    trials_passed = sum(1 for trial in trial_results if trial["passed"])
    cases_passed = sum(
        1
        for case in cases
        if all(
            trial["passed"]
            for trial in trial_results
            if trial["case_id"] == case["id"]
        )
    )
    zero_intervention_trials = sum(
        1
        for trial in trial_results
        if trial["outcome"]["visible_user_interventions"] == 0
    )
    trials_with_user_steering = trials_total - zero_intervention_trials
    internal_turns_total = sum(
        trial["outcome"]["internal_turns"] for trial in trial_results
    )
    report = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "case_set_revision": suite.get("case_set_revision", "unknown"),
        "case_set": {
            "path": str(suite_path.resolve()),
            "sha256": hashlib.sha256(suite_path.read_bytes()).hexdigest(),
            "case_count": len(cases),
        },
        "configuration": configuration,
        "aggregate": {
            "cases_passed": cases_passed,
            "cases_total": len(cases),
            "trials_passed": trials_passed,
            "trials_total": trials_total,
            "avoidable_user_interventions": sum(
                trial["outcome"]["visible_user_interventions"]
                for trial in trial_results
            ),
            "trials_with_no_user_steering": zero_intervention_trials,
            "trials_with_user_steering": trials_with_user_steering,
            "trials_with_no_user_steering_rate": round(
                zero_intervention_trials / trials_total, 4
            ),
            "avoidable_user_intervention_rate": round(
                trials_with_user_steering / trials_total,
                4,
            ),
            "internal_turns_total": internal_turns_total,
            "internal_turns_denominator": trials_total,
            "mean_internal_turns": round(
                internal_turns_total / trials_total,
                2,
            ),
        },
        "dimensions": dimensions,
        "hard_gates": hard_gates,
        "variance": _case_variance(trial_results),
        "trials": trial_results,
        "meets_absolute_bar": not absolute_bar_failures,
        "absolute_bar_failures": absolute_bar_failures,
        "accepted": False,
        "acceptance_failures": [
            *absolute_bar_failures,
            "baseline_comparison_required",
        ],
    }

    report_json = report_dir / f"{configuration_label}-{run_id}.json"
    report_markdown = report_dir / f"{configuration_label}-{run_id}.md"
    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report_markdown.write_text(_render_markdown(report), encoding="utf-8")
    return {
        "report": report,
        "report_json": str(report_json.resolve()),
        "report_markdown": str(report_markdown.resolve()),
    }


def _render_markdown(report: dict) -> str:
    lines = [
        f"# Feature Execution evaluation: {report['configuration']['label']}",
        "",
        f"- Case set: `{report['case_set_revision']}`",
        f"- Blueprint revision: `{report['configuration']['blueprint']['revision']}`",
        f"- Blueprint digest: `{report['configuration']['blueprint']['sha256']}`",
        f"- Behavioral agent: `{str(report['configuration']['behavioral_agent']).lower()}`",
        f"- Meets absolute bar: `{str(report['meets_absolute_bar']).lower()}`",
        f"- Accepted: `{str(report['accepted']).lower()}`",
        "",
        "## Aggregate",
        "",
        f"- Passed cases: {report['aggregate']['cases_passed']}/"
        f"{report['aggregate']['cases_total']}",
        f"- Passed trials: {report['aggregate']['trials_passed']}/"
        f"{report['aggregate']['trials_total']}",
        "- Trials without user steering: "
        f"{report['aggregate']['trials_with_no_user_steering']}/"
        f"{report['aggregate']['trials_total']}",
        "- Trials with avoidable user steering: "
        f"{report['aggregate']['trials_with_user_steering']}/"
        f"{report['aggregate']['trials_total']}",
        "- Mean internal turns: "
        f"{report['aggregate']['internal_turns_total']}/"
        f"{report['aggregate']['internal_turns_denominator']} = "
        f"{report['aggregate']['mean_internal_turns']}",
        "",
        "## Dimensions",
        "",
        "| Dimension | Score | Passed | Total |",
        "|---|---:|---:|---:|",
    ]
    for name, result in report["dimensions"].items():
        score = "unknown" if result["score"] is None else str(result["score"])
        lines.append(f"| {name} | {score} | {result['passed']} | {result['total']} |")
    lines.extend(
        [
            "",
            "## Hard gates",
            "",
            "| Gate | Passed | Passed trials | Total |",
            "|---|---|---:|---:|",
        ]
    )
    for name, result in report["hard_gates"].items():
        lines.append(
            f"| {name} | {str(result['passed']).lower()} | "
            f"{result['passed_trials']} | {result['total']} |"
        )
    lines.extend(["", "## Acceptance failures", ""])
    if report["acceptance_failures"]:
        lines.extend(f"- `{failure}`" for failure in report["acceptance_failures"])
    else:
        lines.append("- None")
    lines.extend(["", "## Trials", ""])
    for trial in report["trials"]:
        lines.append(
            f"- `{trial['case_id']}` trial {trial['trial']}: "
            f"{'pass' if trial['passed'] else 'fail'}; "
            f"terminal `{trial['outcome']['terminal_state']}`; "
            f"manifest `{trial['retained_evidence']['manifest']}`; "
            f"failures `{', '.join(trial['failures']) or 'none'}`"
        )
    return "\n".join(lines) + "\n"


def _configuration_failures(configuration: dict, prefix: str) -> list[str]:
    failures = []
    for field in ("model", "effort", "tools", "harness"):
        value = configuration.get(field)
        if not isinstance(value, str) or not value.strip() or value == "unknown":
            scope = f"{prefix}_" if prefix else ""
            failures.append(f"{scope}configuration_unknown:{field}")
    return failures


def _report_integrity_failures(report: dict, side: str) -> list[str]:
    failures = []
    if set(report.get("dimensions", {})) != set(DIMENSIONS):
        failures.append(f"{side}_incomplete_dimensions")
    if set(report.get("hard_gates", {})) != set(HARD_GATES):
        failures.append(f"{side}_incomplete_hard_gates")
    configuration = report.get("configuration", {})
    failures.extend(_configuration_failures(configuration, side))
    if configuration.get("behavioral_agent"):
        provenance = configuration.get("adapter", {}).get("provenance", {})
        if not (
            provenance.get("reference_adapter_selected") is True
            and provenance.get("all_turns_attested") is True
        ):
            failures.append(f"{side}_behavioral_adapter_unverified")
    blueprint = configuration.get("blueprint", {})
    if not blueprint.get("revision") or not blueprint.get("sha256"):
        failures.append(f"{side}_incomplete_blueprint_metadata")

    trials = report.get("trials")
    case_count = report.get("case_set", {}).get("case_count")
    trials_per_case = configuration.get("trials_per_case")
    if (
        not isinstance(trials, list)
        or not isinstance(case_count, int)
        or not isinstance(trials_per_case, int)
        or len(trials) != case_count * trials_per_case
    ):
        failures.append(f"{side}_incomplete_trials")
        return failures
    if configuration.get("behavioral_agent") and case_count < 18:
        failures.append(f"{side}_insufficient_behavioral_cases")
    if len({trial.get("case_id") for trial in trials}) != case_count:
        failures.append(f"{side}_case_count_inconsistent")
    for trial in trials:
        if not isinstance(trial.get("outcome"), dict):
            failures.append(f"{side}_trial_missing_outcome")
            break
        retained = trial.get("retained_evidence")
        if not isinstance(retained, dict) or not all(
            retained.get(field)
            for field in ("manifest", "manifest_sha256", "patch", "patch_sha256")
        ):
            failures.append(f"{side}_trial_missing_retained_evidence")
            break
        if not isinstance(trial.get("verifier_results"), list):
            failures.append(f"{side}_trial_missing_verifier_results")
            break
        if bool(trial.get("passed")) != (not trial.get("failures", [])):
            failures.append(f"{side}_trial_pass_flag_inconsistent")
            break
        if bool(trial.get("passed")) and any(
            result.get("exit_code") != 0 for result in trial["verifier_results"]
        ):
            failures.append(f"{side}_passing_trial_has_failed_verifier")
            break
        if configuration.get("behavioral_agent"):
            trajectory = trial["outcome"].get("trajectory", [])
            if not trajectory or not all(
                turn.get("adapter_metadata", {}).get("behavioral_agent") is True
                and turn.get("adapter_metadata", {}).get("command_evidence_source")
                == "codex_jsonl_events"
                and turn.get("adapter_metadata", {}).get("model")
                == configuration.get("model")
                and turn.get("adapter_metadata", {}).get("effort")
                == configuration.get("effort")
                and turn.get("adapter_metadata", {}).get("tools")
                == configuration.get("tools")
                for turn in trajectory
            ):
                failures.append(f"{side}_trial_adapter_attestation_missing")
                break

    try:
        recomputed_dimensions = _dimension_results(trials)
        recomputed_gates = _hard_gate_results(trials)
    except (KeyError, TypeError, ZeroDivisionError):
        failures.append(f"{side}_trial_data_invalid")
        return failures
    if recomputed_dimensions != report.get("dimensions"):
        failures.append(f"{side}_dimension_integrity_mismatch")
    if recomputed_gates != report.get("hard_gates"):
        failures.append(f"{side}_hard_gate_integrity_mismatch")
    recomputed_bar_failures = _acceptance_failures(
        behavioral_agent=bool(configuration.get("behavioral_agent")),
        dimensions=recomputed_dimensions,
        hard_gates=recomputed_gates,
        configuration=configuration,
    )
    if bool(report.get("meets_absolute_bar")) != (not recomputed_bar_failures):
        failures.append(f"{side}_absolute_bar_integrity_mismatch")
    return failures


def _changed_variable_groups(baseline: dict, candidate: dict) -> list[str]:
    before = baseline.get("configuration", {})
    after = candidate.get("configuration", {})
    groups = []
    blueprint_fields = ("revision", "workflow_schema", "sha256")
    before_blueprint = before.get("blueprint", {})
    after_blueprint = after.get("blueprint", {})
    if tuple(before_blueprint.get(field) for field in blueprint_fields) != tuple(
        after_blueprint.get(field) for field in blueprint_fields
    ):
        groups.append("blueprint")
    if (before.get("model"), before.get("effort")) != (
        after.get("model"),
        after.get("effort"),
    ):
        groups.append("model_and_effort")
    if before.get("tools") != after.get("tools"):
        groups.append("tools")
    if (
        before.get("harness"),
        before.get("adapter", {}).get("command_sha256"),
    ) != (
        after.get("harness"),
        after.get("adapter", {}).get("command_sha256"),
    ):
        groups.append("harness_and_adapter")
    if before.get("judge") != after.get("judge"):
        groups.append("judge")
    return groups


def compare_reports(baseline: dict, candidate: dict) -> dict:
    same_revision = baseline.get("case_set_revision") == candidate.get(
        "case_set_revision"
    )
    baseline_case_set = baseline.get("case_set", {})
    candidate_case_set = candidate.get("case_set", {})
    same_digest = bool(baseline_case_set.get("sha256")) and baseline_case_set.get(
        "sha256"
    ) == candidate_case_set.get("sha256")
    same_case_count = baseline_case_set.get("case_count") == candidate_case_set.get(
        "case_count"
    )
    comparable = same_revision and same_digest and same_case_count
    regressions = []
    if not same_revision:
        regressions.append("case_set_revision_mismatch")
    if not same_digest:
        regressions.append("case_set_digest_mismatch")
    if not same_case_count:
        regressions.append("case_set_count_mismatch")
    regressions.extend(_report_integrity_failures(baseline, "baseline"))
    regressions.extend(_report_integrity_failures(candidate, "candidate"))
    for name in DIMENSIONS:
        before = baseline.get("dimensions", {}).get(name, {}).get("score")
        after = candidate.get("dimensions", {}).get(name, {}).get("score")
        if before is not None and after is not None and after < before:
            regressions.append(f"dimension_regressed:{name}:{before}->{after}")
        if before is None:
            regressions.append(f"baseline_dimension_unknown:{name}")
    if not baseline.get("configuration", {}).get("behavioral_agent"):
        regressions.append("baseline_not_behavioral")
    if not candidate.get("configuration", {}).get("behavioral_agent"):
        regressions.append("candidate_not_behavioral")
    baseline_trials = baseline.get("configuration", {}).get("trials_per_case")
    candidate_trials = candidate.get("configuration", {}).get("trials_per_case")
    if baseline_trials != candidate_trials:
        regressions.append(
            f"trials_per_case_mismatch:{baseline_trials}!={candidate_trials}"
        )
    candidate_configuration = candidate.get("configuration", {})
    candidate_bar_failures = _acceptance_failures(
        behavioral_agent=bool(candidate_configuration.get("behavioral_agent")),
        dimensions=candidate.get("dimensions", {}),
        hard_gates=candidate.get("hard_gates", {}),
        configuration=candidate_configuration,
    )
    candidate_meets_bar = not candidate_bar_failures
    if not candidate_meets_bar:
        regressions.append("candidate_below_absolute_bar")
    changed_variable_groups = _changed_variable_groups(baseline, candidate)
    if not changed_variable_groups:
        regressions.append("no_variable_group_changed")
    elif len(changed_variable_groups) > 1:
        regressions.append(
            "multiple_variable_groups_changed:" + ",".join(changed_variable_groups)
        )
    return {
        "schema_version": 1,
        "comparable": comparable,
        "candidate_accepted": comparable and candidate_meets_bar and not regressions,
        "regressions": regressions,
        "changed_variable_groups": changed_variable_groups,
        "baseline_label": baseline.get("configuration", {}).get("label", "unknown"),
        "candidate_label": candidate.get("configuration", {}).get("label", "unknown"),
    }
