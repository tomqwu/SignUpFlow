"""Availability router - manage person availability and time-off."""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas.availability import (
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityResponse,
    TimeOffCreate,
    TimeOffResponse,
)
from api.models import (
    Availability,
    VacationPeriod,
    Person,
)

router = APIRouter(prefix="/availability", tags=["availability"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_availability(person_id: str, db: Session = Depends(get_db)):
    """Create availability record for a person."""
    # Verify person exists
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Person '{person_id}' not found",
        )

    # Check if availability already exists
    existing = db.query(Availability).filter(Availability.person_id == person_id).first()
    if existing:
        return {"message": "Availability already exists", "availability_id": existing.id}

    # Create availability
    availability = Availability(
        person_id=person_id,
        rrule=None,
        extra_data={},
    )
    db.add(availability)
    db.commit()
    db.refresh(availability)

    return {"availability_id": availability.id, "person_id": person_id}


@router.get("/{person_id}/timeoff")
def get_timeoff(person_id: str, db: Session = Depends(get_db)):
    """Get all time-off periods for a person."""
    # Get or create availability
    availability = db.query(Availability).filter(Availability.person_id == person_id).first()

    if not availability:
        return {"timeoff": [], "total": 0}

    # Get vacation periods
    vacations = (
        db.query(VacationPeriod)
        .filter(VacationPeriod.availability_id == availability.id)
        .all()
    )

    return {
        "timeoff": [
            {
                "id": v.id,
                "start_date": v.start_date.isoformat(),
                "end_date": v.end_date.isoformat(),
                "reason": v.reason,
            }
            for v in vacations
        ],
        "total": len(vacations),
    }


@router.post("/{person_id}/timeoff", status_code=status.HTTP_201_CREATED)
def add_timeoff(
    person_id: str,
    timeoff_data: TimeOffCreate,
    db: Session = Depends(get_db),
):
    """Add a time-off period for a person."""
    # Get or create availability
    availability = db.query(Availability).filter(Availability.person_id == person_id).first()

    if not availability:
        # Create availability if it doesn't exist
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person '{person_id}' not found",
            )

        availability = Availability(person_id=person_id, rrule=None, extra_data={})
        db.add(availability)
        db.flush()

    # Validate dates
    if timeoff_data.end_date < timeoff_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Check for overlapping vacation periods
    overlapping = db.query(VacationPeriod).filter(
        VacationPeriod.availability_id == availability.id,
        VacationPeriod.start_date <= timeoff_data.end_date,
        VacationPeriod.end_date >= timeoff_data.start_date
    ).first()

    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Time-off period overlaps with existing period ({overlapping.start_date} to {overlapping.end_date})",
        )

    # Create vacation period
    vacation = VacationPeriod(
        availability_id=availability.id,
        start_date=timeoff_data.start_date,
        end_date=timeoff_data.end_date,
        reason=timeoff_data.reason,
    )
    db.add(vacation)
    db.commit()
    db.refresh(vacation)

    return {
        "id": vacation.id,
        "start_date": vacation.start_date.isoformat(),
        "end_date": vacation.end_date.isoformat(),
        "reason": vacation.reason,
        "message": "Time-off period added successfully",
    }


@router.patch("/{person_id}/timeoff/{timeoff_id}")
def update_timeoff(
    person_id: str,
    timeoff_id: int,
    timeoff_data: TimeOffCreate,
    db: Session = Depends(get_db),
):
    """Update a time-off period."""
    # Get availability
    availability = db.query(Availability).filter(Availability.person_id == person_id).first()

    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No availability found for person '{person_id}'",
        )

    # Get vacation period
    vacation = (
        db.query(VacationPeriod)
        .filter(
            VacationPeriod.id == timeoff_id,
            VacationPeriod.availability_id == availability.id,
        )
        .first()
    )

    if not vacation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Time-off period {timeoff_id} not found",
        )

    # Validate dates
    if timeoff_data.end_date < timeoff_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Update vacation period
    vacation.start_date = timeoff_data.start_date
    vacation.end_date = timeoff_data.end_date
    vacation.reason = timeoff_data.reason
    db.commit()
    db.refresh(vacation)

    return {
        "id": vacation.id,
        "start_date": vacation.start_date.isoformat(),
        "end_date": vacation.end_date.isoformat(),
        "reason": vacation.reason,
        "message": "Time-off period updated successfully",
    }


@router.delete("/{person_id}/timeoff/{timeoff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timeoff(person_id: str, timeoff_id: int, db: Session = Depends(get_db)):
    """Delete a time-off period."""
    # Get availability
    availability = db.query(Availability).filter(Availability.person_id == person_id).first()

    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No availability found for person '{person_id}'",
        )

    # Get and delete vacation period
    vacation = (
        db.query(VacationPeriod)
        .filter(
            VacationPeriod.id == timeoff_id,
            VacationPeriod.availability_id == availability.id,
        )
        .first()
    )

    if not vacation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Time-off period {timeoff_id} not found",
        )

    db.delete(vacation)
    db.commit()
    return None
