import unittest
from unittest.mock import mock_open, patch

from src.models import Record
from src.helpers import FileReadError
from src.file_processors import FileProcessor, ChunkFileProcessor, ParallelFileProcessor, ProcessorFactory


class TestFileProcessor(unittest.TestCase):
    def test_read_records(self):
        mock_file_content = "http://example.com 10\nhttp://example.org 20\n"
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with open('dummy', 'r') as f:
                processor = FileProcessor(f)
                records = list(processor.read_records())
                self.assertEqual(len(records), 2)
                self.assertEqual(records[0].url, "http://example.com")
                self.assertEqual(records[0].value, 10)
                self.assertEqual(records[1].url, "http://example.org")
                self.assertEqual(records[1].value, 20)

    def test_read_records_error(self):
        mock_file_content = "http://example.com\nhttp://example.org 20\n"
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with open('dummy', 'r') as f:
                processor = FileProcessor(f)
                with self.assertRaises(FileReadError):
                    list(processor.read_records())


class TestChunkFileProcessor(unittest.TestCase):
    def test_read_records(self):
        mock_file_content = "http://example.com 10\nhttp://example.org 20\nhttp://example.net 30\n"
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with open('dummy', 'r') as f:
                processor = ChunkFileProcessor(f, start_line=1, chunk_size=2)
                records = list(processor.read_records())
                self.assertEqual(len(records), 2)
                self.assertEqual(records[0].url, "http://example.org")
                self.assertEqual(records[0].value, 20)
                self.assertEqual(records[1].url, "http://example.net")
                self.assertEqual(records[1].value, 30)

    def test_read_records_partial_chunk(self):
        mock_file_content = "http://example.com 10\nhttp://example.org 20\n"
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with open('dummy', 'r') as f:
                processor = ChunkFileProcessor(f, start_line=1, chunk_size=2)
                records = list(processor.read_records())
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0].url, "http://example.org")
                self.assertEqual(records[0].value, 20)


class TestParallelFileProcessor(unittest.TestCase):
    def test_read_records(self):
        mock_file_content = "http://example.com 10\nhttp://example.org 20\nhttp://example.net 30\n"
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with open('dummy', 'r') as f:
                processor = ParallelFileProcessor(f, chunk_size=2)
                records = list(processor.read_records())
                self.assertEqual(len(records), 3)
                self.assertIn(Record(10, "http://example.com"), records)
                self.assertIn(Record(20, "http://example.org"), records)
                self.assertIn(Record(30, "http://example.net"), records)


class TestProcessorFactory(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data="http://example.com 10\nhttp://example.org 20\n")
    def test_create_processor_single_thread(self, mock_file):
        processor = ProcessorFactory.create_processor('dummy', chunk_size=0)
        self.assertIsInstance(processor, FileProcessor)

    @patch('builtins.open', new_callable=mock_open, read_data="http://example.com 10\nhttp://example.org 20\n")
    def test_create_processor_parallel(self, mock_file):
        processor = ProcessorFactory.create_processor('dummy', chunk_size=2)
        self.assertIsInstance(processor, ParallelFileProcessor)
