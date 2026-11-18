import json
import os
from pathlib import Path

UNITS = {
    unit["id"]: unit
    for unit in json.loads((Path(__file__).parent / "data" / "work_units.json").read_text())
}


def observe_lookup(source, project_id, customer):
    log = os.environ.get("WORKFLOW_EVAL_OBSERVATIONS")
    if log:
        with open(log, "a") as output:
            print(source, project_id, customer["name"], sep="\t", file=output)


def project_customer(project):
    """A project's customer is its parent."""
    customer = UNITS[project["parent_id"]]
    observe_lookup("proposed", project["id"], customer)
    return customer
