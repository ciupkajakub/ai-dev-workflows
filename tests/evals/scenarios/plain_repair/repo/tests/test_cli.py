import unittest

from cli import parse_limit


class Limit(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(parse_limit("0"), 0)
