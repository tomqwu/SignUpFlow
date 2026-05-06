"""Team schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TeamBase(BaseModel):
    """Base team schema."""

    name: str = Field(..., description="Team name")
    description: str | None = Field(None, description="Team description")
    extra_data: dict[str, Any] | None = Field(None, description="Additional data")


class TeamCreate(TeamBase):
    """Schema for creating a team."""

    id: str = Field(..., description="Unique team ID", min_length=1)
    org_id: str = Field(..., description="Organization ID")
    member_ids: list[str] | None = Field(
        default_factory=list, description="List of member person IDs"
    )


class TeamUpdate(BaseModel):
    """Schema for updating a team."""

    name: str | None = None
    description: str | None = None
    extra_data: dict[str, Any] | None = None


class TeamMemberAdd(BaseModel):
    """Schema for adding team members."""

    person_ids: list[str] = Field(..., description="List of person IDs to add")


class TeamMemberRemove(BaseModel):
    """Schema for removing team members."""

    person_ids: list[str] = Field(..., description="List of person IDs to remove")


class TeamResponse(TeamBase):
    """Schema for team response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    created_at: datetime
    updated_at: datetime
    member_count: int = Field(0, description="Number of members")


class TeamList(BaseModel):
    """Schema for listing teams."""

    teams: list[TeamResponse]
    total: int
