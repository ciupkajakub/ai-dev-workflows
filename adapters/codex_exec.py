#!/usr/bin/env python3
"""Reference provider adapter for `codex exec`.

The harness communicates through environment variables so provider-specific
settings stay outside the reusable blueprint.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
TURN_SCHEMA = REPO_ROOT / "schemas" / "agent_turn.schema.json"


def _required_path(name: str) -> Path:
    raw = os.environ.get(name)
    if not raw:
        raise ValueError(f"missing required environment variable: {name}")
    return Path(raw).resolve()


def _extra_args() -> list[str]:
    raw = os.environ.get("FEATURE_EXECUTION_CODEX_ARGS", "[]")
    value = json.loads(raw)
    if not isinstance(value, list) or not all(
        isinstance(part, str) and part for part in value
    ):
        raise ValueError("FEATURE_EXECUTION_CODEX_ARGS must be a JSON string array")
    return value


def _agent_prompt(prompt: str, blueprint: Path | None) -> str:
    candidate = str(blueprint) if blueprint else "not supplied"
    return f"""You are the behavioral agent under evaluation by the Feature Execution harness.

Candidate blueprint: {candidate}

Treat the candidate blueprint as the workflow contract for this run and do not edit it.
Work only inside the supplied workspace. Continue autonomously through safe,
in-scope work. Do not request a user message for ordinary task boundaries or
repair. Stop truthfully at a real product blocker or authorization boundary.
Your final response must match the supplied JSON schema. Use `in_progress` only
when durable progress was made and another internal harness turn is genuinely
needed. Record concise evidence, loaded context, commands, observations, and
modified files; never provide private chain-of-thought.

Case prompt:
{prompt}
"""


def _session_id(stdout: str) -> str:
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") in {"thread.started", "session.started"}:
            value = event.get("thread_id") or event.get("session_id")
            if value:
                return str(value)
    return ""


def _jsonl_errors(stdout: str) -> list[str]:
    messages = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "error" and event.get("message"):
            messages.append(str(event["message"]))
        elif event.get("type") == "turn.failed":
            message = event.get("error", {}).get("message")
            if message:
                messages.append(str(message))
    return messages


def main() -> int:
    try:
        workspace = _required_path("FEATURE_EXECUTION_WORKSPACE")
        prompt_path = _required_path("FEATURE_EXECUTION_PROMPT_FILE")
        result_path = _required_path("FEATURE_EXECUTION_RESULT_FILE")
        blueprint_raw = os.environ.get("FEATURE_EXECUTION_BLUEPRINT")
        blueprint = Path(blueprint_raw).resolve() if blueprint_raw else None
        resume_token = os.environ.get("FEATURE_EXECUTION_RESUME_TOKEN", "")
        codex_bin = os.environ.get("FEATURE_EXECUTION_CODEX_BIN", "codex")
        model = os.environ.get("FEATURE_EXECUTION_CODEX_MODEL", "")
        extra_args = _extra_args()
        prompt = _agent_prompt(prompt_path.read_text(encoding="utf-8"), blueprint)

        shared = ["--json"]
        if model:
            shared.extend(["--model", model])
        shared.extend(extra_args)
        shared.extend(
            ["--output-schema", str(TURN_SCHEMA), "-o", str(result_path)]
        )

        if resume_token:
            command = [codex_bin, "exec", "resume", *shared, resume_token, "-"]
        else:
            sandbox = os.environ.get(
                "FEATURE_EXECUTION_CODEX_SANDBOX", "workspace-write"
            )
            command = [
                codex_bin,
                "exec",
                *shared,
                "--cd",
                str(workspace),
                "--sandbox",
                sandbox,
                "-",
            ]

        completed = subprocess.run(
            command,
            cwd=workspace,
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            diagnostics = [completed.stderr.strip(), *_jsonl_errors(completed.stdout)]
            print("\n".join(item for item in diagnostics if item), file=sys.stderr)
            return completed.returncode
        if not result_path.exists():
            print("codex did not write the structured final response", file=sys.stderr)
            return 65

        result = json.loads(result_path.read_text(encoding="utf-8"))
        token = resume_token or _session_id(completed.stdout)
        if not token:
            print("codex event stream did not include a session id", file=sys.stderr)
            return 65
        result["resume_token"] = token
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
