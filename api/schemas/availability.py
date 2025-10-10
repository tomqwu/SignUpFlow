"""Availability schemas."""

from typing import Optional
from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class AvailabilityCreate(BaseModel):
    """Schema for creating availability."""

    person_id: str = Field(..., description="Person ID")


class AvailabilityUpdate(BaseModel):
    """Schema for updating availability."""

    rrule: Optional[str] = None


class AvailabilityResponse(BaseModel):
    """Schema for availability response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    person_id: str


class TimeOffCreate(BaseModel):
    """Schema for creating time-off period."""

    start_date: date = Field(..., description="Start date of time-off")
    end_date: date = Field(..., description="End date of time-off")
    reason: Optional[str] = Field(None, description="Reason for time-off")


class TimeOffResponse(BaseModel):
    """Schema for time-off response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None
