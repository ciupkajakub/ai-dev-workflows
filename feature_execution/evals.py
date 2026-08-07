from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import tempfile
import zlib

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

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


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


def _load_judge_calibration(path: Path, judge_model: str) -> dict:
    try:
        calibration = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid judge calibration file: {error}") from error
    revision = calibration.get("calibration_revision")
    examples = calibration.get("human_rated_examples")
    calibrated_model = calibration.get("judge_model")
    maximum_error = calibration.get("maximum_mean_absolute_error")
    if not isinstance(revision, str) or not revision.strip():
        raise ValueError("judge calibration requires calibration_revision")
    if calibrated_model != judge_model or judge_model in {"", "unknown"}:
        raise ValueError("judge model must match the calibrated judge_model")
    if not isinstance(examples, list) or len(examples) < 3:
        raise ValueError("judge calibration requires at least 3 human-rated examples")
    if (
        isinstance(maximum_error, bool)
        or not isinstance(maximum_error, (int, float))
        or not 0 <= maximum_error <= 1
    ):
        raise ValueError(
            "judge calibration requires maximum_mean_absolute_error between 0 and 1"
        )
    example_ids = [example.get("id") for example in examples if isinstance(example, dict)]
    if (
        len(example_ids) != len(examples)
        or any(not isinstance(example_id, str) or not example_id for example_id in example_ids)
        or len(set(example_ids)) != len(example_ids)
    ):
        raise ValueError("judge calibration requires unique example ids")

    score_pairs = []
    for example in examples:
        human_scores = example.get("human_scores")
        judge_scores = example.get("judge_scores")
        if isinstance(human_scores, dict) and isinstance(judge_scores, dict):
            if not human_scores or set(human_scores) != set(judge_scores):
                raise ValueError("judge predictions must match human-rated criteria")
            score_pairs.extend(
                (human_scores[name], judge_scores[name]) for name in human_scores
            )
        elif "human_score" in example and "judge_score" in example:
            score_pairs.append((example["human_score"], example["judge_score"]))
        else:
            raise ValueError("judge predictions are required for human-rated examples")
    if not all(
        not isinstance(score, bool)
        and isinstance(score, (int, float))
        and 0 <= score <= 10
        for pair in score_pairs
        for score in pair
    ):
        raise ValueError("human and judge calibration scores must be between 0 and 10")
    mean_absolute_error = sum(
        abs(float(human) - float(predicted)) for human, predicted in score_pairs
    ) / len(score_pairs)
    if mean_absolute_error > maximum_error:
        raise ValueError(
            "judge calibration exceeds maximum_mean_absolute_error: "
            f"{mean_absolute_error:.4f}>{maximum_error:.4f}"
        )
    return {
        "calibration_revision": revision,
        "calibration_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "calibration_file": str(path.resolve()),
        "human_rated_examples": len(examples),
        "calibration_rating_pairs": len(score_pairs),
        "calibration_mean_absolute_error": round(mean_absolute_error, 4),
        "calibration_maximum_mean_absolute_error": maximum_error,
        "judge_model": judge_model,
    }


