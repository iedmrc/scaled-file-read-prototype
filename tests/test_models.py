import unittest
from src.models import Record


class TestRecord(unittest.TestCase):
    def test_comparison(self):
        r1 = Record(10, "http://example.com")
        r2 = Record(20, "http://example.org")
        self.assertTrue(r1 < r2)
        self.assertTrue(r1 <= r2)
        self.assertTrue(r2 > r1)
        self.assertTrue(r2 >= r1)
        self.assertTrue(r1 != r2)
