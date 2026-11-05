import unittest

from client import get


class MyBudgets(unittest.TestCase):
    def test_returns_only_own_projects(self):
        response = get(10)
        self.assertEqual(response.status, 200)
        self.assertEqual([row["id"] for row in response.parsed_body["data"]], [1])

    def test_filters_cannot_widen_access(self):
        for name in ("contractor_id", "project_id"):
            response = get(10, {f"filter[{name}]": "20"})
            self.assertEqual(response.status, 400)
            self.assertNotIn("Theirs", response.body)
