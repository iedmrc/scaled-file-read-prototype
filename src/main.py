import argparse

from src.models import Record
from src.helpers import Logger, FileReadError
from src.file_processors import ProcessorFactory
from src.heap_manager import HeapManager

logger = Logger().get_logger()


class FileProcessorService:
    """Service class to handle file processing."""

    def __init__(self, file_path: str, top: int, chunk_size: int) -> None:
        """
        Initialize the file processor service.

        Args:
            file_path (str): The path to the file to be processed.
            top (int): The number of top records to retrieve.
            chunk_size (int): The number of lines to read per chunk.
        """
        self.file_path = file_path
        self.top = top
        self.chunk_size = chunk_size

    def process_file(self) -> list[Record]:
        """
        Process the file and retrieve the top records.

        Returns:
            List[Record]: A list of the top records.
        """
        processor = ProcessorFactory.create_processor(self.file_path, self.chunk_size)
        heap_maintainer = HeapManager(self.top)
        with processor as file_processor:
            for record in file_processor.read_records():
                heap_maintainer.add_record(record)
        return heap_maintainer.get_top_records()


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Process a file to find URLs with the largest values.")
    parser.add_argument('file_path', type=str, help='The absolute path of the file to process')
    parser.add_argument('--top', type=int, default=10,
                        help='Number of top records to retrieve (default: 10)')
    parser.add_argument('--chunk-size', type=int, default=0,
                        help='Number of lines to read per chunk (default: 0 for single-threaded)')
    return parser.parse_args()


def main() -> None:
    """Main function to execute the file processing."""
    args = parse_arguments()

    logger.info("Starting file processing")

    try:
        service = FileProcessorService(args.file_path, args.top, args.chunk_size)
        top_records = service.process_file()

        logger.info("Processing completed successfully")
        for record in top_records:
            print(record.url)

    except FileReadError as e:
        logger.error(e)
        exit(1)


if __name__ == "__main__":
    main()
