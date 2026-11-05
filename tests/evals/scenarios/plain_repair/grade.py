from grading import probe, suite_passes

PROBE = """
import json
from cli import parse_limit
try:
    parse_limit("-1")
    rejected = False
except ValueError:
    rejected = True
print(json.dumps([rejected, parse_limit("0"), parse_limit("5")]))
"""


def grade(context):
    outside = [name for name in context.changed_files()
               if name != "cli.py" and not name.startswith(("tests/", "ai-workflow/"))]
    with context.snapshot() as path:
        return {
            "committed": bool(context.new_commits()),
            "suite_passes": suite_passes(path),
            "defect_fixed": probe(path, PROBE) == [True, 0, 5],
            "stayed_in_scope": not outside,
        }
