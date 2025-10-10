"""Organization schemas."""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class OrganizationBase(BaseModel):
    """Base organization schema."""

    name: str = Field(..., description="Organization name")
    region: Optional[str] = Field(None, description="Region code (e.g., CA-ON, US-CA)")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration settings")


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""

    id: str = Field(..., description="Unique organization ID", min_length=1)


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""

    name: Optional[str] = None
    region: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class OrganizationList(BaseModel):
    """Schema for listing organizations."""

    organizations: list[OrganizationResponse]
    total: int
