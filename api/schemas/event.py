"""Event schemas."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EventBase(BaseModel):
    """Base event schema."""

    type: str = Field(..., description="Event type (match, shift, meeting)")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    resource_id: Optional[str] = Field(None, description="Resource/venue ID")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class EventCreate(EventBase):
    """Schema for creating an event."""

    id: str = Field(..., description="Unique event ID", min_length=1)
    org_id: str = Field(..., description="Organization ID")
    team_ids: Optional[List[str]] = Field(default_factory=list, description="List of team IDs")


class EventUpdate(BaseModel):
    """Schema for updating an event."""

    type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    resource_id: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class EventResponse(EventBase):
    """Schema for event response."""

    id: str
    org_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventList(BaseModel):
    """Schema for listing events."""

    events: List[EventResponse]
    total: int
