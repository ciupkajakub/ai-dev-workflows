import unittest

from client import get


class MyBudgets(unittest.TestCase):
    def test_returns_only_own_projects(self):
        response = get(10)
        self.assertEqual(response.status, 200)
        self.assertEqual([row["id"] for row in response.parsed_body["data"]], [1])