def _valid_png_evidence(path: Path) -> bool:
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if not data.startswith(PNG_SIGNATURE):
        return False
    offset = len(PNG_SIGNATURE)
    width = height = channels = None
    compressed = bytearray()
    saw_header = False
    saw_end = False
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            return False
        payload = data[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack(">I", data[offset + 8 + length : chunk_end])[0]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != expected_crc:
            return False
        if kind == b"IHDR":
            if saw_header or offset != len(PNG_SIGNATURE) or length != 13:
                return False
            width, height, bit_depth, color_type, compression, filtering, interlace = (
                struct.unpack(">IIBBBBB", payload)
            )
            if (
                width < 1
                or height < 1
                or bit_depth != 8
                or color_type not in {2, 6}
                or compression != 0
                or filtering != 0
                or interlace != 0
            ):
                return False
            channels = 3 if color_type == 2 else 4
            saw_header = True
        elif kind == b"IDAT":
            if not saw_header or saw_end:
                return False
            compressed.extend(payload)
        elif kind == b"IEND":
            if length != 0 or not saw_header or not compressed:
                return False
            saw_end = True
            offset = chunk_end
            break
        offset = chunk_end
    if not saw_end or offset != len(data) or None in {width, height, channels}:
        return False
    row_bytes = int(width) * int(channels)
    expected_size = int(height) * (row_bytes + 1)
    if expected_size > 100 * 1024 * 1024:
        return False
    try:
        decoder = zlib.decompressobj()
        pixels = decoder.decompress(bytes(compressed), expected_size + 1)
    except zlib.error:
        return False
    if len(pixels) != expected_size or not decoder.eof or decoder.unused_data:
        return False
    return all(pixels[row * (row_bytes + 1)] <= 4 for row in range(int(height)))


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
        copied.append(
            {
                "path": str(destination.resolve()),
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            }
        )

    return {
        "manifest": str(manifest_path.resolve()),
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "patch": str(patch_path.resolve()),
        "patch_sha256": hashlib.sha256(patch_path.read_bytes()).hexdigest(),
        "git_status": str(status_path.resolve()),
        "git_status_sha256": hashlib.sha256(status_path.read_bytes()).hexdigest(),
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
    judge_provenance: dict | None,
    trial_number: int,
) -> tuple[dict | None, list[str]]:
    if not case.get("external_judgment_required"):
        return None, []
    if not judge_command or not judge_provenance:
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
            "FEATURE_EXECUTION_JUDGE_MODEL": str(
                judge_provenance["judge_model"]
            ),
            "FEATURE_EXECUTION_JUDGE_CALIBRATION_FILE": str(
                judge_provenance["calibration_file"]
            ),
            "FEATURE_EXECUTION_JUDGE_CALIBRATION_SHA256": str(
                judge_provenance["calibration_sha256"]
            ),
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
        if (
            judgment.get("judge_model") != judge_provenance["judge_model"]
            or judgment.get("calibration_sha256")
            != judge_provenance["calibration_sha256"]
        ):
            return None, ["external_judge_provenance_mismatch"]
        evidence_refs = judgment.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            return None, ["external_judge_missing_visual_evidence"]
        for raw_reference in evidence_refs:
            reference = Path(str(raw_reference))
            if not reference.is_absolute():
                reference = workspace / reference
            try:
                resolved = reference.resolve()
                resolved.relative_to(workspace.resolve())
            except (OSError, ValueError):
                return None, ["external_judge_unsafe_visual_evidence"]
            if (
                not resolved.is_file()
                or resolved.suffix.lower() != ".png"
                or resolved.stat().st_size > 10 * 1024 * 1024
                or not _valid_png_evidence(resolved)
            ):
                return None, ["external_judge_invalid_visual_evidence"]
        judgment["label"] = judge_label
        judgment["provenance"] = judge_provenance
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
        elif judge.get("judge_model") in {None, "", "unknown"}:
            failures.append("configuration_unknown:judge_model")
        elif (
            not judge.get("calibration_revision")
            or not judge.get("calibration_sha256")
            or not isinstance(judge.get("human_rated_examples"), int)
            or judge.get("human_rated_examples") < 3
            or not isinstance(judge.get("calibration_rating_pairs"), int)
            or judge.get("calibration_rating_pairs") < 3
            or not isinstance(
                judge.get("calibration_mean_absolute_error"), (int, float)
            )
            or not isinstance(
                judge.get("calibration_maximum_mean_absolute_error"), (int, float)
            )
            or not 0
            <= judge.get("calibration_mean_absolute_error")
            <= judge.get("calibration_maximum_mean_absolute_error")
            <= 1
        ):
            failures.append("external_judge_not_calibrated")
        elif judge.get("entrypoint") in {None, "", "unknown"} or judge.get(
            "entrypoint_sha256"
        ) in {None, "", "unknown"}:
            failures.append("external_judge_identity_unverified")
        elif (
            judge.get("command_sha256")
            == configuration.get("adapter", {}).get("command_sha256")
            or judge.get("entrypoint_sha256")
            == configuration.get("adapter", {}).get("entrypoint_sha256")
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
                "sum": sum(turns),
                "denominator": len(turns),
                "mean": round(sum(turns) / len(turns), 2),
            },
            "visible_user_interventions": sum(
                trial["outcome"]["visible_user_interventions"]
                for trial in case_trials
            ),
        }
    return results


