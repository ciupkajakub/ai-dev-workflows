from models import UNITS


def leader_rows():
    return [
        {"customer": UNITS[unit["path"][1]]["name"], "project": unit["name"]}
        for unit in UNITS.values() if unit["type"] == "Project"
    ]
