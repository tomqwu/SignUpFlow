"""Constraint schemas."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ConstraintBase(BaseModel):
    """Base constraint schema."""

    key: str = Field(..., description="Constraint key/identifier")
    type: str = Field(..., description="Constraint type: hard or soft")
    weight: Optional[int] = Field(None, description="Weight for soft constraints")
    predicate: str = Field(..., description="Constraint predicate/rule")
    params: Optional[Dict[str, Any]] = Field(None, description="Constraint parameters")


class ConstraintCreate(ConstraintBase):
    """Schema for creating a constraint."""

    org_id: str = Field(..., description="Organization ID")


class ConstraintUpdate(BaseModel):
    """Schema for updating a constraint."""

    type: Optional[str] = None
    weight: Optional[int] = None
    predicate: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class ConstraintResponse(ConstraintBase):
    """Schema for constraint response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: str
    created_at: datetime
    updated_at: datetime


class ConstraintList(BaseModel):
    """Schema for listing constraints."""

    constraints: List[ConstraintResponse]
    total: int
