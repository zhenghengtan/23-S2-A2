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
        """Returns a list of all mountains on the trail."""
        mountains = []  # List to store encountered mountains
        trails_to_visit = LinkedStack()  # Stack to perform depth-first traversal

        # Start from the current trail
        current = self.store

        while current is not None or len(trails_to_visit) > 0:
            if current is None:
                current = trails_to_visit.pop()

            if isinstance(current, TrailSeries):
                # If it's a TrailSeries, add the mountain and move to the following trail
                mountains.append(current.mountain)
                current = current.following.store

            elif isinstance(current, TrailSplit):
                # If it's a TrailSplit, add the top and bottom branches to the stack
                if current.following.store is not None:
                    trails_to_visit.push(current.following.store)
                trails_to_visit.push(current.top.store)
                trails_to_visit.push(current.bottom.store)

            else:
                break
        return mountains


    def difficulty_maximum_paths(self, max_difficulty: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1008/2085 ONLY!
        paths = []  # List to store valid paths
        current_path = []  # List to store the current path being explored

        def explore_path(current, current_diff):
            if isinstance(current, TrailSeries):
                # If it's a TrailSeries, add the mountain to the current path
                current_path.append(current.mountain)
                current_diff += current.mountain.difficulty_level

                # Continue exploring the following trail
                explore_path(current.following.store, current_diff)

                # Remove the last mountain to backtrack and explore the other branch
                current_path.pop()
                current_diff -= current.mountain.difficulty_level

            elif isinstance(current, TrailSplit):
                if current.following.store is not None:
                    # Explore the following trail
                    explore_path(current.following.store, current_diff)

                # Explore the top branch
                explore_path(current.top.store, current_diff)

                # Explore the bottom branch
                explore_path(current.bottom.store, current_diff)

            if current_diff <= max_difficulty:
                # If the current path's difficulty is within the given 'diff', add it to paths
                paths.append(list(current_path))

        # Start exploring from the current trail with a difficulty of 0
        explore_path(self.store, 0)

        return paths

    def difficulty_difference_paths(self, max_difference: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1054 ONLY!
        raise NotImplementedError()
