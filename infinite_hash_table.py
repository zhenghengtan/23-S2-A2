from __future__ import annotations
from typing import Generic, TypeVar

from data_structures.referential_array import ArrayR

K = TypeVar("K")
V = TypeVar("V")

class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    TABLE_SIZE = 27

    def __init__(self) -> None:
        """
        Complexity:Best Case: O(1)
                   Worst Case: O(1)
        """
        self.level = 0 # Initialize the level to 0
        self.table = [None] * self.TABLE_SIZE

    def hash(self, key: K) -> int:
        """
        Complexity:Best Case: O(1)
                   Worst Case: O(len(key))
        """
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        Complexity:Best Case: O(1)
                   Worst Case: O(len(key))
        """
        index = self.hash(key)
        if self.table[index] is None:
            raise KeyError(f"Key '{key}' not found")
        return self.table[index][key]


    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        Complexity:Best Case: O(1)
                   Worst Case: O(len(key))
        """
        index = self.hash(key)  # Calculate the index where the key-value pair should be stored
        if self.table[index] is None:  # Check if the slot at the calculated index is empty
            self.table[index] = {}  # If the slot is empty, create an empty dictionary in that slot
        elif not isinstance(self.table[index], dict):
            # If the slot is not empty and not a dictionary, it means a sub-table should be created
            # Create a new InfiniteHashTable as a sub-table
            sub_table = InfiniteHashTable(self.level + 1)
            sub_table[key] = value  # Add the key-value pair to the sub-table
            self.table[index] = sub_table  # Replace the existing entry with the sub-table
            return  # Return to avoid setting the key-value pair in the sub-table again

        # If the slot is not empty and is a dictionary or sub-table, set the value in the appropriate structure
        self.table[index][key] = value

    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        Complexity:Best Case: O(1)
                   Worst Case: O(len(key))
        """
        index = self.hash(key)
        if self.table[index] is None or key not in self.table[index]:
            raise KeyError(f"Key '{key}' not found")
        del self.table[index][key]
        # Check if the current table has only one entry left
        if len(self.table[index]) == 1:
            # Collapse the table to a single entry in the parent table
            self.table[index] = None
            # Update the level to move up in the hierarchy
            self.level += 1

    def __len__(self) -> int:
        """
        Complexity:Best Case: O(1)
                   Worst Case: O(N) where N is the number of key-value pairs
        """
        count = 0
        for entry in self.table:
            if entry is not None:
                count += len(entry)
        return count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        return str(self.table)

    def get_location(self, key) -> list[int]:
        """
        Get the sequence of positions required to access this key.

        :raises KeyError: when the key doesn't exist.
        Complexity:Best Case: O(1)
                   Worst Case: O(len(key))
        """
        location = []
        current_level = 0
        while current_level <= self.level:
            index = self.hash(key)
            location.append(index)
            if self.table[index] is None:
                raise KeyError(f"Key '{key}' not found")
            if isinstance(self.table[index], InfiniteHashTable):
                self.level += 1  # Increase the level if it's a sub-table
            key = key[1:]  # Adjust the key for the next level
            current_level += 1
        return location

    def __contains__(self, key: K) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def sort_keys(self, current=None) -> list[str]:
        """
        Returns all keys currently in the table in lexicographically sorted order.
        Complexity:Best Case: O(N log N)
                   Worst Case: O(N^2), where n is the number of keys in the hash table
        """
        if current is None:
            current = self.table  # Start from the top-level table
        keys = []
        for entry in current:
            if entry is None:
                continue
            if isinstance(entry, dict):
                # Entry is a dictionary, so traverse its keys recursively
                keys.extend(self.sort_keys(entry))
            else:
                # Entry is a key-value pair
                keys.append(entry)
        return sorted(keys)

