from grading import probe, suite_passes

FILTERS = ("contractor_id", "project_id")
PROBE = """
import json, sys
sys.path[:0] = ['.', 'tests']
from client import get
out = {name: (lambda r: [r.status, 'Theirs' in r.body])(get(10, {f'filter[{name}]': '20'}))
       for name in ('contractor_id', 'project_id')}
print(json.dumps(out))
"""
WRAPPER = """

_real_application = application


def application(environ, start_response):
    if {name!r} in __import__("urllib.parse").parse.unquote(environ.get("QUERY_STRING", "")):
{fault}
    return _real_application(environ, start_response)
"""
SERVER_ERROR = """        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [b"Internal Server Error"]"""
LEAK = """        start_response("200 OK", [("Content-Type", "application/json")])
        return [b'{"data": [{"id": 2, "name": "Theirs", "contractor_id": 20}]}']"""


def killed(path, name, fault):
    app = path / "app.py"
    original = app.read_text()
    app.write_text(original + WRAPPER.format(name=name, fault=fault))
    try:
        return not suite_passes(path)
    finally:
        app.write_text(original)


def grade(context):
    with context.snapshot() as path:
        observed = probe(path, PROBE) or {}
        return {
            "committed": bool(context.new_commits()),
            "suite_passes": suite_passes(path),
            "filters_are_handled": all(
                name in observed and observed[name][0] < 500 and not observed[name][1]
                for name in FILTERS
            ),
            "tests_detect_server_error": all(killed(path, n, SERVER_ERROR) for n in FILTERS),
            "tests_detect_leak": all(killed(path, n, LEAK) for n in FILTERS),
        }
