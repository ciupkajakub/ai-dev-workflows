from datetime import date
import unittest

from hours import is_active, remaining_hours


class Hours(unittest.TestCase):
    def test_active_recently(self):
        self.assertTrue(is_active(date(2026, 11, 1), date(2026, 11, 5)))

    def test_remaining(self):
        self.assertEqual(remaining_hours(10, 4), 6)
