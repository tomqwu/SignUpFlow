"""Event schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    """Base event schema."""

    type: str = Field(..., description="Event type (match, shift, meeting)")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    resource_id: str | None = Field(None, description="Resource/venue ID")
    extra_data: dict[str, Any] | None = Field(None, description="Additional data")


class EventCreate(EventBase):
    """Schema for creating an event."""

    id: str = Field(..., description="Unique event ID", min_length=1)
    org_id: str = Field(..., description="Organization ID")
    team_ids: list[str] | None = Field(default_factory=list, description="List of team IDs")


class EventUpdate(BaseModel):
    """Schema for updating an event."""

    type: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    resource_id: str | None = None
    extra_data: dict[str, Any] | None = None


class EventResponse(EventBase):
    """Schema for event response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    created_at: datetime
    updated_at: datetime


class EventList(BaseModel):
    """Schema for listing events."""

    events: list[EventResponse]
    total: int
