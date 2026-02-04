"""
API router for recurring events management.

Provides REST API endpoints for:
- Creating recurring event series
- Listing and retrieving series
- Previewing occurrences before saving
- Managing series (update template, delete)
- Editing single occurrences vs entire series
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time
from pydantic import BaseModel, Field, ConfigDict

from api.database import get_db
from api.dependencies import get_current_user, get_current_admin_user, verify_org_member
from api.models import RecurringSeries, RecurrenceException, Event, Person
from api.services.recurrence_generator import (
    generate_occurrences,
    detect_holiday_conflicts,
    validate_series_duration,
    RecurrenceGenerationError
)
import uuid


router = APIRouter(tags=["recurring-events"])


# ============================================================================
# Pydantic Models for Request/Response
# ============================================================================

class RecurringSeriesCreate(BaseModel):
    """Request model for creating recurring series."""
    title: str = Field(..., min_length=1, max_length=255)
    duration: int = Field(..., gt=0, description="Duration in minutes")
    location: Optional[str] = None
    role_requirements: Optional[dict] = None

    pattern_type: str = Field(..., pattern="^(weekly|biweekly|monthly|custom)$")
    frequency_interval: Optional[int] = Field(None, gt=0)
    selected_days: Optional[List[str]] = None
    weekday_position: Optional[str] = Field(None, pattern="^(first|second|third|fourth|last)$")
    weekday_name: Optional[str] = Field(None, pattern="^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$")

    start_date: date
    start_time: time
    end_condition_type: str = Field(..., pattern="^(date|count|indefinite)$")
    end_date: Optional[date] = None
    occurrence_count: Optional[int] = Field(None, gt=0, le=200)


class RecurringSeriesResponse(BaseModel):
    """Response model for recurring series."""
    id: str
    org_id: str
    created_by: str
    title: str
    duration: int
    location: Optional[str]
    role_requirements: Optional[dict]

    pattern_type: str
    frequency_interval: Optional[int]
    selected_days: Optional[List[str]]
    weekday_position: Optional[str]
    weekday_name: Optional[str]

    start_date: date
    end_condition_type: str
    end_date: Optional[date]
    occurrence_count: Optional[int]

    active: bool
    created_at: datetime
    updated_at: datetime

    # Computed fields
    occurrence_preview_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class OccurrencePreview(BaseModel):
    """Preview of generated occurrences."""
    occurrence_sequence: int
    start_time: datetime
    end_time: datetime
    title: str
    location: Optional[str]
    role_requirements: Optional[dict]
    is_holiday_conflict: bool = False
    holiday_label: Optional[str] = None


class PreviewRequest(BaseModel):
    """Request for previewing occurrences without saving."""
    pattern_type: str
    selected_days: Optional[List[str]] = None
    weekday_position: Optional[str] = None
    weekday_name: Optional[str] = None
    frequency_interval: Optional[int] = None

    start_date: date
    start_time: time
    duration: int
    end_condition_type: str
    end_date: Optional[date] = None
    occurrence_count: Optional[int] = None


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/recurring-series", response_model=RecurringSeriesResponse)
def create_recurring_series(
    request: RecurringSeriesCreate,
    org_id: str = Query(..., description="Organization ID"),
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new recurring event series and generate all occurrences.

    Requires admin access. Creates:
    1. RecurringSeries template
    2. Individual Event occurrences based on pattern
    3. Links occurrences to series

    Returns the created series with occurrence count.
    """
    # Verify admin belongs to organization
    verify_org_member(admin, org_id)

    # Create temporary series object for validation
    temp_series = RecurringSeries(
        id=str(uuid.uuid4()),
        org_id=org_id,
        created_by=admin.id,
        **request.dict(exclude={"start_time"})
    )

    # Validate series duration
    try:
        validate_series_duration(temp_series)
    except RecurrenceGenerationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Generate occurrences
    try:
        occurrences = generate_occurrences(temp_series, request.start_time, db)
    except RecurrenceGenerationError as e:
        raise HTTPException(status_code=422, detail=f"Failed to generate occurrences: {e}")

    if not occurrences:
        raise HTTPException(status_code=422, detail="Pattern generated zero occurrences")

    if len(occurrences) > 200:
        raise HTTPException(
            status_code=422,
            detail=f"Pattern generates {len(occurrences)} occurrences (maximum 200 allowed)"
        )

    # Create recurring series in database
    series = RecurringSeries(
        id=temp_series.id,
        org_id=org_id,
        created_by=admin.id,
        **request.dict(exclude={"start_time"})
    )

    db.add(series)

    # Create event occurrences
    for occ in occurrences:
        event = Event(
            id=f"event_{uuid.uuid4()}",
            org_id=org_id,
            type=series.title,
            start_time=occ["start_time"],
            end_time=occ["end_time"],
            series_id=series.id,
            occurrence_sequence=occ["occurrence_sequence"],
            is_exception=False,
            extra_data={
                "location": occ.get("location"),
                "role_requirements": occ.get("role_requirements")
            }
        )
        db.add(event)

    db.commit()
    db.refresh(series)

    # Add occurrence count to response
    response = RecurringSeriesResponse.from_orm(series)
    response.occurrence_preview_count = len(occurrences)

    return response


