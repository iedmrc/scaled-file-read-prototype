import unittest
from unittest.mock import mock_open, patch
from io import StringIO

from src.file_processors import FileProcessor, ParallelFileProcessor
from src.main import FileProcessorService


class FileLikeStringIO(StringIO):
    def __init__(self, initial_value="", name="dummy"):
        super().__init__(initial_value)
        self.name = name


class TestFileProcessorService(unittest.TestCase):
    @patch('src.file_processors.ProcessorFactory.create_processor')
    @patch('builtins.open', new_callable=mock_open, read_data="http://example.com 10\nhttp://example.org 20\n")
    def test_process_file_single_thread(self, mock_file, mock_create_processor):
        mock_processor = FileProcessor(mock_file())
        mock_create_processor.return_value = mock_processor
        service = FileProcessorService('dummy', top=2, chunk_size=0)
        top_records = service.process_file()
        self.assertEqual(len(top_records), 2)
        self.assertEqual(top_records[0].url, "http://example.org")
        self.assertEqual(top_records[0].value, 20)
        self.assertEqual(top_records[1].url, "http://example.com")
        self.assertEqual(top_records[1].value, 10)

    @patch('src.file_processors.ProcessorFactory.create_processor')
    @patch('builtins.open', new_callable=mock_open, read_data="http://example.com 10\nhttp://example.org 20\nhttp://example.net 30\n")
    def test_process_file_parallel(self, mock_file, mock_create_processor):
        mock_processor = ParallelFileProcessor(mock_file(), chunk_size=2)
        mock_create_processor.return_value = mock_processor
        service = FileProcessorService('dummy', top=2, chunk_size=2)
        top_records = service.process_file()
        self.assertEqual(len(top_records), 2)
        self.assertEqual(top_records[0].url, "http://example.net")
        self.assertEqual(top_records[0].value, 30)
        self.assertEqual(top_records[1].url, "http://example.org")
        self.assertEqual(top_records[1].value, 20)
