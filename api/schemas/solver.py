"""Solver schemas."""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field


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
    entities: List[str]
    severity: str


class FairnessMetrics(BaseModel):
    """Schema for fairness metrics."""

    stdev: float
    per_person_counts: Dict[str, int]


class SolutionMetrics(BaseModel):
    """Schema for solution metrics."""

    hard_violations: int
    soft_score: float
    health_score: float
    solve_ms: float
    fairness: FairnessMetrics


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
    violations: List[ViolationInfo]
    message: str


class SolutionResponse(BaseModel):
    """Schema for solution response."""

    id: int
    org_id: str
    solve_ms: float
    hard_violations: int
    soft_score: float
    health_score: float
    metrics: Optional[Dict[str, Any]]
    created_at: datetime
    assignment_count: int = 0

    class Config:
        from_attributes = True


class SolutionList(BaseModel):
    """Schema for listing solutions."""

    solutions: List[SolutionResponse]
    total: int


class ExportFormat(BaseModel):
    """Schema for export format request."""

    format: str = Field(..., description="Export format: json, csv, or ics")
    scope: str = Field("org", description="Export scope: org, person:{id}, or team:{id}")
