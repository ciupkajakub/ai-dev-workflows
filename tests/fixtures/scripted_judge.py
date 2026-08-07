#!/usr/bin/env python3
import json
import os
from pathlib import Path


result = {
    "summary": "independent fixture judgment",
    "rubric_scores": {
        "hierarchy": 9,
        "clarity": 9,
        "states": 9,
        "accessibility": 9,
        "responsive": 9,
    },
    "evidence_refs": [],
}
Path(os.environ["FEATURE_EXECUTION_JUDGE_RESULT_FILE"]).write_text(
    json.dumps(result), encoding="utf-8"
)
