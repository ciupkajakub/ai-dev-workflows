#!/bin/sh
set -eu

repo_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
export PYTHONDONTWRITEBYTECODE=1
python3 -B - "$repo_root" <<'PY'
import hashlib
import json
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
blueprint = root / "feature_execution_blueprint.md"
text = blueprint.read_text()
# Public section numbers and generated provenance are executable interfaces.
outside_fences = []
fence_size = 0
for line in text.splitlines():
    fence = re.match(r"^(`{3,})", line)
    if fence:
        size = len(fence[1])
        if not fence_size:
            fence_size = size
        elif size >= fence_size:
            fence_size = 0
    elif not fence_size:
        outside_fences.append(line)
assert not fence_size, "unclosed blueprint code fence"
sections = re.findall(r"^## (\d+)\. ", "\n".join(outside_fences), re.MULTILINE)
for number in range(1, 15):
    assert sections.count(str(number)) == 1, f"ambiguous public section {number}"
revision = re.search(r"^Blueprint revision: `([^`]+)`", text, re.MULTILINE)[1]
schema = re.search(r"^Workflow schema: `([^`]+)`", text, re.MULTILINE)[1]
digest = hashlib.sha256(blueprint.read_bytes()).hexdigest()
example = root / "example/ai-workflow"
current = [example / "AGENTS.md"] + [
    example / "work/B001-example-feature" / name
    for name in ("FEATURE.md", "IMPLEMENTATION.md", "PROGRESS_STATE.md")
]
for path in current:
    content = path.read_text()
    assert f"Blueprint revision: `{revision}`" in content, path
    assert f"Workflow schema: `{schema}`" in content, path
    assert digest in content, f"stale blueprint digest: {path}"
# Progress is historical: only its appended migration references current bytes.
assert digest in (example / "work/B001-example-feature/PROGRESS.md").read_text()
for name in ("schemas/agent_turn.schema.json", "eval/cases/v1/catalog.json"):
    json.loads((root / name).read_text())
print("Public section interface, current provenance, and JSON formats pass")
PY
"$repo_root/bin/feature-execution" doctor "$repo_root/example/ai-workflow" \
  --blueprint "$repo_root/feature_execution_blueprint.md" --batch B001 >/dev/null
