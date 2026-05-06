"""Resource schemas (venues, rooms, equipment).

The `Resource` ORM model has been around since the initial schema and the solver
already consumes it (see api/routers/solver.py loading resources at /solve time).
This file finally exposes it via the API.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from api.schemas._serializers import BaseResponse
from api.schemas.common import ListResponse


class ResourceBase(BaseModel):
    """Common fields for create + response."""

    type: str = Field(
        ..., min_length=1, max_length=64, description="e.g. 'room', 'venue', 'equipment'"
    )
    location: str = Field(..., min_length=1, max_length=255)
    capacity: int | None = Field(None, ge=0, description="Optional headcount cap; null = unbounded")
    extra_data: dict[str, Any] | None = Field(None, description="Free-form metadata")


class ResourceCreate(ResourceBase):
    id: str = Field(..., min_length=1, max_length=64, description="Caller-supplied unique id")
    org_id: str = Field(..., description="Owning organization")


class ResourceUpdate(BaseModel):
    """All fields optional (PATCH-style update)."""

    type: str | None = Field(None, min_length=1, max_length=64)
    location: str | None = Field(None, min_length=1, max_length=255)
    capacity: int | None = Field(None, ge=0)
    extra_data: dict[str, Any] | None = None


class ResourceResponse(BaseResponse, ResourceBase):
    id: str
    org_id: str
    created_at: datetime
    updated_at: datetime


ResourceList = ListResponse[ResourceResponse]
