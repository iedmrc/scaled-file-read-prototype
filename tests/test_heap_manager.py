import unittest

from src.models import Record
from src.heap_manager import HeapManager


class TestHeapManager(unittest.TestCase):
    def test_heap_maintainer(self):
        heap = HeapManager(2)
        heap.add_record(Record(10, "http://example.com"))
        heap.add_record(Record(20, "http://example.org"))
        heap.add_record(Record(30, "http://example.net"))
        top_records = heap.get_top_records()
        self.assertEqual(len(top_records), 2)
        self.assertEqual(top_records[0].value, 30)
        self.assertEqual(top_records[1].value, 20)
    
    def test_heap_maintainer_less_records(self):
        heap = HeapManager(5)
        heap.add_record(Record(10, "http://example.com"))
        heap.add_record(Record(20, "http://example.org"))
        top_records = heap.get_top_records()
        self.assertEqual(len(top_records), 2)
        self.assertEqual(top_records[0].value, 20)
        self.assertEqual(top_records[1].value, 10)

