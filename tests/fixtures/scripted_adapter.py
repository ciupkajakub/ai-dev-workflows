#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys


plan_path = Path(os.environ["SCRIPTED_ADAPTER_PLAN"])
result_path = Path(os.environ["FEATURE_EXECUTION_RESULT_FILE"])
case_id = os.environ.get("FEATURE_EXECUTION_CASE_ID", "default")
turn_index = int(os.environ.get("FEATURE_EXECUTION_TURN_INDEX", "1")) - 1

required_capabilities = set(
    json.loads(os.environ.get("FEATURE_EXECUTION_REQUIRED_CAPABILITIES", "[]"))
)
available_capabilities = set(
    json.loads(
        os.environ.get(
            "SCRIPTED_ADAPTER_CAPABILITIES",
            json.dumps(sorted(required_capabilities)),
        )
    )
)
missing_capabilities = sorted(required_capabilities - available_capabilities)
if missing_capabilities:
    print(
        "capability preflight failed; scripted profile lacks: "
        + ", ".join(missing_capabilities),
        file=sys.stderr,
    )
    raise SystemExit(76)

log_path = os.environ.get("SCRIPTED_ADAPTER_LOG")
if log_path:
    with Path(log_path).open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "turn_index": turn_index + 1,
                    "resume_token": os.environ.get(
                        "FEATURE_EXECUTION_RESUME_TOKEN", ""
                    ),
                    "prompt": Path(
                        os.environ["FEATURE_EXECUTION_PROMPT_FILE"]
                    ).read_text(encoding="utf-8"),
                }
            )
            + "\n"
        )

plan = json.loads(plan_path.read_text(encoding="utf-8"))
turns = plan.get(case_id, plan.get("default", []))
if not turns:
    raise SystemExit(f"no scripted turns for {case_id}")

turn = dict(turns[min(turn_index, len(turns) - 1)])
if turn.pop("resume_unavailable", False) and os.environ.get(
    "FEATURE_EXECUTION_RESUME_TOKEN"
):
    raise SystemExit(75)
for relative, content in turn.pop("write_files", {}).items():
    target = Path(os.environ["FEATURE_EXECUTION_WORKSPACE"]) / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.chmod(0o644)
    target.write_text(content, encoding="utf-8")
turn.setdefault("evidence_refs", [])
turn.setdefault("requested_user_instruction", False)
turn.setdefault("context_loaded", [])
turn.setdefault("rubric_scores", {})
turn.setdefault("resume_token", f"scripted-{case_id}")
result_path.write_text(json.dumps(turn), encoding="utf-8")
