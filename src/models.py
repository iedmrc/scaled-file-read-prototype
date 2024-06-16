from dataclasses import dataclass


@dataclass
class Record:
    value: int
    url: str

    def __lt__(self, other: 'Record') -> bool:
        """
        Check if this record is less than another record.

        Args:
            other (Record): The other record to compare against.

        Returns:
            bool: True if this record's value is less than the other record's value, False otherwise.
        """
        return self.value < other.value

    def __le__(self, other: 'Record') -> bool:
        """
        Check if this record is less than or equal to another record.

        Args:
            other (Record): The other record to compare against.

        Returns:
            bool: True if this record's value is less than or equal to the other record's value, False otherwise.
        """
        return self.value <= other.value

    def __gt__(self, other: 'Record') -> bool:
        """
        Check if this record is greater than another record.

        Args:
            other (Record): The other record to compare against.

        Returns:
            bool: True if this record's value is greater than the other record's value, False otherwise.
        """
        return self.value > other.value

    def __ge__(self, other: 'Record') -> bool:
        """
        Check if this record is greater than or equal to another record.

        Args:
            other (Record): The other record to compare against.

        Returns:
            bool: True if this record's value is greater than or equal to the other record's value, False otherwise.
        """
        return self.value >= other.value

    def __eq__(self, other: 'Record') -> bool:
        """
        Check if this record is equal to another record.

        Args:
            other (Record): The other record to compare against.

        Returns:
            bool: True if this record's value is equal to the other record's value, False otherwise.
        """
        return self.value == other.value

    def __ne__(self, other: 'Record') -> bool:
        """
        Check if this record is not equal to another record.

        Args:
            other (Record): The other record to compare against.

        Returns:
            bool: True if this record's value is not equal to the other record's value, False otherwise.
        """
        return self.value != other.value
