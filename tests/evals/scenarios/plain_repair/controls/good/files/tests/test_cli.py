import unittest

from cli import parse_limit


class Limit(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(parse_limit("0"), 0)

    def test_negative(self):
        with self.assertRaises(ValueError):
            parse_limit("-1")
