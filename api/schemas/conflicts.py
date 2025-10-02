"""Conflict detection schemas."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ConflictCheckRequest(BaseModel):
    """Request schema for checking conflicts."""

    person_id: str = Field(..., description="Person ID to check")
    event_id: str = Field(..., description="Event ID to assign to")


class ConflictType(BaseModel):
    """A detected scheduling conflict."""

    type: str = Field(
        ..., description="Conflict type: already_assigned, time_off, double_booked"
    )
    message: str = Field(..., description="Human-readable conflict message")
    conflicting_event_id: Optional[str] = Field(
        None, description="ID of conflicting event if applicable"
    )
    start_time: Optional[datetime] = Field(None, description="Conflict start time")
    end_time: Optional[datetime] = Field(None, description="Conflict end time")


class ConflictCheckResponse(BaseModel):
    """Response schema for conflict check."""

    has_conflicts: bool = Field(..., description="Whether conflicts were detected")
    conflicts: List[ConflictType] = Field(
        default_factory=list, description="List of detected conflicts"
    )
    can_assign: bool = Field(
        ..., description="Whether assignment should be allowed despite conflicts"
    )
