import argparse
from helpers import Logger, FileReadError
from file_processors import ProcessorFactory
from heap_manager import HeapManager

logger = Logger().get_logger()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process a file to find URLs with the largest values.")
    parser.add_argument('file_path', type=str, help='The absolute path of the file to process')
    parser.add_argument('--top', type=int, default=10,
                        help='Number of top records to retrieve (default: 10)')
    return parser.parse_args()


def main():
    args = parse_arguments()

    logger.info("Starting file processing")

    try:
        processor = ProcessorFactory.create_processor(args.file_path)
        heap_maintainer = HeapManager(args.top)

        with processor as file_processor:
            for record in file_processor.read_records():
                heap_maintainer.add_record(record)

        top_records = heap_maintainer.get_top_records()

        logger.info("Processing completed successfully")
        for record in top_records:
            print(record.url)

    except FileReadError as e:
        logger.error(e)
        exit(1)


if __name__ == "__main__":
    main()
