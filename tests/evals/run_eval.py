#!/usr/bin/env python3
"""Run workflow scenarios in disposable repositories and grade observable results."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import io
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

EVALS = Path(__file__).resolve().parent
SOURCE = EVALS.parents[1]
SCENARIOS = EVALS / "scenarios"
sys.path.insert(0, str(EVALS))

from grading import Context  # noqa: E402

CLAUDE_TOOLS = "Bash Read Edit Write Glob Grep Skill Agent"
CHECK_COMMAND = r"(unittest|check\.sh|e2e/run\.sh)"
IDENTITY = ("-c", "user.name=Eval fixture", "-c", "user.email=eval@localhost",
            "-c", "commit.gpgsign=false")


def scenario_ids():
    return sorted(path.name for path in SCENARIOS.iterdir() if (path / "grade.py").is_file())


def load_grader(scenario):
    path = SCENARIOS / scenario / "grade.py"
    spec = importlib.util.spec_from_file_location(f"grade_{scenario}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(path, *args):
    return subprocess.run(
        ["git", "-C", str(path), *IDENTITY, *args], capture_output=True, text=True, check=True,
    ).stdout.strip()


def resolve_instructions(reference):
    if reference == "none":
        return "none"
    return subprocess.run(
        ["git", "-C", str(SOURCE), "rev-parse", "--verify", f"{reference}^{{commit}}"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def install_package(workspace, commit):
    tooling = workspace / "ai-workflow" / "tooling"
    tooling.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(
        ["git", "-C", str(SOURCE), "archive", "--format=tar", commit, "LICENSE", "skills"],
        capture_output=True, check=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(tooling, filter="tar")
    for provider in (".claude", ".agents"):
        directory = workspace / provider / "skills"
        directory.mkdir(parents=True)
        (directory / "workflow").symlink_to("../../ai-workflow/tooling/skills/workflow")


def prepare_workspace(scenario, instructions, workspace):
    """Build a fresh repository holding only what a real project would hold."""
    shutil.copytree(SCENARIOS / scenario / "repo", workspace)
    (workspace / ".gitignore").write_text("__pycache__/\n*.pyc\n")
    if instructions != "none":
        install_package(workspace, instructions)
    git(workspace, "init", "-q", "-b", "main")
    git(workspace, "add", "-A")
    git(workspace, "commit", "-qm", "Project state before this work")
    return git(workspace, "rev-parse", "HEAD")


def prompt_for(scenario, instructions):
    text = (SCENARIOS / scenario / "prompt.md").read_text().strip()
    return text if instructions == "none" else f"/workflow {text}"


def claude_command(args):
    return [
        "claude", "-p", "--output-format", "stream-json", "--verbose",
        "--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence",
        "--permission-mode", "acceptEdits", "--allowedTools", CLAUDE_TOOLS,
        "--model", args.model, "--effort", args.effort,
        "--max-budget-usd", str(args.max_budget_usd),
    ]


def parse_events(output):
    events = []
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def tool_calls(events):
    seen = set()
    for event in events:
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                if block.get("id") not in seen:
                    seen.add(block.get("id"))
                    yield block.get("name"), block.get("input") or {}


def behavior_metrics(events):
    """Observations that inform diagnosis. They never change a verdict."""
    commands = [call.get("command", "") for name, call in tool_calls(events) if name == "Bash"]
    serialized = [json.dumps(call) for _, call in tool_calls(events)]
    return {
        "bash_commands": len(commands),
        "commit_after_semicolon": sum(
            bool(re.search(r";\s*git\s+(commit|push)\b", command)) for command in commands
        ),
        "checks_piped_without_pipefail": sum(
            bool(re.search(CHECK_COMMAND + r"[^;&]*\|\s*(tail|head|grep|sed|awk)\b", command))
            and "pipefail" not in command for command in commands
        ),
        "subagents": sum(name == "Agent" for name, _ in tool_calls(events)),
        "instructions_read": sorted({
            name for name in ("prepare.md", "deliver.md", "verify.md")
            if any(f"/{name}" in text or f" {name}" in text for text in serialized)
        }),
    }


def grade(scenario, workspace, base, final_message, events=()):
    context = Context(Path(workspace), base, final_message, list(events))
    criteria = {"responded": bool(final_message.strip())}
    criteria.update(load_grader(scenario).grade(context))
    return {"verdict": "pass" if all(criteria.values()) else "fail", "criteria": criteria}


def apply_control(scenario, control, workspace):
    """Commit a canned solution so a grader can be tested without running an agent."""
    directory = SCENARIOS / scenario / "controls" / control
    files = directory / "files"
    if files.is_dir():
        shutil.copytree(files, workspace, dirs_exist_ok=True)
        git(workspace, "add", "-A")
        git(workspace, "commit", "-qm", f"Control: {control}")
    return (directory / "message.txt").read_text()


def check_control(scenario, control, instructions="HEAD"):
    commit = resolve_instructions(instructions)
    with tempfile.TemporaryDirectory(prefix="workflow-eval-control-") as directory:
        workspace = Path(directory) / "workspace"
        base = prepare_workspace(scenario, commit, workspace)
        message = apply_control(scenario, control, workspace) if control != "unchanged" else ""
        return grade(scenario, workspace, base, message)


def run_trial(args, scenario, instructions, number):
    variant = instructions[:12]
    directory = Path(args.out) / scenario / variant / str(number)
    result_file = directory / "result.json"
    if result_file.exists():
        previous = json.loads(result_file.read_text())
        if previous["verdict"] != "invalid":
            return previous
    directory.mkdir(parents=True, exist_ok=True)
    result = {"scenario": scenario, "instructions": instructions, "run": number,
              "model": args.model, "effort": args.effort}
    with tempfile.TemporaryDirectory(prefix="workflow-eval-") as temporary:
        workspace = Path(temporary) / "workspace"
        base = prepare_workspace(scenario, instructions, workspace)
        command = shlex.split(args.executor_command) if args.executor_command else claude_command(args)
        started = time.monotonic()
        try:
            process = subprocess.run(
                command, cwd=workspace, input=prompt_for(scenario, instructions),
                capture_output=True, text=True, timeout=args.timeout,
            )
            output, error, code = process.stdout, process.stderr, process.returncode
        except subprocess.TimeoutExpired as expired:
            output = (expired.stdout or b"").decode(errors="replace")
            error, code = "executor timeout", None
        result["seconds"] = round(time.monotonic() - started)
        (directory / "transcript.jsonl").write_text(output)
        (directory / "stderr.txt").write_text(error)
        events = parse_events(output)
        final = next((e for e in reversed(events) if e.get("type") == "result"), {})
        message = final.get("result") or ""
        result.update(
            cost_usd=final.get("total_cost_usd"), turns=final.get("num_turns"),
            metrics=behavior_metrics(events),
        )
        (directory / "diff.patch").write_text(
            subprocess.run(["git", "-C", str(workspace), "diff", base, "HEAD"],
                           capture_output=True, text=True).stdout
        )
        if code != 0 or final.get("is_error") or not final:
            # An executor that could not finish says nothing about the instructions.
            detail = (error.strip() or message)[-300:]
            result.update(verdict="invalid", reason=f"executor exit {code}: {detail}")
        else:
            result.update(grade(scenario, workspace, base, message, events))
    result_file.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{scenario} {variant} #{number}: {result['verdict']}", flush=True)
    return result


def report(out):
    results = [json.loads(path.read_text()) for path in sorted(Path(out).rglob("result.json"))]
    rows = {}
    for result in results:
        key = (result["scenario"], result["instructions"][:12])
        row = rows.setdefault(key, {"pass": 0, "fail": 0, "invalid": 0, "missed": {}, "cost": 0.0})
        row[result["verdict"]] += 1
        row["cost"] += result.get("cost_usd") or 0
        for name, value in result.get("criteria", {}).items():
            if not value:
                row["missed"][name] = row["missed"].get(name, 0) + 1
    lines = ["| Scenario | Instructions | Pass | Fail | Invalid | Failed criteria | Cost USD |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for (scenario, variant), row in sorted(rows.items()):
        missed = ", ".join(f"{k} x{v}" for k, v in sorted(row["missed"].items())) or "-"
        lines.append(f"| {scenario} | {variant} | {row['pass']} | {row['fail']} | "
                     f"{row['invalid']} | {missed} | {row['cost']:.2f} |")
    text = "\n".join(lines) + "\n"
    (Path(out) / "report.md").write_text(text)
    return text


def command_controls(args):
    failures = 0
    for scenario in args.scenario or scenario_ids():
        for control, expected in (("good", "pass"), ("bad", "fail"), ("unchanged", "fail")):
            result = check_control(scenario, control)
            matches = result["verdict"] == expected
            failures += not matches
            print(f"{'ok ' if matches else 'BAD'} {scenario} {control}: {result['verdict']} "
                  f"{[k for k, v in result['criteria'].items() if not v]}")
    return 1 if failures else 0


def command_run(args):
    scenarios = args.scenario or scenario_ids()
    variants = [resolve_instructions(reference) for reference in args.instructions]
    trials = [(s, v, n) for s in scenarios for v in variants for n in range(1, args.runs + 1)]
    if args.dry_run:
        print(f"{len(trials)} trials, at most ${args.max_budget_usd} each: "
              f"{len(scenarios)} scenarios x {len(variants)} variants x {args.runs} runs")
        print(shlex.join(claude_command(args)))
        return 0
    Path(args.out).mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(lambda trial: run_trial(args, *trial), trials))
    print(report(args.out))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    controls = commands.add_parser("controls", help="Test the graders without running an agent")
    controls.add_argument("--scenario", action="append")
    controls.set_defaults(handler=command_controls)
    trial = commands.add_parser("run", help="Run agent trials; this uses paid model capacity")
    trial.add_argument("--instructions", action="append", required=True,
                       help="Committed source revision, or 'none'; repeat to compare")
    trial.add_argument("--out", required=True)
    trial.add_argument("--scenario", action="append")
    trial.add_argument("--runs", type=int, default=5)
    trial.add_argument("--jobs", type=int, default=1)
    trial.add_argument("--model", default="claude-opus-5-5")
    trial.add_argument("--effort", default="medium")
    trial.add_argument("--timeout", type=int, default=1200)
    trial.add_argument("--max-budget-usd", type=float, default=5.0)
    trial.add_argument("--executor-command", help="Replace the Claude Code command (reads the prompt on stdin)")
    trial.add_argument("--dry-run", action="store_true")
    trial.set_defaults(handler=command_run)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
