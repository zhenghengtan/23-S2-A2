from __future__ import annotations
from dataclasses import dataclass

from mountain import Mountain

from typing import TYPE_CHECKING, Union

from data_structures.linked_stack import LinkedStack


# Avoid circular imports for typing.
if TYPE_CHECKING:
    from personality import WalkerPersonality

@dataclass
class TrailSplit:
    """
    A split in the trail.
       _____top______
      /              \
    -<                >-following-
      \____bottom____/
    """

    top: Trail
    bottom: Trail
    following: Trail

    def remove_branch(self) -> TrailStore:
        """Removes the branch, should just leave the remaining following trail."""
        return self.following.store

@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--following--

    """

    mountain: Mountain
    following: Trail

    def remove_mountain(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Removing the mountain at the beginning of this series.
        """
        return self.following

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain in series before the current one.
        """
        return TrailSeries(mountain, Trail(self))

    def add_empty_branch_before(self) -> TrailStore:
        """Returns a *new* trail which would be the result of:
        Adding an empty branch, where the current trailstore is now the following path.
        """
        return TrailSplit(Trail(), Trail(), Trail(self))

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain after the current mountain, but before the following trail.
        """
        return TrailSeries(self.mountain, Trail(TrailSeries(mountain, self.following)))

    def add_empty_branch_after(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch after the current mountain, but before the following trail.
        """
        return TrailSeries(self.mountain, Trail(TrailSplit(Trail(), Trail(), self.following)))

TrailStore = Union[TrailSplit, TrailSeries, None]

@dataclass
class Trail:

    store: TrailStore = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain before everything currently in the trail.
        """
        new_series = TrailSeries(mountain, Trail(self.store))
        return Trail(new_series)

    def add_empty_branch_before(self) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch before everything currently in the trail.
        """
        return Trail(TrailSplit(Trail(), Trail(), Trail(self.store)))

    def follow_path(self, personality: WalkerPersonality) -> None:
        """Follow a path and add mountains according to a personality."""
        from personality import PersonalityDecision
        trails = LinkedStack()
        current = self.store
        while current is not None or len(trails) > 0:

            if current == None:
                current = trails.pop()

            #if current is a trailseries, add the mountain in the trailseries
            if isinstance(current, TrailSeries):
                personality.add_mountain(current.mountain)
                #the following of the trail series is added
                current = current.following.store

            elif isinstance(current, TrailSplit):
                if current.following.store != None:
                    trails.push(current.following.store)
                current_select = personality.select_branch(current.top, current.bottom)
                if current_select == PersonalityDecision.TOP:
                    current = current.top.store
                elif current_select == PersonalityDecision.BOTTOM:
                    current = current.bottom.store
                elif current_select == PersonalityDecision.STOP:
                    return

                
    def collect_all_mountains(self) -> list[Mountain]:
        """
        Returns a list of all mountains on the trail.
        Complexity:best case:O(1)
                   worst case:O(N), where N is the total number of nodes in the trail structure
        """
        mountains = []

        def traverse(node):
            if node is None:
                return

            if isinstance(node, TrailSeries):
                traverse(node.mountain)
                traverse(node.following)
            elif isinstance(node, TrailSplit):
                traverse(node.top)
                traverse(node.bottom)
                traverse(node.following)
            elif isinstance(node, Mountain):
                mountains.append(node)
            elif isinstance(node, Trail): 
                traverse(node.store)

        traverse(self.store)
        return mountains


    def difficulty_maximum_paths(self, max_difficulty: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1008/2085 ONLY!
        paths = []  # To store valid paths

        def traverse(node, current_path, current_difficulty):
            if node is None:
                return

            if isinstance(node, TrailSeries):
                traverse(node.mountain, current_path, current_difficulty)  # Continue with the current path
                traverse(node.following, current_path, current_difficulty)  # Continue with the current path
            elif isinstance(node, TrailSplit):
                # Explore both branches
                top_path = current_path.copy()
                bottom_path = current_path.copy()

                # Continue with the top branch
                traverse(node.top, top_path, current_difficulty)

                # Continue with the bottom branch
                traverse(node.bottom, bottom_path, current_difficulty)

            elif isinstance(node, Mountain):
                # Check if the mountain's difficulty is within the limit
                if node.difficulty_level <= max_difficulty:
                    current_path.append(node)
                    current_difficulty += node.difficulty_level

                    # If the path's difficulty is within the limit, add it to the result
                    if current_difficulty <= max_difficulty:
                        paths.append(current_path.copy())

            elif isinstance(node, Trail):
                # Handle the case when node is a Trail
                traverse(node.store, current_path, current_difficulty)

        # Start traversal from the current Trail instance
        traverse(self.store, [], 0)
        return paths

    def difficulty_difference_paths(self, max_difference: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1054 ONLY!
        raise NotImplementedError()
