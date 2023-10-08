from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')

class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes:list|None=None, internal_sizes:list|None=None) -> None:
        self.sizes = sizes
        self.size_index = 0
        if sizes is not None:
            self.TABLE_SIZES = sizes
        self.count = 0
        self.array: ArrayR[tuple[K1, LinearProbeTable[K2, V]]] = ArrayR(self.TABLE_SIZES[self.size_index])
        self.internal_sizes = internal_sizes

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2, is_insert: bool) -> tuple[int, int]:
        """
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.
        """
        # Calculate the initial hash indices for key1 and key2 using hash1 and hash2
        index1 = self.hash1(key1)
        index2 = self.hash2(key2, self.internal_tables[index1])

        # If is_insert is True and the table at index1 is full, raise FullError
        if is_insert and self.internal_tables[index1].is_full():
            raise FullError("Table is full and cannot insert.")

        # Start linear probing
        while True:
            current_key1, current_key2 = self.internal_tables[index1].get_keys(index2)

            # If the slot is empty and we're inserting, return the indices
            if current_key1 is None and current_key2 is None and is_insert:
                return index1, index2

            # If we're not inserting and found the keys, return the indices
            if current_key1 == key1 and current_key2 == key2:
                return index1, index2
            
            # Move to the next slot using linear probing
            index2 = (index2 + 1) % len(self.internal_tables[index1])

            # If we've checked all slots, wrap around to the beginning of the table
            if index2 == self.hash2(key2, self.internal_tables[index1]):
                index1 = (index1 + 1) % len(self.internal_tables)

                # If we've checked all top-level tables, raise KeyError
                if index1 == self.hash1(key1):
                    raise KeyError("Key pair not found in the table.")

    def iter_keys(self, key:K1|None=None) -> Iterator[K1|K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        if key is None:
            # Iterate over all top-level tables and yield keys from each
            for table in self.internal_tables:
                yield from table.keys()
        else:
            # Get the index for the top-level key and yield keys from the corresponding internal table
            index = self.hash1(key)
            yield from self.internal_tables[index].keys()

    def keys(self, key:K1|None=None) -> list[K1|K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """
        if key is None:
            # Iterate over all top-level tables and yield values from each
            for table in self.internal_tables:
                yield from table.values()
        else:
            # Get the index for the top-level key and yield values from the corresponding internal table
            index = self.hash1(key)
            yield from self.internal_tables[index].values()

    def iter_values(self, key:K1|None=None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        if key is None:
            # Collect all values from all internal tables into a list
            all_values = [table.values() for table in self.internal_tables]
            return [value for values in all_values for value in values]
        else:
            # Get the index for the top-level key and return values from the corresponding internal table
            index = self.hash1(key)
            return self.internal_tables[index].values()

    def values(self, key:K1|None=None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        if key is None:
            # Collect all values from all internal tables into a list
            all_values = [table.values() for table in self.internal_tables]
            return [value for values in all_values for value in values]
        else:
            # Get the index for the top-level key and return values from the corresponding internal table
            index = self.hash1(key)
            return self.internal_tables[index].values()

    def __contains__(self, key: tuple[K1, K2]) -> bool:
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

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        key1, key2 = key
        index1, index2 = self._linear_probe(key1, key2, is_insert=False)
        if self.internal_tables[index1][index2] is None:
            raise KeyError(f"Key pair {key} not found in the table.")
        return self.internal_tables[index1][index2]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.


        """

        k1_position = self._linear_probe(key, True)

        if self.array[k1_position] is None:
            self.count += 1

        new_linear_probe_table = LinearProbeTable(self.internal_sizes)

        self.array[k1_position] = (key[0], new_linear_probe_table)

        new_linear_probe_table[key[1]] = data


    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        key1, key2 = key
        index1, index2 = self._linear_probe(key1, key2, is_insert=False)
        if self.internal_tables[index1][index2] is None:
            raise KeyError(f"Key pair {key} not found in the table.")
        self.internal_tables[index1][index2] = None



    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        pass

    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        pass

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        pass

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        pass
