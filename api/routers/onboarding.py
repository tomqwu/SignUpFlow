"""
Onboarding API Router

Endpoints for managing user onboarding progress:
- GET /api/onboarding/progress - Get current user's onboarding state
- PUT /api/onboarding/progress - Update onboarding progress
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import Optional, Dict, List, Any
from pydantic import BaseModel

from api.database import get_db
from api.models import OnboardingProgress, Person
from api.dependencies import get_current_user, get_current_admin_user, verify_org_member
from api.services.onboarding_service import OnboardingService
from api.services.sample_data_generator import (
    generate_sample_data,
    cleanup_sample_data,
    has_sample_data,
    get_sample_data_summary
)

router = APIRouter(tags=["onboarding"])


# Pydantic schemas
class OnboardingProgressResponse(BaseModel):
    """Onboarding progress response schema."""

    id: int
    person_id: str
    org_id: str
    wizard_step_completed: int
    wizard_data: Dict[str, Any]
    checklist_state: Dict[str, bool]
    tutorials_completed: List[str]
    features_unlocked: List[str]
    videos_watched: List[str]
    onboarding_skipped: bool
    checklist_dismissed: Optional[bool] = False
    tutorials_dismissed: Optional[bool] = False

    class Config:
        from_attributes = True


class OnboardingProgressUpdate(BaseModel):
    """Onboarding progress update schema."""

    wizard_step_completed: Optional[int] = None
    wizard_data: Optional[Dict[str, Any]] = None
    checklist_state: Optional[Dict[str, bool]] = None
    tutorials_completed: Optional[List[str]] = None
    features_unlocked: Optional[List[str]] = None
    videos_watched: Optional[List[str]] = None
    onboarding_skipped: Optional[bool] = None
    checklist_dismissed: Optional[bool] = None
    tutorials_dismissed: Optional[bool] = None


@router.get("/onboarding/progress", response_model=OnboardingProgressResponse)
def get_onboarding_progress(
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's onboarding progress.
    """
    service = OnboardingService(db)
    return service.get_progress(current_user.id)


@router.put("/onboarding/progress", response_model=OnboardingProgressResponse)
def update_onboarding_progress(
    update: OnboardingProgressUpdate,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's onboarding progress.
    """
    service = OnboardingService(db)
    return service.update_progress(current_user.id, update.dict(exclude_unset=True))


@router.post("/onboarding/skip")
def skip_onboarding(
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark onboarding as skipped for experienced users.
    """
    service = OnboardingService(db)
    service.skip_onboarding(current_user.id)
    return {"message": "Onboarding skipped successfully"}


@router.post("/onboarding/reset")
def reset_onboarding(
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset onboarding progress.
    """
    service = OnboardingService(db)
    service.reset_onboarding(current_user.id)
    return {"message": "Onboarding progress reset successfully"}


@router.post("/onboarding/sample-data/generate")
def generate_sample_data_endpoint(
    org_id: str,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Generate sample data for exploration (admin only).

    Creates:
    - 5 sample events
    - 3 sample teams
    - 10 sample volunteers

    All data is prefixed with "SAMPLE - " for easy identification.
    """
    verify_org_member(current_admin, org_id)

    # Check if sample data already exists
    if has_sample_data(org_id, db):
        raise HTTPException(
            status_code=409,
            detail="Sample data already exists. Clean up existing sample data first."
        )

    try:
        created_ids = generate_sample_data(org_id, db)
        return {
            "message": "Sample data generated successfully",
            "created": created_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sample data: {str(e)}")


@router.delete("/onboarding/sample-data")
def cleanup_sample_data_endpoint(
    org_id: str,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Remove all sample data (admin only).

    Deletes all entities prefixed with "SAMPLE - ".
    """
    verify_org_member(current_admin, org_id)

    try:
        deleted_counts = cleanup_sample_data(org_id, db)
        return {
            "message": "Sample data cleaned up successfully",
            "deleted": deleted_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup sample data: {str(e)}")


@router.get("/onboarding/sample-data/status")
def get_sample_data_status(
    org_id: str,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get sample data status for organization.

    Returns whether sample data exists and counts.
    """
    verify_org_member(current_user, org_id)

    exists = has_sample_data(org_id, db)
    summary = get_sample_data_summary(org_id, db) if exists else {}

    return {
        "has_sample_data": exists,
        "summary": summary
    }
