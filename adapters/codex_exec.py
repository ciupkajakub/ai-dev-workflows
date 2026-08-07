#!/usr/bin/env python3
"""Reference provider adapter for `codex exec`.

The harness communicates through environment variables so provider-specific
settings stay outside the reusable blueprint.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
TURN_SCHEMA = REPO_ROOT / "schemas" / "agent_turn.schema.json"
ADAPTER_VERSION = "codex-exec-v1"


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
    reserved = {
        "--ask-for-approval",
        "--cd",
        "--config",
        "--dangerously-bypass-approvals-and-sandbox",
        "--full-auto",
        "--json",
        "--model",
        "--output-schema",
        "--sandbox",
        "--yolo",
        "-C",
        "-a",
        "-c",
        "-m",
        "-o",
        "-s",
    }
    if any(
        part in reserved
        or part.startswith("--cd=")
        or part.startswith("--config=")
        or part.startswith("--model=")
        or part.startswith("--output-schema=")
        or part.startswith("--sandbox=")
        for part in value
    ):
        raise ValueError(
            "FEATURE_EXECUTION_CODEX_ARGS contains a reserved provider setting"
        )
    return value


def _codex_binary() -> tuple[str, dict]:
    """Resolve Codex and mark overrides as non-behavioral test providers."""
    override = os.environ.get("FEATURE_EXECUTION_CODEX_BIN")
    requested = override or "codex"
    resolved_raw = shutil.which(requested)
    if not resolved_raw:
        raise ValueError(f"Codex executable not found: {requested}")
    resolved = Path(resolved_raw).resolve()
    executable_digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
    expected_digest = os.environ.get("FEATURE_EXECUTION_CODEX_EXPECTED_SHA256", "")
    version = "unknown"
    verified = False
    if override is None:
        completed = subprocess.run(
            [str(resolved), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        version = completed.stdout.strip()
        verified = (
            completed.returncode == 0
            and bool(re.fullmatch(r"codex-cli\s+\d+\.\d+\.\d+[^\s]*", version))
            and bool(re.fullmatch(r"[0-9a-f]{64}", expected_digest))
            and executable_digest == expected_digest
        )
    return str(resolved), {
        "codex_binary_verified": verified,
        "codex_executable": str(resolved),
        "codex_executable_sha256": executable_digest,
        "codex_expected_sha256": expected_digest or "unknown",
        "codex_version": version,
        "codex_binary_override": override is not None,
    }


def _agent_prompt(prompt: str, blueprint: Path | None) -> str:
    candidate = str(blueprint) if blueprint else "not supplied"
    return f"""You are the behavioral agent under evaluation by the Feature Execution harness.

Candidate blueprint: {candidate}

Treat the candidate blueprint as the workflow contract for this run and do not edit it.
Work only inside the supplied workspace. Your final response must match the
supplied JSON schema. Record concise evidence, loaded context, observations,
and modified files; never provide private chain-of-thought.

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


def _jsonl_commands(stdout: str) -> list[dict]:
    commands = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if event.get("type") != "item.completed" or item.get("type") not in {
            "command_execution",
            "command",
        }:
            continue
        commands.append(
            {
                "command": str(item.get("command", "")),
                "exit_code": item.get("exit_code"),
                "result": str(
                    item.get("aggregated_output")
                    or item.get("output")
                    or item.get("status", "")
                )[:500],
            }
        )
    return commands


def main() -> int:
    try:
        workspace = _required_path("FEATURE_EXECUTION_WORKSPACE")
        prompt_path = _required_path("FEATURE_EXECUTION_PROMPT_FILE")
        result_path = _required_path("FEATURE_EXECUTION_RESULT_FILE")
        blueprint_raw = os.environ.get("FEATURE_EXECUTION_BLUEPRINT")
        blueprint = Path(blueprint_raw).resolve() if blueprint_raw else None
        resume_token = os.environ.get("FEATURE_EXECUTION_RESUME_TOKEN", "")
        codex_bin, codex_provenance = _codex_binary()
        model = os.environ.get("FEATURE_EXECUTION_CODEX_MODEL", "")
        effort = os.environ.get("FEATURE_EXECUTION_CODEX_EFFORT", "")
        tools_label = os.environ.get("FEATURE_EXECUTION_CODEX_TOOLS_LABEL", "")
        extra_args = _extra_args()
        extra_args_sha256 = hashlib.sha256(
            json.dumps(extra_args, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        sandbox = os.environ.get("FEATURE_EXECUTION_CODEX_SANDBOX", "workspace-write")
        prompt = _agent_prompt(prompt_path.read_text(encoding="utf-8"), blueprint)

        shared = ["--json"]
        if model:
            shared.extend(["--model", model])
        if effort:
            shared.extend(["--config", f'model_reasoning_effort="{effort}"'])
        shared.extend(extra_args)
        shared.extend(
            ["--output-schema", str(TURN_SCHEMA), "-o", str(result_path)]
        )

        if resume_token:
            command = [codex_bin, "exec", "resume", *shared, resume_token, "-"]
        else:
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
        result["commands_run"] = _jsonl_commands(completed.stdout)
        result["adapter_metadata"] = {
            "adapter": ADAPTER_VERSION,
            "behavioral_agent": codex_provenance["codex_binary_verified"],
            "command_evidence_source": "codex_jsonl_events",
            "model": model or "unknown",
            "effort": effort or "unknown",
            "tools": tools_label or "unknown",
            "sandbox": sandbox,
            "codex_args_sha256": extra_args_sha256,
            **codex_provenance,
        }
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
