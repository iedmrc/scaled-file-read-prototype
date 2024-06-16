from abc import ABC, abstractmethod
from typing import Generator, IO, Optional, Type
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.models import Record
from src.helpers import Logger, FileReadError

logger = Logger().get_logger()


class AbstractFileProcessor(ABC):
    """Abstract base class for file processors."""

    def __init__(self, file: IO) -> None:
        """
        Initialize the file processor.

        Args:
            file (IO): The file object to be processed.
        """
        self.file = file

    @abstractmethod
    def read_records(self) -> Generator[Record, None, None]:
        """
        Read records from the file.

        Yields:
            Generator[Record, None, None]: A generator yielding Record objects.
        """
        pass

    def __enter__(self) -> 'AbstractFileProcessor':
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[Type[BaseException]]) -> None:
        """
        Exit the runtime context related to this object.

        Args:
            exc_type (Optional[Type[BaseException]]): The exception type.
            exc_val (Optional[BaseException]): The exception value.
            exc_tb (Optional[Type[BaseException]]): The traceback object.
        """
        self.file.close()


class FileProcessor(AbstractFileProcessor):
    """Processor for reading entire files."""

    def read_records(self) -> Generator[Record, None, None]:
        """
        Read records from the file and yield them.

        Yields:
            Generator[Record, None, None]: A generator yielding Record objects.

        Raises:
            FileReadError: If there is an error processing a line.
        """
        for line in self.file:
            try:
                url, value = line.rsplit(maxsplit=1)
                yield Record(int(value), url)
            except ValueError as e:
                logger.error(f"Error processing line: {line}")
                raise FileReadError(f"Error processing line: {line}") from e


class ChunkFileProcessor(AbstractFileProcessor):
    """Processor for reading specific chunks of a file."""

    def __init__(self, file: IO, start_line: int, chunk_size: int) -> None:
        """
        Initialize the chunk file processor.

        Args:
            file (IO): The file object to be processed.
            start_line (int): The starting line for the chunk.
            chunk_size (int): The number of lines to read in the chunk.
        """
        super().__init__(file)
        self.__start_line = start_line
        self.__chunk_size = chunk_size

    def read_records(self) -> Generator[Record, None, None]:
        """
        Read a specific chunk of records from the file.

        Yields:
            Generator[Record, None, None]: A generator yielding Record objects.

        Raises:
            FileReadError: If there is an error processing a line.
        """
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

    def __init__(self, file: IO, chunk_size: int) -> None:
        """
        Initialize the parallel file processor.

        Args:
            file (IO): The file object to be processed.
            chunk_size (int): The number of lines to read in each chunk.
        """
        super().__init__(file)
        self.chunk_size = chunk_size

    def read_records(self) -> Generator[Record, None, None]:
        """
        Read records from the file in parallel.

        Yields:
            Generator[Record, None, None]: A generator yielding Record objects.
        """
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
        """
        Process a chunk of the file and return records.

        Args:
            start_line (int): The starting line for the chunk.
            chunk_size (int): The number of lines to read in the chunk.

        Returns:
            list[Record]: A list of Record objects.

        Raises:
            FileReadError: If there is an error opening the file.
        """
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
        """
        Create a file processor for the given file path.

        Args:
            file_path (str): The path to the file to be processed.
            chunk_size (int, optional): The number of lines to read in each chunk. Defaults to 0.

        Returns:
            AbstractFileProcessor: The created file processor.

        Raises:
            FileReadError: If there is an error opening the file.
        """
        try:
            file = open(file_path, 'r')
            if chunk_size > 0:
                return ParallelFileProcessor(file, chunk_size)
            else:
                return FileProcessor(file)
        except IOError as e:
            logger.error(f"Unable to open file {file_path}")
            raise FileReadError(f"Unable to open file {file_path}") from e
