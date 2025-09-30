"""DSL data structures for constraint evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from roster_cli.core.models import Event, Person, Team


@dataclass
class EvalContext:
    """Context for evaluating constraints."""

    event: Event | None = None
    person: Person | None = None
    team: Team | None = None
    date: date | None = None
    all_events: list[Event] | None = None
    all_people: list[Person] | None = None
    all_teams: list[Team] | None = None
    holidays: dict[date, bool] | None = None
    params: dict[str, Any] | None = None
    assignments: dict[str, list[str]] | None = None  # event_id -> person_ids
    person_assignments: dict[str, list[Event]] | None = None  # person_id -> events


@dataclass
class ConstraintResult:
    """Result of constraint evaluation."""

    satisfied: bool
    penalty: float = 0.0
    reason: str = ""
