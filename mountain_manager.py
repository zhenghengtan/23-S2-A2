from __future__ import annotations
from mountain import Mountain

class MountainManager:

    def __init__(self) -> None:
        """
        Complexity:Best Case: O(1)
                   Worst Case: O(1), just initialisations
        """
        self.mountains = []

    def add_mountain(self, mountain: Mountain) -> None:
        """
        append mounatin
        Complexity:Best Case: O(1)
                   Worst Case: O(n), where n is the current number of mountains
        """
        self.mountains.append(mountain)

    def remove_mountain(self, mountain: Mountain) -> None:
        """
        remove mounatin
        Complexity:Best Case: O(1)
                   Worst Case: O(n), where n is the number of mountain
        """
        if mountain in self.mountains:
            self.mountains.remove(mountain)

    def edit_mountain(self, old: Mountain, new: Mountain) -> None:
        """
        remove old mounatain and add new mountain
        Complexity:Best Case: O(1)
                   Worst Case: O(n), where n is the number of mountain
        """
        if old in self.mountains:
            index = self.mountains.index(old)
            self.mountains[index] = new

    def mountains_with_difficulty(self, diff: int) -> list[Mountain]:
        """
        iterates through the list of mountains and collects mountains with the specified difficulty
        Complexity:Best Case: O(1)
                   Worst Case: O(n), where n is the number of mountain
        """
        return [mountain for mountain in self.mountains if mountain.difficulty_level == diff]

    def group_by_difficulty(self) -> list[list[Mountain]]:
        """
        creates a dictionary with 'difficulty' as keys and lists of mountains as values. 
        The dictionary creation loop runs in O(n) time. 
        Sorting the dictionary keys in ascending order takes O(nlog(n)) time
        Complexity:Best Case: O(n)
                   Worst Case: O(nlogn), just initialisations
        """
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