def _aggregate_results(trials: list[dict], case_ids: list[str]) -> dict:
    trials_total = len(trials)
    trials_passed = sum(1 for trial in trials if trial["passed"])
    cases_passed = sum(
        1
        for case_id in case_ids
        if all(trial["passed"] for trial in trials if trial["case_id"] == case_id)
    )
    zero_intervention_trials = sum(
        1
        for trial in trials
        if trial["outcome"]["visible_user_interventions"] == 0
    )
    trials_with_user_steering = trials_total - zero_intervention_trials
    avoidable_interventions = sum(
        trial["outcome"]["visible_user_interventions"] for trial in trials
    )
    internal_turns_total = sum(
        trial["outcome"]["internal_turns"] for trial in trials
    )
    return {
        "cases_passed": cases_passed,
        "cases_total": len(case_ids),
        "trials_passed": trials_passed,
        "trials_total": trials_total,
        "avoidable_user_interventions": avoidable_interventions,
        "trials_with_no_user_steering": zero_intervention_trials,
        "trials_with_user_steering": trials_with_user_steering,
        "trials_with_no_user_steering_rate": round(
            zero_intervention_trials / trials_total, 4
        ),
        "avoidable_user_intervention_rate": round(
            trials_with_user_steering / trials_total, 4
        ),
        "internal_turns_total": internal_turns_total,
        "internal_turns_denominator": trials_total,
        "mean_internal_turns": round(internal_turns_total / trials_total, 2),
    }


def _observed_tradeoffs(trials: list[dict]) -> list[dict]:
    tradeoffs = []
    for case_id, result in _case_variance(trials).items():
        if result["passed"] < result["total"]:
            tradeoffs.append(
                {
                    "case_id": case_id,
                    "type": "reliability",
                    "passed_trials": result["passed"],
                    "total_trials": result["total"],
                }
            )
        if result["internal_turns"]["minimum"] != result["internal_turns"]["maximum"]:
            tradeoffs.append(
                {
                    "case_id": case_id,
                    "type": "turn_variance",
                    "minimum": result["internal_turns"]["minimum"],
                    "maximum": result["internal_turns"]["maximum"],
                }
            )
    return tradeoffs


def _command_entrypoint(command: list[str]) -> Path | None:
    if len(command) == 1:
        candidate = Path(command[0]).expanduser()
    elif (
        len(command) == 2
        and re.fullmatch(r"python(?:3(?:\.\d+)?)?", Path(command[0]).name)
    ):
        candidate = Path(command[1]).expanduser()
    else:
        return None
    try:
        resolved = candidate.resolve()
    except OSError:
        return None
    return resolved if resolved.is_file() else None


def _command_entrypoint_metadata(command: list[str]) -> dict:
    entrypoint = _command_entrypoint(command)
    return {
        "entrypoint": str(entrypoint) if entrypoint else "unknown",
        "entrypoint_sha256": (
            hashlib.sha256(entrypoint.read_bytes()).hexdigest()
            if entrypoint
            else "unknown"
        ),
    }


