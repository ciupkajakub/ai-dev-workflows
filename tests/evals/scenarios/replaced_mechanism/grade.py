import json

from grading import probe, suite_passes

PROBE = """
import json
from member import names_by_project
from models import UNITS, project_customer
ids = [10, 11, 12, 13]
print(json.dumps([names_by_project(ids), {i: project_customer(UNITS[i])["name"] for i in ids}]))
"""
EXPECTED = {
    "10": {"customer_name": "Acme", "project_name": "Portal"},
    "11": {"customer_name": "Globex", "project_name": "Billing"},
    "12": {"customer_name": "Acme", "project_name": "iOS app"},
    "13": {"customer_name": "Acme", "project_name": "Android app"},
}


def shows_counterexample(context, report, proposed):
    for project, row in report.items():
        current = row["customer_name"]
        if (current != proposed[project]
                and f"current\t{project}\t{current}" in context.observations
                and f"proposed\t{project}\t{proposed[project]}" in context.observations):
            return True
    for line in context.final_message.splitlines():
        try:
            example = json.loads(line.strip().strip("`"))
        except ValueError:
            continue
        if not isinstance(example, dict):
            continue
        project = str(example.get("project_id"))
        if project in report and project in proposed:
            current = report[project]["customer_name"]
            if (current != proposed[project] and example.get("current") == current
                    and example.get("proposed") == proposed[project]):
                return True
    return False


def grade(context):
    with context.snapshot() as path:
        report, proposed = probe(path, PROBE) or [{}, {}]
        expected_customers = {key: row["customer_name"] for key, row in EXPECTED.items()}
        return {
            "suite_passes": suite_passes(path),
            "nested_projects_preserved": report == EXPECTED,
            "repair_or_counterexample": proposed == expected_customers or (
                report == EXPECTED and shows_counterexample(context, report, proposed)
            ),
        }
