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
        self.size_index = 0
        if sizes is not None:
            self.TABLE_SIZES = sizes
        self.count = 0

        # First key hashes to a LinearProbe hash table. Get that LinearProbe table, then hash the second key to that table.
        self.array: ArrayR[tuple[K1, LinearProbeTable[K2, V]]] = ArrayR(self.TABLE_SIZES[self.size_index])

        # If internal_sizes is None, use the same table sizes as the top-level table.
        self.internal_sizes = internal_sizes if internal_sizes is not None else self.TABLE_SIZES

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

        _linear_probe(self, key1: K1, key2: K2, is_insert: bool) -> tuple[int, int] , return the:
            Index to access in the top-level table, followed by Index to access in the low-level table
            In a tuple.
            Your linear probe method should create the internal hash table if is_insert is true and this is the first pair with key1 .

            Complexity: Best case O(1), empty slot in top-level table, no further probing
                        Worst case O(n), when the entire top-level table is iterated, n is the size of the top-level table
        """

        outer_idx = None 
        inner_idx = None 

        # Calculate the initial hash indices for key1 and key2 using hash1 and hash2
        index1 = self.hash1(key1)
        # If subtable is not none, linear probe until hit none
        for _ in range(self.table_size):
            if self.array[index1] is None:
                if is_insert:
                    inner_lpt = LinearProbeTable(self.internal_sizes)
                    self.count += 1
                    inner_lpt.hash = lambda k: self.hash2(k, inner_lpt)
                    # create the linear probe at that place as tuple[K1, ]
                    self.array[index1] = (key1, inner_lpt)
                    outer_idx = index1 
                    inner_idx = self.hash2(key2, inner_lpt)
                    return (outer_idx, inner_idx)
                else:
                    raise KeyError(key1)
            elif self.array[index1][0] == key1:
                # Found the key1. Now search the subtable 
                outer_idx = index1
                inner_lpt = self.array[index1][1]

                # Used an internal function
                inner_idx = inner_lpt._linear_probe(key2, is_insert)
                return (outer_idx, inner_idx)
            else:
                # Taken by something else. Time to linear probe 
                index1 = (index1 + 1) % self.table_size 

        if is_insert and self[index1].is_full():
            raise FullError("Table is full and cannot insert.") 

        return (outer_idx, inner_idx)

    def iter_keys(self, key:K1|None=None) -> Iterator[K1|K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        
        Complexity: Best case O(1) when key is None
                    Worst case O(N) when key is provided, N is the number of elements in the top-level table
        """
        if key is None:
            for kv in self.array:
                if kv is not None:
                    key, _ = kv 
                    yield key
        else:
            # Get the index for the top-level key and yield keys from the corresponding internal table
            index = self.hash1(key)
            # Linear probe until key matches
            
            for _ in range(len(self.array)):
                if self.array[index] is None:
                    raise KeyError(f"Key {key} not found in the table.")
                elif self.array[index][0] == key:
                    # Found the key1. Now search the subtable 
                    inner_lpt = self.array[index][1]
                    for inner_key in inner_lpt.keys():
                        yield inner_key
                    return
                else:
                    # Taken by something else. Time to linear probe 
                    index = (index + 1) % self.table_size

    def keys(self, key:K1|None=None) -> list[K1|K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.

        Complexity: Best case O(1) when key is None
                    Worst case O(n) when key is provided
        """
        if key is None:
            res = [kv[0] for kv in self.array if kv is not None]
            return res 
        else:
            index = self.hash1(key)

            # Linear probe until key matches
            for _ in range(len(self.array)):
                if self.array[index] is None:
                    raise KeyError(f"Key {key} not found in the table.")
                elif self.array[index][0] == key:
                    # Found the key1. Now search the subtable 
                    inner_lpt = self.array[index][1]
                    return inner_lpt.keys()
                else:
                    # Taken by something else. Time to linear probe 
                    index = (index + 1) % self.table_size

    def iter_values(self, key:K1|None=None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.

        Complexity: Best case O(1) when key is None
                    Worst case O(n) when key is provided
        """
        if key is None:
            for kv in self.array:
                if kv is not None:
                    key, lpt = kv 
                    for value in lpt.values():
                        yield value
        else:
            # Get the index for the top-level key and return values from the corresponding internal table
            outer_idx = self.hash1(key)
            inner_lpt = self.array[outer_idx][1]

            # Linear probe until key matches
            for _ in range(len(self.array)):
                if self.array[outer_idx] is None:
                    raise KeyError(f"Key {key} not found in the table.")
                elif self.array[outer_idx][0] == key:
                    # Found the key1. Now search the subtable 
                    for value in inner_lpt.values():
                        yield value
                    return
                else:
                    # Taken by something else. Time to linear probe 
                    outer_idx = (outer_idx + 1) % self.table_size


    def values(self, key:K1|None=None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.

        Complexity: Best case O(1) when key is None
                    Worst case O(n) when key is provided
        """
        if key is None:
            res = []
            for kv in self.array:
                if kv is not None:
                    key, lpt = kv 
                    res.extend(lpt.values())

            return res
        else:
            # Get the index for the top-level key and return values from the corresponding internal table
            outer_index = self.hash1(key)
            inner_lpt = self.array[outer_index][1]

            # Linear probe until key matches
            for _ in range(len(self.array)):
                if self.array[outer_index] is None:
                    raise KeyError(f"Key {key} not found in the table.")
                elif self.array[outer_index][0] == key:
                    # Found the key1. Now search the subtable 
                    return inner_lpt.values()
                else:
                    # Taken by something else. Time to linear probe 
                    outer_index = (outer_index + 1) % self.table_size


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

        :complexity: See linear probe.
        """
        print("Current key is", key)
        key1, key2 = key
        index1, _ = self._linear_probe(key1, key2, is_insert=False)
        if self.array[index1] is None:
            raise KeyError(f"Key pair {key} not found in the table.")
        return self.array[index1][1][key2]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.

        :complexity: see rehash
        """
        key1, key2 = key
        k1_position, _ = self._linear_probe(key1, key2, True)
        
        self.array[k1_position][1][key2] = data

        if self.count > self.table_size / 2:
            self._rehash()


    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.

        :complexity: See linear probe.
        """
        key1, key2 = key
        index1, index2 = self._linear_probe(key1, key2, is_insert=False)
        if self.array[index1][1][key2] is None:
            raise KeyError(f"Key pair {key} not found in the table.")

        inner_lpt = self.array[index1][1] 
        del inner_lpt[key2]

        if inner_lpt.is_empty():
            self.array[index1] = None
            self.count -= 1


    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        old_array = self.array
        self.size_index += 1
        if self.size_index >= len(self.TABLE_SIZES):
            # Cannot be resized further.
            return
        self.array = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0
        
        for kv in old_array:
            if kv is not None:
                key, lpt = kv 
                inner_keys = lpt.keys()
                for inner_key in inner_keys:
                    self[key, inner_key] = lpt[inner_key]

    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        Best and worst are O(1)
        """
        return len(self.array)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        Best and worst are O(1)
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        return str([str(item) for item in self.array])