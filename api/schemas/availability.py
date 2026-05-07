"""Availability schemas."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AvailabilityCreate(BaseModel):
    """Schema for creating availability."""

    person_id: str = Field(..., description="Person ID")


class AvailabilityUpdate(BaseModel):
    """Schema for updating availability."""

    rrule: str | None = None


class AvailabilityResponse(BaseModel):
    """Schema for availability response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    person_id: str


class TimeOffCreate(BaseModel):
    """Schema for creating time-off period."""

    start_date: date = Field(..., description="Start date of time-off")
    end_date: date = Field(..., description="End date of time-off")
    reason: str | None = Field(None, description="Reason for time-off")


class TimeOffResponse(BaseModel):
    """Schema for time-off response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    start_date: date
    end_date: date
    reason: str | None = None


class AvailabilityExceptionCreate(BaseModel):
    """Schema for adding a single-date availability exception."""

    exception_date: date = Field(..., description="Single date the volunteer is blocked")


class AvailabilityExceptionResponse(BaseModel):
    """Schema for an availability exception row."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    exception_date: date


class AvailabilityRruleResponse(BaseModel):
    """Schema for the single rrule string per person."""

    rrule: str | None


class AvailabilityRruleUpdate(BaseModel):
    """Schema for setting the rrule string."""

    rrule: str = Field(..., min_length=1, description="iCalendar RRULE expression")
