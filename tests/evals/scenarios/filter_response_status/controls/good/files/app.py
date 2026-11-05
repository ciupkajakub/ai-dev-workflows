"""My budgets endpoint."""

import json
from urllib.parse import parse_qsl

PROJECTS = [
    {"id": 1, "name": "Mine", "contractor_id": 10},
    {"id": 2, "name": "Theirs", "contractor_id": 20},
]
FILTERABLE = {"id": "id"}


class UnsupportedFilter(Exception):
    pass


def my_budgets(user_id, filters):
    rows = [project for project in PROJECTS if project["contractor_id"] == user_id]
    for name, value in filters.items():
        if name not in FILTERABLE:
            raise UnsupportedFilter(name)
        field = FILTERABLE[name]
        rows = [row for row in rows if str(row[field]) == value]
    return rows


def application(environ, start_response):
    try:
        user_id = int(environ["HTTP_X_USER_ID"])
        filters = {
            key[7:-1]: value
            for key, value in parse_qsl(environ.get("QUERY_STRING", ""))
            if key.startswith("filter[")
        }
        body = json.dumps({"data": my_budgets(user_id, filters)}).encode()
        start_response("200 OK", [("Content-Type", "application/json")])
    except UnsupportedFilter:
        body = json.dumps({"error": "unsupported filter"}).encode()
        start_response("400 Bad Request", [("Content-Type", "application/json")])
    except Exception:
        body = b"Internal Server Error"
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
    return [body]
