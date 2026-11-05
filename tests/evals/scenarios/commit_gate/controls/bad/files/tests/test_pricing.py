import unittest

from pricing import format_price


class Price(unittest.TestCase):
    def test_two_decimals(self):
        self.assertEqual(format_price(12.5), "12.50")