def _reference_adapter_verified(
    adapter_command: list[str],
    trials: list[dict],
    model: str,
    effort: str,
    tools: str,
) -> tuple[bool, dict]:
    reference = Path(__file__).resolve().parents[1] / "adapters" / "codex_exec.py"
    reference_selected = _command_entrypoint(adapter_command) == reference.resolve()
    turns = [
        turn
        for trial in trials
        for turn in trial.get("outcome", {}).get("trajectory", [])
    ]
    provider_fields = (
        "codex_executable",
        "codex_executable_sha256",
        "codex_version",
        "codex_args_sha256",
        "sandbox",
    )
    provider_fingerprints = {
        tuple(turn.get("adapter_metadata", {}).get(field) for field in provider_fields)
        for turn in turns
    }
    runtime_consistent = len(provider_fingerprints) == 1
    attested = bool(turns) and all(
        turn.get("adapter_metadata", {}).get("behavioral_agent") is True
        and turn.get("adapter_metadata", {}).get("command_evidence_source")
        == "codex_jsonl_events"
        and turn.get("adapter_metadata", {}).get("model") == model
        and turn.get("adapter_metadata", {}).get("effort") == effort
        and turn.get("adapter_metadata", {}).get("tools") == tools
        and turn.get("adapter_metadata", {}).get("codex_binary_verified") is True
        and turn.get("adapter_metadata", {}).get("codex_binary_override") is False
        and re.fullmatch(
            r"[0-9a-f]{64}",
            str(
                turn.get("adapter_metadata", {}).get(
                    "codex_executable_sha256", ""
                )
            ),
        )
        and turn.get("adapter_metadata", {}).get("codex_expected_sha256")
        == turn.get("adapter_metadata", {}).get("codex_executable_sha256")
        and re.fullmatch(
            r"[0-9a-f]{64}",
            str(turn.get("adapter_metadata", {}).get("codex_args_sha256", "")),
        )
        and turn.get("adapter_metadata", {}).get("codex_version")
        not in {None, "", "unknown"}
        and turn.get("adapter_metadata", {}).get("sandbox")
        not in {None, "", "unknown"}
        for turn in turns
    ) and runtime_consistent
    first_metadata = turns[0].get("adapter_metadata", {}) if turns else {}
    return reference_selected and attested, {
        "reference_adapter_selected": reference_selected,
        "all_turns_attested": attested,
        "reference_adapter_sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
        "provider_runtime_consistent": runtime_consistent,
        "provider_runtime": {
            field: first_metadata.get(field, "unknown") for field in provider_fields
        },
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
    allow_verifier_commands: bool,
    judge_command: list[str] | None,
    judge_label: str,
    judge_model: str,
    judge_calibration_file: Path | None,
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
    verifier_commands_declared = sum(
        len(case.get("expected", {}).get("verifier_commands", [])) for case in cases
    )
    if verifier_commands_declared and not allow_verifier_commands:
        raise ValueError(
            "suite contains verifier commands; review the suite and pass "
            "--allow-verifier-commands to authorize them with current user permissions"
        )
    external_judgment_required = any(
        case.get("external_judgment_required") for case in cases
    )
    judge_provenance = None
    if judge_command and external_judgment_required:
        if judge_calibration_file is None:
            raise ValueError("an external judge requires --judge-calibration-file")
        judge_provenance = _load_judge_calibration(
            judge_calibration_file, judge_model
        )

    report_dir.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    evidence_root = report_dir / f"{configuration_label}-{run_id}-evidence"
    if judge_provenance and judge_calibration_file:
        evidence_root.mkdir(parents=True, exist_ok=True)
        retained_calibration = evidence_root / "judge-calibration.json"
        shutil.copy2(judge_calibration_file, retained_calibration)
        judge_provenance["calibration_file"] = str(retained_calibration.resolve())
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
                    judge_provenance=judge_provenance,
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
                        "verifier_commands_declared": len(
                            case.get("expected", {}).get("verifier_commands", [])
                        ),
                        "external_judgment_required": bool(
                            case.get("external_judgment_required")
                        ),
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
            **_command_entrypoint_metadata(adapter_command),
        },
        "judge": (
            {
                "label": judge_label,
                "executable": Path(judge_command[0]).name,
                "command_sha256": hashlib.sha256(
                    json.dumps(judge_command).encode("utf-8")
                ).hexdigest(),
                **_command_entrypoint_metadata(judge_command),
                **(judge_provenance or {}),
            }
            if judge_command
            else None
        ),
        "external_judgment_required": external_judgment_required,
        "verifier_commands_authorized": allow_verifier_commands,
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
    case_ids = [case["id"] for case in cases]
    report = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "case_set_revision": suite.get("case_set_revision", "unknown"),
        "case_set": {
            "path": str(suite_path.resolve()),
            "sha256": hashlib.sha256(suite_path.read_bytes()).hexdigest(),
            "case_count": len(cases),
            "case_ids": case_ids,
        },
        "configuration": configuration,
        "aggregate": _aggregate_results(trial_results, case_ids),
        "dimensions": dimensions,
        "hard_gates": hard_gates,
        "variance": _case_variance(trial_results),
        "observed_tradeoffs": _observed_tradeoffs(trial_results),
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


