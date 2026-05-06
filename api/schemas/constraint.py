"""Constraint schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConstraintBase(BaseModel):
    """Base constraint schema."""

    key: str = Field(..., description="Constraint key/identifier")
    type: str = Field(..., description="Constraint type: hard or soft")
    weight: int | None = Field(None, description="Weight for soft constraints")
    predicate: str = Field(..., description="Constraint predicate/rule")
    params: dict[str, Any] | None = Field(None, description="Constraint parameters")


class ConstraintCreate(ConstraintBase):
    """Schema for creating a constraint."""

    org_id: str = Field(..., description="Organization ID")


class ConstraintUpdate(BaseModel):
    """Schema for updating a constraint."""

    type: str | None = None
    weight: int | None = None
    predicate: str | None = None
    params: dict[str, Any] | None = None


class ConstraintResponse(ConstraintBase):
    """Schema for constraint response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: str
    created_at: datetime
    updated_at: datetime


class ConstraintList(BaseModel):
    """Schema for listing constraints."""

    constraints: list[ConstraintResponse]
    total: int
