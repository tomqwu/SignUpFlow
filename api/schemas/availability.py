"""Availability schemas."""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field


class AvailabilityCreate(BaseModel):
    """Schema for creating availability."""

    person_id: str = Field(..., description="Person ID")


class AvailabilityUpdate(BaseModel):
    """Schema for updating availability."""

    rrule: Optional[str] = None


class AvailabilityResponse(BaseModel):
    """Schema for availability response."""

    id: int
    person_id: str

    class Config:
        from_attributes = True


class TimeOffCreate(BaseModel):
    """Schema for creating time-off period."""

    start_date: date = Field(..., description="Start date of time-off")
    end_date: date = Field(..., description="End date of time-off")
    reason: Optional[str] = Field(None, description="Reason for time-off")


class TimeOffResponse(BaseModel):
    """Schema for time-off response."""

    id: int
    start_date: date
    end_date: date

    class Config:
        from_attributes = True
