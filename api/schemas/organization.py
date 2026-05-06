"""Organization schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from api.schemas._serializers import BaseResponse


class OrganizationBase(BaseModel):
    """Base organization schema."""

    name: str = Field(..., description="Organization name")
    region: str | None = Field(None, description="Region code (e.g., CA-ON, US-CA)")
    config: dict[str, Any] | None = Field(None, description="Configuration settings")


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""

    id: str = Field(..., description="Unique organization ID", min_length=1)


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""

    name: str | None = None
    region: str | None = None
    config: dict[str, Any] | None = None


class OrganizationResponse(BaseResponse, OrganizationBase):
    """Schema for organization response."""

    id: str
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None = None
    deletion_scheduled_at: datetime | None = None
    data_retention_until: datetime | None = None


from api.schemas.common import ListResponse

OrganizationList = ListResponse[OrganizationResponse]
