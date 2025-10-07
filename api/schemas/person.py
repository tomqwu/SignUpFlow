"""Person schemas."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class PersonBase(BaseModel):
    """Base person schema."""

    name: str = Field(..., description="Person's full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    roles: Optional[List[str]] = Field(default_factory=list, description="List of roles")
    timezone: str = Field(default="UTC", description="User's timezone preference")
    language: str = Field(default="en", description="User's language preference (ISO 639-1 code)")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class PersonCreate(PersonBase):
    """Schema for creating a person."""

    id: str = Field(..., description="Unique person ID", min_length=1)
    org_id: str = Field(..., description="Organization ID")


class PersonUpdate(BaseModel):
    """Schema for updating a person."""

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    roles: Optional[List[str]] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class PersonResponse(PersonBase):
    """Schema for person response."""

    id: str
    org_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PersonList(BaseModel):
    """Schema for listing people."""

    people: List[PersonResponse]
    total: int
