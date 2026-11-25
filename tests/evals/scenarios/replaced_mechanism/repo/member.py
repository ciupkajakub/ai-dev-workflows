from models import UNITS, observe_lookup


def names_by_project(project_ids):
    names = {}
    for project_id in project_ids:
        project = UNITS[project_id]
        customer = UNITS[project["path"][1]]
        observe_lookup("current", project_id, customer)
        names[project_id] = {"customer_name": customer["name"], "project_name": project["name"]}
    return names
