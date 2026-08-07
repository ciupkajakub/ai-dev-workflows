from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .doctor import inspect_workflow
from .evals import compare_reports, run_eval_suite
from .harness import parse_adapter_command, run_outcome_loop


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="feature-execution",
        description=(
            "Executable harness and evaluation support for the Feature Execution "
            "Blueprint."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="validate generated workflow artifacts")
    doctor.add_argument("workflow_root", type=Path)
    doctor.add_argument("--blueprint", type=Path)

    run = subparsers.add_parser("run", help="drive one batch to a terminal outcome")
    run.add_argument("--workspace", type=Path, required=True)
    run.add_argument("--prompt-file", type=Path, required=True)
    run.add_argument("--adapter-command", required=True)
    run.add_argument("--result", type=Path, required=True)
    run.add_argument("--max-turns", type=int, default=24)
    run.add_argument("--adapter-timeout-seconds", type=int, default=1800)
    run.add_argument("--blueprint", type=Path)

    evaluate = subparsers.add_parser("eval", help="run a versioned behavioral case set")
    evaluate.add_argument("--suite", type=Path, required=True)
    evaluate.add_argument("--adapter-command", required=True)
    evaluate.add_argument("--blueprint", type=Path, required=True)
    evaluate.add_argument("--configuration-label", required=True)
    evaluate.add_argument("--trials", type=int, default=3)
    evaluate.add_argument("--report-dir", type=Path, required=True)
    evaluate.add_argument("--behavioral-agent", action="store_true")
    evaluate.add_argument("--model", default="unknown")
    evaluate.add_argument("--effort", default="unknown")
    evaluate.add_argument("--tools", default="unknown")
    evaluate.add_argument("--harness-label", default="feature-execution-v1")

    compare = subparsers.add_parser("compare", help="compare baseline and candidate reports")
    compare.add_argument("--baseline", type=Path, required=True)
    compare.add_argument("--candidate", type=Path, required=True)
    compare.add_argument("--output", type=Path)
    return parser


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "doctor":
            report = inspect_workflow(args.workflow_root, args.blueprint)
            print(json.dumps(report, indent=2))
            return 0 if report["valid"] else 1

        if args.command == "run":
            command = parse_adapter_command(args.adapter_command)
            prompt = args.prompt_file.read_text(encoding="utf-8")
            outcome, exit_code = run_outcome_loop(
                workspace=args.workspace,
                prompt=prompt,
                adapter_command=command,
                max_turns=args.max_turns,
                adapter_timeout_seconds=args.adapter_timeout_seconds,
                blueprint=args.blueprint,
            )
            args.result.parent.mkdir(parents=True, exist_ok=True)
            args.result.write_text(json.dumps(outcome, indent=2), encoding="utf-8")
            print(json.dumps(outcome, indent=2))
            return exit_code

        if args.command == "eval":
            result = run_eval_suite(
                suite_path=args.suite,
                adapter_command=parse_adapter_command(args.adapter_command),
                blueprint=args.blueprint,
                configuration_label=args.configuration_label,
                trials_per_case=args.trials,
                report_dir=args.report_dir,
                behavioral_agent=args.behavioral_agent,
                model=args.model,
                effort=args.effort,
                tools=args.tools,
                harness_label=args.harness_label,
            )
            print(
                json.dumps(
                    {
                        "report_json": result["report_json"],
                        "report_markdown": result["report_markdown"],
                        "meets_absolute_bar": result["report"]["meets_absolute_bar"],
                        "accepted": result["report"]["accepted"],
                    },
                    indent=2,
                )
            )
            return 0

        if args.command == "compare":
            baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
            candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
            comparison = compare_reports(baseline, candidate)
            rendered = json.dumps(comparison, indent=2)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(rendered, encoding="utf-8")
            print(rendered)
            return 0 if comparison["candidate_accepted"] else 1
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 64
    return 64
