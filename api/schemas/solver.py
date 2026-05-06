"""Solver schemas."""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SolveRequest(BaseModel):
    """Schema for solve request."""

    org_id: str = Field(..., description="Organization ID")
    from_date: date = Field(..., description="Start date for schedule")
    to_date: date = Field(..., description="End date for schedule")
    mode: str = Field("strict", description="Solve mode: strict or relaxed")
    change_min: bool = Field(False, description="Enable change minimization")


class ViolationInfo(BaseModel):
    """Schema for constraint violation."""

    constraint_key: str
    message: str
    entities: list[str]
    severity: str


class FairnessMetrics(BaseModel):
    """Schema for fairness metrics."""

    stdev: float
    per_person_counts: dict[str, int]


class StabilityMetrics(BaseModel):
    """Stability metrics relative to the org's currently-published solution."""

    moves_from_published: int = 0
    affected_persons: int = 0


class SolutionMetrics(BaseModel):
    """Schema for solution metrics."""

    hard_violations: int
    soft_score: float
    health_score: float
    solve_ms: float
    fairness: FairnessMetrics
    stability: StabilityMetrics = Field(default_factory=StabilityMetrics)


class AssignmentInfo(BaseModel):
    """Schema for assignment information."""

    event_id: str
    person_id: str
    event_start: datetime
    event_type: str


class SolveResponse(BaseModel):
    """Schema for solve response."""

    solution_id: int = Field(..., description="Database ID of saved solution")
    metrics: SolutionMetrics
    assignment_count: int
    violations: list[ViolationInfo]
    message: str


class SolutionResponse(BaseModel):
    """Schema for solution response."""

    id: int
    org_id: str
    solve_ms: float
    hard_violations: int
    model_config = ConfigDict(from_attributes=True)

    soft_score: float
    health_score: float
    metrics: dict[str, Any] | None
    created_at: datetime
    is_published: bool = False
    published_at: datetime | None = None
    assignment_count: int = 0


from api.schemas.common import ListResponse

SolutionList = ListResponse[SolutionResponse]


class ExportFormat(BaseModel):
    """Schema for export format request."""

    format: str = Field(..., description="Export format: json, csv, pdf, or ics")
    scope: str = Field("org", description="Export scope: org, person:{id}, or team:{id}")


class AssignmentChange(BaseModel):
    """One added/removed assignment in a diff."""

    event_id: str
    person_id: str
    role: str | None = None


class SolutionDiffResponse(BaseModel):
    """Diff between two solutions in the same org."""

    solution_a_id: int
    solution_b_id: int
    added: list[AssignmentChange]
    removed: list[AssignmentChange]
    unchanged_count: int
    affected_persons: list[str]
    moves: int


class FairnessStats(BaseModel):
    """Fairness metrics + histogram of per-person assignment counts."""

    stdev: float
    per_person_counts: dict[str, int]
    histogram: dict[str, int]  # str-keyed for JSON: "count" → num_people


class WorkloadStats(BaseModel):
    """Aggregate workload distribution stats."""

    max_events_per_person: int
    min_events_per_person: int
    median_events_per_person: float
    total_events_assigned: int
    distinct_persons_assigned: int


class SolutionStatsResponse(BaseModel):
    """Stats response for ``GET /solutions/{id}/stats`` (admin only)."""

    solution_id: int
    fairness: FairnessStats
    stability: StabilityMetrics
    workload: WorkloadStats
