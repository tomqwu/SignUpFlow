"""Team schemas."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    """Base team schema."""

    name: str = Field(..., description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class TeamCreate(TeamBase):
    """Schema for creating a team."""

    id: str = Field(..., description="Unique team ID", min_length=1)
    org_id: str = Field(..., description="Organization ID")
    member_ids: Optional[List[str]] = Field(default_factory=list, description="List of member person IDs")


class TeamUpdate(BaseModel):
    """Schema for updating a team."""

    name: Optional[str] = None
    description: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class TeamMemberAdd(BaseModel):
    """Schema for adding team members."""

    person_ids: List[str] = Field(..., description="List of person IDs to add")


class TeamMemberRemove(BaseModel):
    """Schema for removing team members."""

    person_ids: List[str] = Field(..., description="List of person IDs to remove")


class TeamResponse(TeamBase):
    """Schema for team response."""

    id: str
    org_id: str
    created_at: datetime
    updated_at: datetime
    member_count: int = Field(0, description="Number of members")

    class Config:
        from_attributes = True


class TeamList(BaseModel):
    """Schema for listing teams."""

    teams: List[TeamResponse]
    total: int
