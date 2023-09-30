from __future__ import annotations
from mountain import Mountain

class MountainManager:

    # def __init__(self) -> None:
    #     pass

    # def add_mountain(self, mountain: Mountain) -> None:
    #     raise NotImplementedError()

    # def remove_mountain(self, mountain: Mountain) -> None:
    #     raise NotImplementedError()

    # def edit_mountain(self, old: Mountain, new: Mountain) -> None:
    #     raise NotImplementedError()

    # def mountains_with_difficulty(self, diff: int) -> list[Mountain]:
    #     raise NotImplementedError()

    # def group_by_difficulty(self) -> list[list[Mountain]]:
    #     raise NotImplementedError()
        
    def __init__(self) -> None:
        self.mountains = []

    def add_mountain(self, mountain: Mountain) -> None:
        self.mountains.append(mountain)

    def remove_mountain(self, mountain: Mountain) -> None:
        if mountain in self.mountains:
            self.mountains.remove(mountain)

    def edit_mountain(self, old: Mountain, new: Mountain) -> None:
        if old in self.mountains:
            index = self.mountains.index(old)
            self.mountains[index] = new

    def mountains_with_difficulty(self, diff: int) -> list[Mountain]:
        return [mountain for mountain in self.mountains if mountain.difficulty_level == diff]

    def group_by_difficulty(self) -> list[list[Mountain]]:
         # Create a dictionary to group mountains by difficulty
        grouped_mountains = {}
        for mountain in self.mountains:
            difficulty = mountain.difficulty_level
            if difficulty not in grouped_mountains:
                grouped_mountains[difficulty] = []
            grouped_mountains[difficulty].append(mountain)

        # Sort the groups by difficulty in ascending order
        sorted_groups = sorted(grouped_mountains.items(), key=lambda x: x[0])

        # Extract the lists of mountains from the sorted groups
        result = [group[1] for group in sorted_groups]
        return result

