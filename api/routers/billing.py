"""Billing and subscription management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from api.database import get_db
from api.dependencies import get_current_user
from api.models import Person, Organization

router = APIRouter(tags=["billing"])


@router.get("/billing/subscription")
def get_subscription(
    org_id: str = Query(..., description="Organization ID"),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current subscription details for organization.

    Returns subscription tier, usage metrics, and billing information.
    """
    # Placeholder - will be implemented in Phase 3
    return {
        "org_id": org_id,
        "plan_tier": "free",
        "status": "active",
        "message": "Billing system initialization in progress"
    }
