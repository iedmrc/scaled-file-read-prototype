from abc import ABC, abstractmethod
from typing import Generator, IO

from models import Record
from helpers import Logger, FileReadError

logger = Logger().get_logger()


class AbstractFileProcessor(ABC):
    """Abstract base class for file processors."""

    def __init__(self, file: IO):
        self.file = file

    @abstractmethod
    def read_records(self) -> Generator[Record, None, None]:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()


class FileProcessor(AbstractFileProcessor):
    """Processor for reading entire files."""

    def read_records(self) -> Generator[Record, None, None]:
        """Read records from the file and yield them."""
        for line in self.file:
            try:
                url, value = line.rsplit(maxsplit=1)
                yield Record(int(value), url)
            except ValueError as e:
                logger.error(f"Error processing line: {line}")
                raise FileReadError(f"Error processing line: {line}") from e


class ProcessorFactory:
    """Factory class to create different processors."""

    @staticmethod
    def create_processor(file_path: str) -> AbstractFileProcessor:
        """Create a file processor for the given file path."""
        try:
            file = open(file_path, 'r')
            return FileProcessor(file)
        except IOError as e:
            logger.error(f"Unable to open file {file_path}")
            raise FileReadError(f"Unable to open file {file_path}") from e
