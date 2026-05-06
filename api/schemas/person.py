"""Person schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PersonBase(BaseModel):
    """Base person schema."""

    name: str = Field(..., description="Person's full name")
    email: EmailStr | None = Field(None, description="Email address")
    roles: list[str] | None = Field(default_factory=list, description="List of roles")
    timezone: str = Field(default="UTC", description="User's timezone preference")
    language: str = Field(default="en", description="User's language preference (ISO 639-1 code)")
    extra_data: dict[str, Any] | None = Field(None, description="Additional data")


class PersonCreate(PersonBase):
    """Schema for creating a person."""

    id: str = Field(..., description="Unique person ID", min_length=1)
    org_id: str = Field(..., description="Organization ID")


class PersonUpdate(BaseModel):
    """Schema for updating a person."""

    name: str | None = None
    email: EmailStr | None = None
    roles: list[str] | None = None
    timezone: str | None = None
    language: str | None = None
    extra_data: dict[str, Any] | None = None


class PersonResponse(PersonBase):
    """Schema for person response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    created_at: datetime
    updated_at: datetime


class PersonList(BaseModel):
    """Schema for listing people."""

    people: list[PersonResponse]
    total: int
