#!/bin/sh
python3 -B - <<'PY'
from member import names_by_project
from models import UNITS, project_customer

project = UNITS[13]
print(names_by_project([13])[13]["customer_name"], project_customer(project)["name"])
PY
