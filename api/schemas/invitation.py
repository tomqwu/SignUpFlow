"""Invitation schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InvitationCreate(BaseModel):
    """Schema for creating an invitation."""

    email: EmailStr = Field(..., description="Email address of the invitee")
    name: str = Field(..., description="Full name of the invitee", min_length=1)
    roles: list[str] = Field(..., description="Roles to assign (e.g., ['volunteer', 'admin'])")


class InvitationResponse(BaseModel):
    """Schema for invitation response."""

    id: str
    org_id: str
    email: str
    name: str
    roles: list[str]
    invited_by: str
    model_config = ConfigDict(from_attributes=True)

    token: str
    status: str  # pending, accepted, expired, cancelled
    expires_at: datetime
    created_at: datetime
    accepted_at: datetime | None = None


class InvitationList(BaseModel):
    """Schema for listing invitations."""

    invitations: list[InvitationResponse]
    total: int


class InvitationVerify(BaseModel):
    """Schema for verifying an invitation token."""

    valid: bool
    invitation: InvitationResponse | None = None
    message: str | None = None


class InvitationAccept(BaseModel):
    """Schema for accepting an invitation."""

    password: str = Field(
        ..., min_length=6, description="Password for the new account (min 6 characters)"
    )
    timezone: str = Field(default="UTC", description="User's timezone preference")


class InvitationAcceptResponse(BaseModel):
    """Schema for invitation acceptance response."""

    person_id: str
    org_id: str
    name: str
    email: str
    roles: list[str]
    timezone: str
    token: str  # Auth token for immediate login
    message: str
