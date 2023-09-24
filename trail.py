from __future__ import annotations
from dataclasses import dataclass

from mountain import Mountain

from typing import TYPE_CHECKING, Union

from personality import PersonalityDecision

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
        return self.following

@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--followinTrailg--

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
        new_series = TrailSeries(mountain=mountain, following=self)
        return new_series

    def add_empty_branch_before(self) -> TrailStore:
        """Returns a *new* trail which would be the result of:
        Adding an empty branch, where the current trailstore is now the following path.
        """
        return TrailSplit(top=None, bottom=None, following=self)

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain after the current mountain, but before the following trail.
        """
        new_series = TrailSeries(mountain=self.mountain, following=self.following)
        self.mountain = mountain
        return new_series

    def add_empty_branch_after(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch after the current mountain, but before the following trail.
        """
        return TrailSplit(top=None, bottom=None, following=self)

TrailStore = Union[TrailSplit, TrailSeries, None]

@dataclass
class Trail:

    store: TrailStore = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain before everything currently in the trail.
        """
        new_series = TrailSeries(mountain=mountain, following=self.store)
        return new_series

    def add_empty_branch_before(self) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch before everything currently in the trail.
        """
        return TrailSplit(top=None, bottom=None, following=self.store)

    def follow_path(self, personality: WalkerPersonality) -> None:
        """Follow a path and add mountains according to a personality."""
        current = self.store
        while current:
            if isinstance(current, TrailSeries):
                if current.mountain:
                    personality.add_mountain(current.mountain)
                current = current.following

            elif isinstance(current, TrailSplit):
                decision = personality.select_branch(current.top, current.bottom)
                if decision == PersonalityDecision.STOP:
                    return
                elif decision == PersonalityDecision.TOP:
                    current = current.top if current.top else current.following
                elif decision == PersonalityDecision.BOTTOM:
                    current = current.bottom if current.bottom else current.following
            else:
                break

    def collect_all_mountains(self) -> list[Mountain]:
        """Returns a list of all mountains on the trail."""
        mountains = []
        current = self.store
        while current:
            if isinstance(current, TrailSeries):
                mountains.append(current.mountain)
                current = current.following
            elif isinstance(current, TrailSplit):
                current = current.following
            else:
                break
        return mountains

    def difficulty_maximum_paths(self, max_difficulty: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1008/2085 ONLY!
        raise NotImplementedError()

    def difficulty_difference_paths(self, max_difference: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1054 ONLY!
        raise NotImplementedError()
