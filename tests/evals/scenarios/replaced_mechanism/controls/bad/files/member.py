from models import UNITS, project_customer


def names_by_project(project_ids):
    names = {}
    for project_id in project_ids:
        project = UNITS[project_id]
        names[project_id] = {
            "customer_name": project_customer(project)["name"],
            "project_name": project["name"],
        }
    return names
