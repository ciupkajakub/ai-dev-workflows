from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
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


def _initialize_git(workspace: Path) -> None:
    subprocess.run(
        ["git", "init", "--quiet"], cwd=workspace, check=True, capture_output=True
    )


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


def _evaluate_case(case: dict, outcome: dict, workspace: Path) -> tuple[bool, list[str]]:
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

    rendered_evidence = "\n".join(
        [outcome.get("summary", "")]
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
        for turn in outcome.get("trajectory", [])
        for item in turn.get("context_loaded", [])
    }
    for item in sorted(required_context - loaded_context):
        failures.append(f"missing_context:{item}")
    for item in sorted(forbidden_context & loaded_context):
        failures.append(f"forbidden_context:{item}")

    required_rubric = expected.get("rubric_minimums", {})
    observed_rubric = {}
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
    for field in ("model", "effort", "tools", "harness"):
        value = configuration.get(field)
        if not isinstance(value, str) or not value.strip() or value == "unknown":
            failures.append(f"configuration_unknown:{field}")
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
        results[case_id] = {
            "pass_rate": round(
                sum(1 for trial in case_trials if trial["passed"])
                / len(case_trials),
                4,
            ),
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
) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", configuration_label):
        raise ValueError(
            "configuration label must contain only letters, numbers, dot, dash, "
            "or underscore"
        )
    suite = load_eval_suite(
        suite_path, minimum_cases=1, require_full_coverage=behavioral_agent
    )
    cases = suite["cases"]
    if trials_per_case < 1:
        raise ValueError("trials must be at least 1")

    trial_results = []
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
                _initialize_git(workspace)
                outcome, _exit_code = run_outcome_loop(
                    workspace=workspace,
                    prompt=case["prompt"],
                    adapter_command=adapter_command,
                    case_id=case["id"],
                    blueprint=candidate_blueprint,
                    max_turns=int(case.get("max_turns", 24)),
                    adapter_timeout_seconds=int(case.get("timeout_seconds", 1800)),
                )
                passed, failures = _evaluate_case(case, outcome, workspace)
                trial_results.append(
                    {
                        "case_id": case["id"],
                        "trial": trial_number,
                        "dimensions": case.get("dimensions", []),
                        "hard_gates": case.get("hard_gates", []),
                        "passed": passed,
                        "failures": failures,
                        "outcome": outcome,
                    }
                )

    dimensions = _dimension_results(trial_results)
    hard_gates = _hard_gate_results(trial_results)
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
        },
        "behavioral_agent": behavioral_agent,
        "trials_per_case": trials_per_case,
    }
    absolute_bar_failures = _acceptance_failures(
        behavioral_agent=behavioral_agent,
        dimensions=dimensions,
        hard_gates=hard_gates,
        configuration=configuration,
    )
    cases_total = len(trial_results)
    zero_intervention_trials = sum(
        1
        for trial in trial_results
        if trial["outcome"]["visible_user_interventions"] == 0
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
            "cases_passed": sum(1 for trial in trial_results if trial["passed"]),
            "cases_total": cases_total,
            "avoidable_user_interventions": sum(
                trial["outcome"]["visible_user_interventions"]
                for trial in trial_results
            ),
            "trials_with_no_user_steering": zero_intervention_trials,
            "trials_with_no_user_steering_rate": round(
                zero_intervention_trials / cases_total, 4
            ),
            "avoidable_user_intervention_rate": round(
                sum(
                    1
                    for trial in trial_results
                    if trial["outcome"]["visible_user_interventions"] > 0
                )
                / cases_total,
                4,
            ),
            "mean_internal_turns": round(
                sum(trial["outcome"]["internal_turns"] for trial in trial_results)
                / cases_total,
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

    report_dir.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
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
        "## Dimensions",
        "",
        "| Dimension | Score | Passed | Total |",
        "|---|---:|---:|---:|",
    ]
    for name, result in report["dimensions"].items():
        score = "unknown" if result["score"] is None else str(result["score"])
        lines.append(f"| {name} | {score} | {result['passed']} | {result['total']} |")
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
            f"terminal `{trial['outcome']['terminal_state']}`"
        )
    return "\n".join(lines) + "\n"


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
    for side, report in (("baseline", baseline), ("candidate", candidate)):
        configuration = report.get("configuration", {})
        for field in ("model", "effort", "tools", "harness"):
            value = configuration.get(field)
            if (
                not isinstance(value, str)
                or not value.strip()
                or value == "unknown"
            ):
                regressions.append(f"{side}_configuration_unknown:{field}")
    baseline_trials = baseline.get("configuration", {}).get("trials_per_case")
    candidate_trials = candidate.get("configuration", {}).get("trials_per_case")
    if baseline_trials != candidate_trials:
        regressions.append(
            f"trials_per_case_mismatch:{baseline_trials}!={candidate_trials}"
        )
    candidate_meets_bar = bool(
        candidate.get("meets_absolute_bar", candidate.get("accepted", False))
    )
    if not candidate_meets_bar:
        regressions.append("candidate_below_absolute_bar")
    return {
        "schema_version": 1,
        "comparable": comparable,
        "candidate_accepted": comparable and candidate_meets_bar and not regressions,
        "regressions": regressions,
        "baseline_label": baseline.get("configuration", {}).get("label", "unknown"),
        "candidate_label": candidate.get("configuration", {}).get("label", "unknown"),
    }
