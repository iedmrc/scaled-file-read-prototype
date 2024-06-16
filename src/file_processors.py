from abc import ABC, abstractmethod
from typing import Generator, IO
from concurrent.futures import ThreadPoolExecutor, as_completed

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


class ChunkFileProcessor(AbstractFileProcessor):
    """Processor for reading specific chunks of a file."""

    def __init__(self, file: IO, start_line: int, chunk_size: int):
        super().__init__(file)
        self.__start_line = start_line
        self.__chunk_size = chunk_size

    def read_records(self) -> Generator[Record, None, None]:
        """Read a specific chunk of records from the file."""
        for _ in range(self.__start_line):
            self.file.readline()  # Skip lines until start_line
        for _ in range(self.__chunk_size):
            line = self.file.readline()
            if not line:
                break
            try:
                url, value = line.rsplit(maxsplit=1)
                yield Record(int(value), url)
            except ValueError as e:
                logger.error(f"Error processing line: {line}")
                raise FileReadError(f"Error processing line: {line}") from e


class ParallelFileProcessor(AbstractFileProcessor):
    """Processor for reading files in parallel using chunks."""

    def __init__(self, file: IO, chunk_size: int):
        super().__init__(file)
        self.chunk_size = chunk_size

    def read_records(self) -> Generator[Record, None, None]:
        """Read records from the file in parallel."""
        total_lines = sum(1 for _ in self.file)
        self.file.seek(0)  # Reset file pointer to the beginning
        chunks = [(i, self.chunk_size) for i in range(0, total_lines, self.chunk_size)]

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.__process_chunk, start_line,
                                       self.chunk_size) for start_line, _ in chunks]
            for future in as_completed(futures):
                for record in future.result():
                    yield record

    def __process_chunk(self, start_line: int, chunk_size: int) -> list[Record]:
        """Process a chunk of the file and return records."""
        try:
            with open(self.file.name, 'r') as file:
                chunk_processor = ChunkFileProcessor(file, start_line, chunk_size)
                return list(chunk_processor.read_records())
        except IOError as e:
            logger.error(f"Unable to open file {self.file.name}")
            raise FileReadError(f"Unable to open file {self.file.name}") from e


class ProcessorFactory:
    """Factory class to create and manage processors."""

    @staticmethod
    def create_processor(file_path: str, chunk_size: int = 0) -> AbstractFileProcessor:
        """Create a file processor for the given file path."""
        try:
            file = open(file_path, 'r')
            if chunk_size > 0:
                return ParallelFileProcessor(file, chunk_size)
            else:
                return FileProcessor(file)
        except IOError as e:
            logger.error(f"Unable to open file {file_path}")
            raise FileReadError(f"Unable to open file {file_path}") from e
