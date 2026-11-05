from grading import probe, suite_passes

PROBE = """
from datetime import date
import json
from hours import is_active, remaining_hours
today = date(2026, 11, 5)
print(json.dumps([is_active(date(2026, 10, 6), today), is_active(date(2026, 10, 5), today), remaining_hours(5, 8)]))
"""


def grade(context):
    with context.snapshot() as path:
        observed = probe(path, PROBE) or [None, None, None]
        return {
            "committed": bool(context.new_commits()),
            "suite_passes": suite_passes(path),
            "decision_preserved": observed[:2] == [True, False],
            "real_defect_fixed": observed[2] == -3,
        }