@router.get("/recurring-series", response_model=List[RecurringSeriesResponse])
def list_recurring_series(
    org_id: str = Query(..., description="Organization ID"),
    active_only: bool = Query(True, description="Only return active series"),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all recurring series for an organization.

    Returns all series the user has access to (must be in same organization).
    """
    # Verify user belongs to organization
    verify_org_member(current_user, org_id)

    query = db.query(RecurringSeries).filter(RecurringSeries.org_id == org_id)

    if active_only:
        query = query.filter(RecurringSeries.active == True)

    series_list = query.order_by(RecurringSeries.created_at.desc()).all()

    # Add occurrence count for each series
    response_list = []
    for series in series_list:
        response = RecurringSeriesResponse.from_orm(series)

        # Count occurrences
        occurrence_count = db.query(Event).filter(
            Event.series_id == series.id
        ).count()
        response.occurrence_preview_count = occurrence_count

        response_list.append(response)

    return response_list


@router.get("/recurring-series/{series_id}", response_model=RecurringSeriesResponse)
def get_recurring_series(
    series_id: str,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific recurring series by ID.

    Returns series details with occurrence count.
    """
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()

    if not series:
        raise HTTPException(status_code=404, detail="Recurring series not found")

    # Verify user belongs to same organization
    verify_org_member(current_user, series.org_id)

    # Add occurrence count
    response = RecurringSeriesResponse.from_orm(series)
    occurrence_count = db.query(Event).filter(Event.series_id == series.id).count()
    response.occurrence_preview_count = occurrence_count

    return response


@router.get("/recurring-series/{series_id}/occurrences")
def get_series_occurrences(
    series_id: str,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all event occurrences for a recurring series.

    Returns list of Event objects with exception indicators.
    """
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()

    if not series:
        raise HTTPException(status_code=404, detail="Recurring series not found")

    # Verify user belongs to same organization
    verify_org_member(current_user, series.org_id)

    # Get all occurrences for this series
    occurrences = db.query(Event).filter(
        Event.series_id == series_id
    ).order_by(Event.occurrence_sequence).all()

    return {
        "series_id": series_id,
        "series_title": series.title,
        "occurrence_count": len(occurrences),
        "occurrences": [
            {
                "id": occ.id,
                "occurrence_sequence": occ.occurrence_sequence,
                "start_time": occ.start_time,
                "end_time": occ.end_time,
                "is_exception": occ.is_exception,
                "type": occ.type,
                "extra_data": occ.extra_data
            }
            for occ in occurrences
        ]
    }


@router.post("/recurring-series/preview", response_model=List[OccurrencePreview])
def preview_occurrences(
    request: PreviewRequest,
    org_id: str = Query(..., description="Organization ID"),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Preview occurrences for a recurring pattern WITHOUT creating them.

    Used by the UI calendar preview to show occurrences before saving.
    Returns up to 100 occurrences for preview.
    """
    # Verify user belongs to organization
    verify_org_member(current_user, org_id)

    # Create temporary series object for preview
    temp_series = RecurringSeries(
        id="preview",
        org_id=org_id,
        created_by=current_user.id,
        title="Preview",
        duration=request.duration,
        pattern_type=request.pattern_type,
        selected_days=request.selected_days,
        weekday_position=request.weekday_position,
        weekday_name=request.weekday_name,
        frequency_interval=request.frequency_interval,
        start_date=request.start_date,
        end_condition_type=request.end_condition_type,
        end_date=request.end_date,
        occurrence_count=request.occurrence_count
    )

    # Validate series duration
    try:
        validate_series_duration(temp_series)
    except RecurrenceGenerationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Generate occurrences
    try:
        occurrences = generate_occurrences(temp_series, request.start_time, db)
    except RecurrenceGenerationError as e:
        raise HTTPException(status_code=422, detail=f"Failed to generate preview: {e}")

    # Limit preview to 100 occurrences for performance
    occurrences = occurrences[:100]

    # Detect holiday conflicts
    occurrences = detect_holiday_conflicts(occurrences, org_id, db)

    return [OccurrencePreview(**occ) for occ in occurrences]


@router.delete("/recurring-series/{series_id}")
def delete_recurring_series(
    series_id: str,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a recurring series and all its occurrences.

    Requires admin access. Deletes:
    1. All event occurrences linked to series
    2. All exceptions for those occurrences
    3. The series itself

    Warning: This is irreversible!
    """
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()

    if not series:
        raise HTTPException(status_code=404, detail="Recurring series not found")

    # Verify admin belongs to same organization
    verify_org_member(current_admin, series.org_id)

    # Delete all occurrences (cascade will delete exceptions)
    occurrences = db.query(Event).filter(Event.series_id == series_id).all()
    occurrence_count = len(occurrences)

    for occ in occurrences:
        db.delete(occ)

    # Delete series
    db.delete(series)
    db.commit()

    return {
        "message": "Recurring series deleted successfully",
        "series_id": series_id,
        "occurrences_deleted": occurrence_count
    }


@router.put("/recurring-series/{series_id}")
def update_series_template(
    series_id: str,
    title: Optional[str] = None,
    location: Optional[str] = None,
    role_requirements: Optional[dict] = None,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update the series template (affects future occurrences).

    Only updates the template - existing occurrences are NOT changed.
    Use this to modify what future occurrences will look like.

    Note: To modify recurrence pattern, delete and recreate the series.
    """
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).first()

    if not series:
        raise HTTPException(status_code=404, detail="Recurring series not found")

    # Verify admin belongs to same organization
    verify_org_member(current_admin, series.org_id)

    # Update template fields
    if title is not None:
        series.title = title

    if location is not None:
        series.location = location

    if role_requirements is not None:
        series.role_requirements = role_requirements

    series.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(series)

    return RecurringSeriesResponse.from_orm(series)
