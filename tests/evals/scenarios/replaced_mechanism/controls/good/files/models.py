import json
from pathlib import Path

UNITS = {
    unit["id"]: unit
    for unit in json.loads((Path(__file__).parent / "data" / "work_units.json").read_text())
}


def project_customer(project):
    """A project's customer is its nearest Customer ancestor."""
    unit = UNITS[project["parent_id"]]
    while unit["type"] != "Customer":
        unit = UNITS[unit["parent_id"]]
    return unit
