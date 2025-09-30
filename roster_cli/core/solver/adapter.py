"""Solver adapter interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from roster_cli.core.models import (
    Availability,
    ConstraintBinding,
    Event,
    Holiday,
    Org,
    Person,
    Patch,
    Resource,
    SolutionBundle,
    Team,
)


@dataclass
class SolveContext:
    """Context for solving."""

    org: Org
    people: list[Person]
    teams: list[Team]
    resources: list[Resource]
    events: list[Event]
    constraints: list[ConstraintBinding]
    availability: list[Availability]
    holidays: list[Holiday]
    from_date: date
    to_date: date
    mode: str
    change_min: bool
    published_solution: SolutionBundle | None = None


class SolverAdapter(ABC):
    """Abstract solver adapter."""

    @abstractmethod
    def build_model(self, context: SolveContext) -> None:
        """Build internal model from context."""
        pass

    @abstractmethod
    def solve(self, timeout_s: int | None = None) -> SolutionBundle:
        """Solve and return solution bundle."""
        pass

    @abstractmethod
    def set_objective(self, weights: dict[str, int]) -> None:
        """Set objective function weights."""
        pass

    @abstractmethod
    def enable_change_minimization(self, enabled: bool, weight_move_published: int) -> None:
        """Enable/disable change minimization."""
        pass

    @abstractmethod
    def incremental_update(self, changes: Patch) -> None:
        """Apply incremental changes to model."""
        pass
