import unittest

from member import names_by_project


class Names(unittest.TestCase):
    def test_names(self):
        self.assertEqual(
            names_by_project([10, 11]),
            {
                10: {"customer_name": "Acme", "project_name": "Portal"},
                11: {"customer_name": "Globex", "project_name": "Billing"},
            },
        )
