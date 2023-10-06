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
                current = current.following




            elif isinstance(current, TrailSplit):
                if current.following.store != None:
                    trails.push(current.following.store)
                current_select = personality.select_branch(current.top, current.bottom)
                if current_select == PersonalityDecision.TOP:
                    current = current.top.store
                elif current_select == PersonalityDecision.BOTTOM:
                    current = current.bottom.store
                elif current_select == PersonalityDecision.STOP:
                    raise NotImplementedError
            else:
                break
                




    def collect_all_mountains(self) -> list[Mountain]:
        """Returns a list of all mountains on the trail."""
        all_mountains = []

        # Start from the current TrailSeries
        current_series = self.store
        while current_series:
            # Check if the current series has a mountain
            if isinstance(current_series, TrailSeries):
                all_mountains.append(current_series.mountain)

            # Move to the next series (following)
            current_series = current_series.following.store if isinstance(current_series.following, Trail) else None

        return all_mountains


    def difficulty_maximum_paths(self, max_difficulty: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1008/2085 ONLY!
        def dfs(current_series, current_path, current_difficulty):
            if not current_series:
                return []
            
            # Check if we've reached the end of a branch or the maximum difficulty
            if isinstance(current_series, TrailSplit) or current_difficulty > max_difficulty:
                return []
            
            # Check if the current series has a mountain
            if isinstance(current_series, TrailSeries):
                current_path.append(current_series.mountain)
                current_difficulty += current_series.mountain.difficulty
            # Check if we've reached the end of the trail
            if not current_series.following:
                return [current_path[:]]

            paths = []

            # Explore each possible branch
            for branch in [current_series.top, current_series.bottom]:
                new_path = current_path[:]
                new_difficulty = current_difficulty
                paths.extend(dfs(branch.store, new_path, new_difficulty))

            # Continue along the main trail
            paths.extend(dfs(current_series.following.store, current_path, current_difficulty))

            return paths
        
        initial_path = []
        initial_difficulty = 0
        paths = dfs(self.store, initial_path, initial_difficulty)
        return paths

    def difficulty_difference_paths(self, max_difference: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1054 ONLY!
        raise NotImplementedError()