def _retained_evidence_valid(retained: object) -> bool:
    if not isinstance(retained, dict):
        return False
    for path_field, digest_field in (
        ("manifest", "manifest_sha256"),
        ("patch", "patch_sha256"),
        ("git_status", "git_status_sha256"),
    ):
        raw_path = retained.get(path_field)
        digest = retained.get(digest_field)
        if not isinstance(raw_path, str) or not re.fullmatch(
            r"[0-9a-f]{64}", str(digest)
        ):
            return False
        path = Path(raw_path)
        if (
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != digest
        ):
            return False
    referenced_files = retained.get("referenced_files")
    if not isinstance(referenced_files, list):
        return False
    for reference in referenced_files:
        if not isinstance(reference, dict):
            return False
        path = Path(str(reference.get("path", "")))
        digest = reference.get("sha256")
        if (
            not path.is_file()
            or not re.fullmatch(r"[0-9a-f]{64}", str(digest))
            or hashlib.sha256(path.read_bytes()).hexdigest() != digest
        ):
            return False
    return True


def _report_integrity_failures(report: dict, side: str) -> list[str]:
    failures = []
    if report.get("schema_version") != 1:
        failures.append(f"{side}_unsupported_report_schema")
    if set(report.get("dimensions", {})) != set(DIMENSIONS):
        failures.append(f"{side}_incomplete_dimensions")
    if set(report.get("hard_gates", {})) != set(HARD_GATES):
        failures.append(f"{side}_incomplete_hard_gates")
    configuration = report.get("configuration", {})
    failures.extend(_configuration_failures(configuration, side))
    if configuration.get("behavioral_agent"):
        provenance = configuration.get("adapter", {}).get("provenance", {})
        provider_runtime = provenance.get("provider_runtime", {})
        if not (
            provenance.get("reference_adapter_selected") is True
            and provenance.get("all_turns_attested") is True
            and provenance.get("provider_runtime_consistent") is True
            and re.fullmatch(
                r"[0-9a-f]{64}",
                str(provenance.get("reference_adapter_sha256", "")),
            )
            and re.fullmatch(
                r"[0-9a-f]{64}",
                str(provider_runtime.get("codex_executable_sha256", "")),
            )
            and re.fullmatch(
                r"[0-9a-f]{64}",
                str(provider_runtime.get("codex_args_sha256", "")),
            )
            and provider_runtime.get("codex_version") not in {None, "", "unknown"}
            and provider_runtime.get("sandbox") not in {None, "", "unknown"}
        ):
            failures.append(f"{side}_behavioral_adapter_unverified")
    blueprint = configuration.get("blueprint", {})
    if not blueprint.get("revision") or not blueprint.get("sha256"):
        failures.append(f"{side}_incomplete_blueprint_metadata")
    if configuration.get("external_judgment_required"):
        judge = configuration.get("judge") or {}
        calibration_file = Path(str(judge.get("calibration_file", "")))
        calibration_digest = judge.get("calibration_sha256")
        if (
            not calibration_file.is_file()
            or not re.fullmatch(r"[0-9a-f]{64}", str(calibration_digest))
            or hashlib.sha256(calibration_file.read_bytes()).hexdigest()
            != calibration_digest
        ):
            failures.append(f"{side}_judge_calibration_invalid")
        else:
            try:
                recomputed_calibration = _load_judge_calibration(
                    calibration_file, str(judge.get("judge_model", "unknown"))
                )
            except ValueError:
                failures.append(f"{side}_judge_calibration_invalid")
            else:
                calibration_fields = (
                    "calibration_revision",
                    "calibration_sha256",
                    "human_rated_examples",
                    "calibration_rating_pairs",
                    "calibration_mean_absolute_error",
                    "calibration_maximum_mean_absolute_error",
                    "judge_model",
                )
                if any(
                    judge.get(field) != recomputed_calibration.get(field)
                    for field in calibration_fields
                ):
                    failures.append(f"{side}_judge_calibration_metrics_mismatch")

    trials = report.get("trials")
    case_set = report.get("case_set", {})
    case_count = case_set.get("case_count")
    case_ids = case_set.get("case_ids")
    trials_per_case = configuration.get("trials_per_case")
    if (
        not isinstance(trials, list)
        or not isinstance(case_count, int)
        or not isinstance(case_ids, list)
        or len(case_ids) != case_count
        or not all(isinstance(case_id, str) and case_id for case_id in case_ids)
        or len(set(case_ids)) != case_count
        or not isinstance(trials_per_case, int)
        or not all(isinstance(trial, dict) for trial in trials)
        or len(trials) != case_count * trials_per_case
    ):
        failures.append(f"{side}_incomplete_trials")
        return failures
    if configuration.get("behavioral_agent") and case_count < 18:
        failures.append(f"{side}_insufficient_behavioral_cases")
    if bool(configuration.get("external_judgment_required")) != any(
        trial.get("external_judgment_required") is True for trial in trials
    ):
        failures.append(f"{side}_judgment_scope_inconsistent")
    expected_trials = {
        (case_id, trial_number)
        for case_id in case_ids
        for trial_number in range(1, trials_per_case + 1)
    }
    trial_keys_valid = all(
        isinstance(trial.get("case_id"), str)
        and isinstance(trial.get("trial"), int)
        for trial in trials
    )
    actual_trials = (
        {(trial["case_id"], trial["trial"]) for trial in trials}
        if trial_keys_valid
        else set()
    )
    if (
        not trial_keys_valid
        or len(actual_trials) != len(trials)
        or actual_trials != expected_trials
    ):
        failures.append(f"{side}_unbalanced_trials")

    for trial in trials:
        if not isinstance(trial.get("outcome"), dict):
            failures.append(f"{side}_trial_missing_outcome")
            break
        if not isinstance(trial.get("external_judgment_required"), bool):
            failures.append(f"{side}_trial_judgment_scope_missing")
            break
        retained = trial.get("retained_evidence")
        if not _retained_evidence_valid(retained):
            failures.append(f"{side}_trial_retained_evidence_invalid")
            break
        verifier_results = trial.get("verifier_results")
        verifier_count = trial.get("verifier_commands_declared")
        if (
            not isinstance(verifier_results, list)
            or not isinstance(verifier_count, int)
            or verifier_count < 0
            or len(verifier_results) != verifier_count
        ):
            failures.append(f"{side}_trial_missing_verifier_results")
            break
        if verifier_count and not configuration.get("verifier_commands_authorized"):
            failures.append(f"{side}_verifier_commands_unauthorized")
            break
        if bool(trial.get("passed")) != (not trial.get("failures", [])):
            failures.append(f"{side}_trial_pass_flag_inconsistent")
            break
        if bool(trial.get("passed")) and any(
            result.get("exit_code") != 0 for result in verifier_results
        ):
            failures.append(f"{side}_passing_trial_has_failed_verifier")
            break
        if configuration.get("behavioral_agent"):
            trajectory = trial["outcome"].get("trajectory", [])
            provider_runtime = (
                configuration.get("adapter", {})
                .get("provenance", {})
                .get("provider_runtime", {})
            )
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
                and turn.get("adapter_metadata", {}).get("codex_binary_verified")
                is True
                and turn.get("adapter_metadata", {}).get("codex_binary_override")
                is False
                and turn.get("adapter_metadata", {}).get("codex_expected_sha256")
                == turn.get("adapter_metadata", {}).get(
                    "codex_executable_sha256"
                )
                and turn.get("adapter_metadata", {}).get("codex_executable")
                == provider_runtime.get("codex_executable")
                and turn.get("adapter_metadata", {}).get("codex_executable_sha256")
                == provider_runtime.get("codex_executable_sha256")
                and turn.get("adapter_metadata", {}).get("codex_version")
                == provider_runtime.get("codex_version")
                and turn.get("adapter_metadata", {}).get("codex_args_sha256")
                == provider_runtime.get("codex_args_sha256")
                and turn.get("adapter_metadata", {}).get("sandbox")
                == provider_runtime.get("sandbox")
                for turn in trajectory
            ):
                failures.append(f"{side}_trial_adapter_attestation_missing")
                break
        if trial.get("external_judgment_required"):
            judgment = trial.get("external_judgment")
            judge = configuration.get("judge") or {}
            provenance = (
                judgment.get("provenance", {}) if isinstance(judgment, dict) else {}
            )
            if not (
                isinstance(judgment, dict)
                and judgment.get("label") == judge.get("label")
                and judgment.get("judge_model") == judge.get("judge_model")
                and judgment.get("calibration_sha256")
                == judge.get("calibration_sha256")
                and isinstance(judgment.get("rubric_scores"), dict)
                and all(
                    isinstance(score, (int, float)) and not isinstance(score, bool)
                    for score in judgment.get("rubric_scores", {}).values()
                )
                and judgment.get("evidence_refs")
                and retained.get("referenced_files")
                and any(
                    Path(reference["path"]).suffix.lower() == ".png"
                    and _valid_png_evidence(Path(reference["path"]))
                    for reference in retained.get("referenced_files", [])
                )
                and provenance.get("judge_model") == judge.get("judge_model")
                and provenance.get("calibration_revision")
                == judge.get("calibration_revision")
                and provenance.get("calibration_sha256")
                == judge.get("calibration_sha256")
            ):
                failures.append(f"{side}_trial_judgment_incomplete")
                break

    try:
        recomputed_aggregate = _aggregate_results(trials, case_ids)
        recomputed_dimensions = _dimension_results(trials)
        recomputed_gates = _hard_gate_results(trials)
        recomputed_variance = _case_variance(trials)
        recomputed_tradeoffs = _observed_tradeoffs(trials)
    except (KeyError, TypeError, ZeroDivisionError):
        failures.append(f"{side}_trial_data_invalid")
        return failures
    if recomputed_aggregate != report.get("aggregate"):
        failures.append(f"{side}_aggregate_integrity_mismatch")
    if recomputed_dimensions != report.get("dimensions"):
        failures.append(f"{side}_dimension_integrity_mismatch")
    if recomputed_gates != report.get("hard_gates"):
        failures.append(f"{side}_hard_gate_integrity_mismatch")
    if recomputed_variance != report.get("variance"):
        failures.append(f"{side}_variance_integrity_mismatch")
    if recomputed_tradeoffs != report.get("observed_tradeoffs"):
        failures.append(f"{side}_tradeoff_integrity_mismatch")
    recomputed_bar_failures = _acceptance_failures(
        behavioral_agent=bool(configuration.get("behavioral_agent")),
        dimensions=recomputed_dimensions,
        hard_gates=recomputed_gates,
        configuration=configuration,
    )
    if bool(report.get("meets_absolute_bar")) != (not recomputed_bar_failures):
        failures.append(f"{side}_absolute_bar_integrity_mismatch")
    if report.get("absolute_bar_failures") != recomputed_bar_failures:
        failures.append(f"{side}_absolute_bar_failures_mismatch")
    if report.get("accepted") is not False:
        failures.append(f"{side}_standalone_report_claims_acceptance")
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
        before.get("adapter", {}).get("entrypoint_sha256"),
        before.get("adapter", {}).get("provenance", {}).get(
            "reference_adapter_sha256"
        ),
    ) != (
        after.get("harness"),
        after.get("adapter", {}).get("command_sha256"),
        after.get("adapter", {}).get("entrypoint_sha256"),
        after.get("adapter", {}).get("provenance", {}).get(
            "reference_adapter_sha256"
        ),
    ):
        groups.append("harness_and_adapter")
    provider_fields = (
        "codex_executable",
        "codex_executable_sha256",
        "codex_version",
        "codex_args_sha256",
        "sandbox",
    )
    before_provider = (
        before.get("adapter", {}).get("provenance", {}).get("provider_runtime", {})
    )
    after_provider = (
        after.get("adapter", {}).get("provenance", {}).get("provider_runtime", {})
    )
    if tuple(before_provider.get(field) for field in provider_fields) != tuple(
        after_provider.get(field) for field in provider_fields
    ):
        groups.append("provider_runtime")
    judge_fields = (
        "label",
        "executable",
        "command_sha256",
        "entrypoint_sha256",
        "judge_model",
        "calibration_revision",
        "calibration_sha256",
        "human_rated_examples",
        "calibration_rating_pairs",
        "calibration_mean_absolute_error",
        "calibration_maximum_mean_absolute_error",
    )
    before_judge = before.get("judge") or {}
    after_judge = after.get("judge") or {}
    if tuple(before_judge.get(field) for field in judge_fields) != tuple(
        after_judge.get(field) for field in judge_fields
    ):
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
    comparable_case_set = same_revision and same_digest and same_case_count
    regressions = []
    if not same_revision:
        regressions.append("case_set_revision_mismatch")
    if not same_digest:
        regressions.append("case_set_digest_mismatch")
    if not same_case_count:
        regressions.append("case_set_count_mismatch")
    integrity_failures = [
        *_report_integrity_failures(baseline, "baseline"),
        *_report_integrity_failures(candidate, "candidate"),
    ]
    regressions.extend(integrity_failures)
    comparable = comparable_case_set and not integrity_failures
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
