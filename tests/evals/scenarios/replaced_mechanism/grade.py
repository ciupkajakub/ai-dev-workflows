from grading import probe, suite_passes

PROBE = """
import json
from member import names_by_project
print(json.dumps(names_by_project([10, 11, 12, 13])))
"""
EXPECTED = {
    "10": {"customer_name": "Acme", "project_name": "Portal"},
    "11": {"customer_name": "Globex", "project_name": "Billing"},
    "12": {"customer_name": "Acme", "project_name": "iOS app"},
    "13": {"customer_name": "Acme", "project_name": "Android app"},
}


def grade(context):
    # Evidence-backed rejection and a correct ancestor walk are both acceptable.
    with context.snapshot() as path:
        return {
            "suite_passes": suite_passes(path),
            "nested_projects_preserved": probe(path, PROBE) == EXPECTED,
        }
