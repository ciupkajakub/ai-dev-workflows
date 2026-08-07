#!/usr/bin/env python3
import json
import os
from pathlib import Path


plan_path = Path(os.environ["SCRIPTED_ADAPTER_PLAN"])
result_path = Path(os.environ["FEATURE_EXECUTION_RESULT_FILE"])
case_id = os.environ.get("FEATURE_EXECUTION_CASE_ID", "default")
turn_index = int(os.environ.get("FEATURE_EXECUTION_TURN_INDEX", "1")) - 1

plan = json.loads(plan_path.read_text(encoding="utf-8"))
turns = plan.get(case_id, plan.get("default", []))
if not turns:
    raise SystemExit(f"no scripted turns for {case_id}")

turn = dict(turns[min(turn_index, len(turns) - 1)])
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
