import heapq

from src.models import Record

class HeapManager:
    """Maintains a min-heap to store the top N records."""

    def __init__(self, n: int) -> None:
        """
        Initialize the heap manager with a specific size.

        Args:
            n (int): The maximum number of records to store in the heap.
        """
        self.n = n
        self.min_heap: list[Record] = []

    def add_record(self, record: Record) -> None:
        """
        Add a record to the heap, ensuring it contains only the top N records.

        Args:
            record (Record): The record to add to the heap.
        """
        if len(self.min_heap) < self.n:
            heapq.heappush(self.min_heap, record)
        else:
            heapq.heappushpop(self.min_heap, record)

    def get_top_records(self) -> list[Record]:
        """
        Get the top records sorted in descending order.

        Returns:
            List[Record]: A list of the top records sorted in descending order.
        """
        return sorted(self.min_heap, reverse=True)
