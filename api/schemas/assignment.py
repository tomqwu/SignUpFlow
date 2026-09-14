"""Schemas for the volunteer-assignment self-service endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from api.schemas._serializers import BaseResponse


class AssignmentDeclineRequest(BaseModel):
    """Body for POST /assignments/{id}/decline."""

    decline_reason: str = Field(..., min_length=1, max_length=500)
    expected_revision: int | None = Field(None, ge=1)


class AssignmentSwapRequest(BaseModel):
    """Body for POST /assignments/{id}/swap-request."""

    note: str | None = Field(None, max_length=500)
    expected_revision: int | None = Field(None, ge=1)


class AssignmentResponse(BaseResponse):
    """Single-assignment response shape returned by self-service mutations."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: str
    person_id: str
    role: str | None
    status: str
    response_status: str
    responded_by_person_id: str | None
    responded_at: datetime | None
    commitment_revision: int
    response_revision: int | None
    response_current: bool
    decline_reason: str | None
    assigned_at: datetime
