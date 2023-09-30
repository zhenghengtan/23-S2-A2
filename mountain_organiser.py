from __future__ import annotations

from mountain import Mountain

class MountainOrganiser:

    def __init__(self) -> None:
        self.mountains = []  # Sorted list of mountains based on difficulty_level and length
        self.mountain_dict = {}  # Dictionary to map mountain names to their position in the sorted list

    def cur_position(self, mountain: Mountain) -> int:
        if mountain.name not in self.mountain_dict:
            raise KeyError("Mountain not found in the organiser")
        return self.mountain_dict[mountain.name]

    def add_mountains(self, mountains: list[Mountain]) -> None:
        for mountain in mountains:
            if mountain.name in self.mountain_dict:
                continue  # Mountain already added
            index = self._find_insert_position(mountain)
            insort_left(self.mountains, mountain, key=lambda x: (x.difficulty_level, x.length))
            self._update_dict(index)

    def _find_insert_position(self, mountain: Mountain) -> int:
        left, right = 0, len(self.mountains)
        while left < right:
            mid = (left + right) // 2
            if (self.mountains[mid].difficulty_level, self.mountains[mid].length) < (mountain.difficulty_level, mountain.length):
                left = mid + 1
            else:
                right = mid
        return left

    def _update_dict(self, index: int) -> None:
        for i in range(index, len(self.mountains)):
            self.mountain_dict[self.mountains[i].name] = i
