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
from api.dependencies import get_current_user, verify_admin_access, verify_org_member
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

    Returns onboarding state including:
    - Wizard step completion (0-4)
    - Checklist item states
    - Completed tutorials
    - Unlocked features
    - Skip/dismiss flags
    """
    # Get or create onboarding progress for user
    progress = db.query(OnboardingProgress).filter(
        OnboardingProgress.person_id == current_user.id
    ).first()

    if not progress:
        # Create initial progress record
        progress = OnboardingProgress(
            person_id=current_user.id,
            org_id=current_user.org_id,
            wizard_step_completed=0,
            wizard_data={},
            checklist_state={},
            tutorials_completed=[],
            features_unlocked=[],
            videos_watched=[],
            onboarding_skipped=False,
            checklist_dismissed=False,
            tutorials_dismissed=False
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)

    return progress


@router.put("/onboarding/progress", response_model=OnboardingProgressResponse)
def update_onboarding_progress(
    update: OnboardingProgressUpdate,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's onboarding progress.

    Supports partial updates - only provided fields will be updated.

    Fields:
    - wizard_step_completed: 0-4 (0=not started, 4=completed)
    - wizard_data: Free-form data from wizard (org, event, team, invitations)
    - checklist_state: Dict of checklist items {"complete_profile": True, ...}
    - tutorials_completed: List of completed tutorial IDs
    - features_unlocked: List of unlocked feature IDs
    - onboarding_skipped: Whether user skipped onboarding
    - checklist_dismissed: Whether checklist widget was dismissed
    - tutorials_dismissed: Whether all tutorials were dismissed
    """
    # Get existing progress or create new
    progress = db.query(OnboardingProgress).filter(
        OnboardingProgress.person_id == current_user.id
    ).first()

    if not progress:
        # Create new progress record
        progress = OnboardingProgress(
            person_id=current_user.id,
            org_id=current_user.org_id,
            wizard_step_completed=0,
            wizard_data={},
            checklist_state={},
            tutorials_completed=[],
            features_unlocked=[],
            videos_watched=[],
            onboarding_skipped=False,
            checklist_dismissed=False,
            tutorials_dismissed=False
        )
        db.add(progress)

    # Update fields (only if provided in request)
    if update.wizard_step_completed is not None:
        # Validate wizard step (0-4)
        if not 0 <= update.wizard_step_completed <= 4:
            raise HTTPException(
                status_code=422,
                detail="wizard_step_completed must be between 0 and 4"
            )
        progress.wizard_step_completed = update.wizard_step_completed

    if update.wizard_data is not None:
        # Store wizard form data for resume functionality
        progress.wizard_data = update.wizard_data
        flag_modified(progress, "wizard_data")

    if update.checklist_state is not None:
        # Merge with existing checklist state
        current_state = progress.checklist_state or {}
        current_state.update(update.checklist_state)
        progress.checklist_state = current_state
        # Flag as modified so SQLAlchemy detects the change
        flag_modified(progress, "checklist_state")

    if update.tutorials_completed is not None:
        progress.tutorials_completed = update.tutorials_completed

    if update.features_unlocked is not None:
        progress.features_unlocked = update.features_unlocked

    if update.videos_watched is not None:
        progress.videos_watched = update.videos_watched

    if update.onboarding_skipped is not None:
        progress.onboarding_skipped = update.onboarding_skipped

    if update.checklist_dismissed is not None:
        progress.checklist_dismissed = update.checklist_dismissed

    if update.tutorials_dismissed is not None:
        progress.tutorials_dismissed = update.tutorials_dismissed

    db.commit()
    db.refresh(progress)

    return progress


@router.post("/onboarding/skip")
def skip_onboarding(
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark onboarding as skipped for experienced users.

    Sets wizard_step_completed to 4 (completed) and onboarding_skipped flag.
    """
    progress = db.query(OnboardingProgress).filter(
        OnboardingProgress.person_id == current_user.id
    ).first()

    if not progress:
        progress = OnboardingProgress(
            person_id=current_user.id,
            org_id=current_user.org_id,
            wizard_step_completed=4,  # Mark as completed
            checklist_state={},
            tutorials_completed=[],
            features_unlocked=[],
            onboarding_skipped=True
        )
        db.add(progress)
    else:
        progress.wizard_step_completed = 4
        progress.onboarding_skipped = True

    db.commit()
    db.refresh(progress)

    return {"message": "Onboarding skipped successfully"}


@router.post("/onboarding/reset")
def reset_onboarding(
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset onboarding progress (for testing or re-enabling).

    Clears all progress and allows user to go through onboarding again.
    """
    progress = db.query(OnboardingProgress).filter(
        OnboardingProgress.person_id == current_user.id
    ).first()

    if progress:
        progress.wizard_step_completed = 0
        progress.checklist_state = {}
        progress.tutorials_completed = []
        progress.features_unlocked = []
        progress.onboarding_skipped = False

        db.commit()
        db.refresh(progress)

    return {"message": "Onboarding progress reset successfully"}


@router.post("/onboarding/sample-data/generate")
def generate_sample_data_endpoint(
    org_id: str,
    admin: Person = Depends(verify_admin_access),
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
    verify_org_member(admin, org_id)

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
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """
    Remove all sample data (admin only).

    Deletes all entities prefixed with "SAMPLE - ".
    """
    verify_org_member(admin, org_id)

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
