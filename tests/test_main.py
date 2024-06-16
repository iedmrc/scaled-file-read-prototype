import unittest
from unittest.mock import mock_open, patch

from src.helpers import FileReadError
from src.models import Record
from src.file_processors import FileProcessor, ParallelFileProcessor
from src.main import FileProcessorService

from tests.helpers import parameterized_test


class TestFileProcessorService(unittest.TestCase):

    @parameterized_test(
        ("", 2, 0, []),  # Empty file
        ("http://example.com 10\n", 2, 0, [Record(10, "http://example.com")]),  # Single record
        ("http://example.com 10\nhttp://example.org 20\n", 2, 0,
         [Record(20, "http://example.org"), Record(10, "http://example.com")]),  # Exactly top records
        # Fewer than top records
        ("http://example.com 10\n", 2, 0, [Record(10, "http://example.com")]),
        ("http://example.com -10\nhttp://example.org -20\n", 2, 0,
         [Record(-10, "http://example.com"), Record(-20, "http://example.org")]),  # Negative values
        ("http://example.com 1000000000\nhttp://example.org 2000000000\n", 2, 0,
         [Record(2000000000, "http://example.org"), Record(1000000000, "http://example.com")]),  # Large values
        ("http://example.com 10\nhttp://example.org twenty\n", 2, 0, FileReadError),  # Non-integer values
        ("http://example.com 10\nhttp://example.org 20\n" * 1000, 2, 0,
         [Record(20, "http://example.org"), Record(20, "http://example.org")]),  # Very large number of records
        ("http://example.com 10\nhttp://example.org 20\nhttp://example.net 30\n", 3, 0,
         [Record(30, "http://example.net"), Record(20, "http://example.org"), Record(10, "http://example.com")]),  # Three records
        ("http://example.com 10\nhttp://example.org 20\nhttp://example.net 30\nhttp://example.info 40\n", 3, 0,
         [Record(40, "http://example.info"), Record(30, "http://example.net"), Record(20, "http://example.org")]),  # Four records
        ("http://example.com 10\nhttp://example.org 10\nhttp://example.net 10\nhttp://example.info 10\nhttp://example.edu 10\n", 3,
         0, [Record(10, "http://example.com"), Record(10, "http://example.org"), Record(10, "http://example.net")]),  # Same values -- The behavior is strange here (compared to tuples)
        ("http://example.com 10\nhttp://example.org 10\nhttp://example.net 20\nhttp://example.info 20\nhttp://example.edu 30\nhttp://example.gov 30\n", 4, 0,
         [Record(value=30, url='http://example.gov'), Record(value=30, url='http://example.edu'), Record(value=20, url='http://example.net'), Record(value=20, url='http://example.info')]),  # Mixed values -- The behavior is strange here as well
    )
    @patch('src.file_processors.ProcessorFactory.create_processor')
    def test_process_file_single_thread(self, mock_file_content, top, chunk_size, expected, mock_create_processor):
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            mock_processor = FileProcessor(mock_open(read_data=mock_file_content)())
            mock_create_processor.return_value = mock_processor

            service = FileProcessorService('dummy', top=top, chunk_size=chunk_size)
            if isinstance(expected, type) and issubclass(expected, Exception):
                with self.assertRaises(expected):
                    service.process_file()
            else:
                top_records = service.process_file()
                self.assertEqual(len(top_records), len(expected))
                for record, expected_record in zip(top_records, expected):
                    self.assertEqual(record.url, expected_record.url)
                    self.assertEqual(record.value, expected_record.value)

    @parameterized_test(
        ("", 2, 2, []),  # Empty file
        ("http://example.com 10\n", 2, 2, [Record(10, "http://example.com")]),  # Single record
        ("http://example.com 10\nhttp://example.org 20\n", 2, 2,
         [Record(20, "http://example.org"), Record(10, "http://example.com")]),  # Exactly top records
        # Fewer than top records
        ("http://example.com 10\n", 2, 2, [Record(10, "http://example.com")]),
        ("http://example.com -10\nhttp://example.org -20\n", 2, 2,
         [Record(-10, "http://example.com"), Record(-20, "http://example.org")]),  # Negative values
        ("http://example.com 1000000000\nhttp://example.org 2000000000\n", 2, 2,
         [Record(2000000000, "http://example.org"), Record(1000000000, "http://example.com")]),  # Large values
        ("http://example.com 10\nhttp://example.org twenty\n", 2, 2, FileReadError),  # Non-integer values
        ("http://example.com 10\nhttp://example.org 20\n" * 100, 2, 6,
         [Record(20, "http://example.org"), Record(20, "http://example.org")]),  # Large number of records
        ("http://example.com 10\nhttp://example.org 20\nhttp://example.net 30\n", 3, 2,
         [Record(30, "http://example.net"), Record(20, "http://example.org"), Record(10, "http://example.com")]),  # Three records
        ("http://example.com 10\nhttp://example.org 20\nhttp://example.net 30\nhttp://example.info 40\n", 3, 2,
         [Record(40, "http://example.info"), Record(30, "http://example.net"), Record(20, "http://example.org")]),  # Four records
    )
    @patch('src.file_processors.ProcessorFactory.create_processor')
    def test_process_file_parallel(self, mock_file_content, top, chunk_size, expected, mock_create_processor):
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            mock_processor = ParallelFileProcessor(
                mock_open(read_data=mock_file_content)(), chunk_size=chunk_size)
            mock_create_processor.return_value = mock_processor

            service = FileProcessorService('dummy', top=top, chunk_size=chunk_size)
            if isinstance(expected, type) and issubclass(expected, Exception):
                with self.assertRaises(expected):
                    service.process_file()
            else:
                top_records = service.process_file()
                self.assertEqual(len(top_records), len(expected))
                for record, expected_record in zip(top_records, expected):
                    self.assertEqual(record.url, expected_record.url)
                    self.assertEqual(record.value, expected_record.value)
