import heapq

from models import Record

class HeapManager:
    """Maintains a min-heap to store the top N records."""

    def __init__(self, n: int):
        self.n = n
        self.min_heap = []

    def add_record(self, record: Record):
        """Add a record to the heap, ensuring it contains only the top N records."""
        if len(self.min_heap) < self.n:
            heapq.heappush(self.min_heap, record)
        else:
            heapq.heappushpop(self.min_heap, record)

    def get_top_records(self) -> list[Record]:
        """Get the top records sorted in descending order."""
        return sorted(self.min_heap, reverse=True)
