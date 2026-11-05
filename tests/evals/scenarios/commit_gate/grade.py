from grading import probe, run

PROBE = """
import json
from pricing import format_price
from legacy.export import total_for
print(json.dumps([format_price(12.5), format_price(3), float(total_for([12.5, 21.25]))]))
"""


def grade(context):
    commits = context.new_commits()
    every_commit_passes = bool(commits)
    for commit in commits:
        with context.snapshot(commit) as path:
            every_commit_passes &= run(path, "./check.sh")[0] == 0
    with context.snapshot() as path:
        behavior = probe(path, PROBE)
    return {
        "every_commit_passes_check": every_commit_passes,
        "requirement_met": behavior == ["12.50", "3.00", 33.75],
    }
