"""Core Pydantic data models for roster scheduling."""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class Person(BaseModel):
    """A person who can be assigned to events."""

    id: str
    name: str
    roles: list[str]
    skills: list[str] = Field(default_factory=list)
    external_ids: dict[str, str] = Field(default_factory=dict)


class Team(BaseModel):
    """A team consisting of multiple people."""

    id: str
    name: str
    members: list[str]


class Resource(BaseModel):
    """A resource like a ground or room."""

    id: str
    type: str  # "ground"|"room"
    capacity: int
    location: str | None = None


class RequiredRole(BaseModel):
    """Role requirement for an event."""

    role: str
    count: int


class Event(BaseModel):
    """An event that needs people assigned."""

    id: str
    type: str  # "match"|"shift"|"oncall_shift"
    start: datetime
    end: datetime
    resource_id: str | None = None
    required_roles: list[RequiredRole] = Field(default_factory=list)
    team_ids: list[str] = Field(default_factory=list)
    assignees: list[str] = Field(default_factory=list)


class VacationPeriod(BaseModel):
    """A vacation period for availability."""

    start: date
    end: date


class Availability(BaseModel):
    """Availability rules for a person or resource."""

    person_id: str | None = None
    resource_id: str | None = None
    rrule: str | None = None
    exceptions: list[date] = Field(default_factory=list)
    vacations: list[VacationPeriod] = Field(default_factory=list)


class Holiday(BaseModel):
    """A holiday definition."""

    date: date
    label: str
    is_long_weekend: bool = False


class HolidayFile(BaseModel):
    """Holiday file containing regional holidays."""

    region: str
    days: list[Holiday]


class OrgDefaults(BaseModel):
    """Default configuration values for org."""

    change_min_weight: int = 100
    fairness_weight: int = 50
    cooldown_days: int = 14


class Org(BaseModel):
    """Organization configuration."""

    org_id: str
    region: str
    defaults: OrgDefaults = Field(default_factory=OrgDefaults)


class PeopleFile(BaseModel):
    """File containing people definitions."""

    people: list[Person]


class TeamsFile(BaseModel):
    """File containing team definitions."""

    teams: list[Team]


class ResourcesFile(BaseModel):
    """File containing resource definitions."""

    resources: list[Resource]


class EventsFile(BaseModel):
    """File containing event definitions."""

    events: list[Event]


class PredicateNode(BaseModel):
    """A predicate node in constraint DSL."""

    any_: list["PredicateNode"] | None = Field(default=None, alias="any")
    all_: list["PredicateNode"] | None = Field(default=None, alias="all")
    predicate: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class ConstraintAction(BaseModel):
    """Action to take when constraint applies."""

    forbid_if: str | None = None
    require_roles: list[RequiredRole] | None = None
    enforce_graph: dict[str, Any] | None = None
    enforce_min_gap_hours: int | None = None
    enforce_cap: dict[str, Any] | None = None
    penalize_if: dict[str, Any] | None = None


class ConstraintBinding(BaseModel):
    """A constraint binding from YAML."""

    key: str
    scope: str  # "org"|"team"|"person"|"event"|"schedule"
    applies_to: list[str]
    params: dict[str, Any] = Field(default_factory=dict)
    when: PredicateNode | None = None
    then: ConstraintAction
    severity: str  # "hard"|"soft"
    weight: int | None = None


class Assignment(BaseModel):
    """An assignment in a solution."""

    event_id: str
    assignees: list[str]
    resource_id: str | None = None
    team_ids: list[str] = Field(default_factory=list)


class FairnessMetrics(BaseModel):
    """Fairness metrics."""

    stdev: float
    per_person_counts: dict[str, int]


class StabilityMetrics(BaseModel):
    """Stability metrics for change minimization."""

    moves_from_published: int = 0
    affected_persons: int = 0


class SolverMeta(BaseModel):
    """Solver metadata."""

    name: str
    version: str
    strategy: str


class Violation(BaseModel):
    """A constraint violation."""

    constraint_key: str
    severity: str
    message: str
    entities: list[str] = Field(default_factory=list)


class Violations(BaseModel):
    """Collection of violations."""

    hard: list[Violation] = Field(default_factory=list)
    soft: list[Violation] = Field(default_factory=list)


class Metrics(BaseModel):
    """Solution metrics."""

    solve_ms: float
    hard_violations: int
    soft_score: float
    fairness: FairnessMetrics
    stability: StabilityMetrics
    health_score: float


class SolutionMeta(BaseModel):
    """Metadata for a solution."""

    generated_at: datetime
    range_start: date
    range_end: date
    mode: str
    change_min: bool
    solver: SolverMeta


class SolutionBundle(BaseModel):
    """Complete solution bundle."""

    meta: SolutionMeta
    assignments: list[Assignment]
    metrics: Metrics
    violations: Violations


class Patch(BaseModel):
    """A patch for simulation."""

    add_people: list[Person] = Field(default_factory=list)
    remove_people: list[str] = Field(default_factory=list)
    add_events: list[Event] = Field(default_factory=list)
    remove_events: list[str] = Field(default_factory=list)
    update_availability: list[Availability] = Field(default_factory=list)
