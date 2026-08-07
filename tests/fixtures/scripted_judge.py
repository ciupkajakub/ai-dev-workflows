#!/usr/bin/env python3
import json
import os
from pathlib import Path
import struct
import zlib


workspace = Path(os.environ["FEATURE_EXECUTION_WORKSPACE"])
evidence = workspace / "ui-evidence.png"


def png_chunk(kind, payload):
    checksum = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)


header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
pixels = zlib.compress(b"\x00\xff\xff\xff\xff")
evidence.write_bytes(
    b"\x89PNG\r\n\x1a\n"
    + png_chunk(b"IHDR", header)
    + png_chunk(b"IDAT", pixels)
    + png_chunk(b"IEND", b"")
)

result = {
    "summary": "independent fixture judgment",
    "judge_model": os.environ["FEATURE_EXECUTION_JUDGE_MODEL"],
    "calibration_sha256": os.environ[
        "FEATURE_EXECUTION_JUDGE_CALIBRATION_SHA256"
    ],
    "rubric_scores": {
        "hierarchy": 9,
        "clarity": 9,
        "states": 9,
        "accessibility": 9,
        "responsive": 9,
    },
    "evidence_refs": [str(evidence)],
}
Path(os.environ["FEATURE_EXECUTION_JUDGE_RESULT_FILE"]).write_text(
    json.dumps(result), encoding="utf-8"
)
