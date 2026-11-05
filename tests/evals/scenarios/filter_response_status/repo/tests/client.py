"""Minimal test client for the WSGI application."""

import json
from urllib.parse import urlencode

from app import application


class Response:
    def __init__(self, status, content_type, body):
        self.status, self.content_type, self.body = status, content_type, body

    @property
    def parsed_body(self):
        if self.content_type == "application/json":
            return json.loads(self.body)
        return self.body


def get(user_id, params=None):
    captured = {}

    def start_response(status, headers):
        captured.update(status=int(status.split()[0]), headers=dict(headers))

    environ = {"HTTP_X_USER_ID": str(user_id), "QUERY_STRING": urlencode(params or {})}
    body = b"".join(application(environ, start_response)).decode()
    return Response(captured["status"], captured["headers"]["Content-Type"], body)
