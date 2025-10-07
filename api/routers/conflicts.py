"""Conflict detection router - check for scheduling conflicts."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from api.database import get_db
from api.schemas.conflicts import (
    ConflictCheckRequest,
    ConflictCheckResponse,
    ConflictType,
)
from api.models import (
    Person,
    Event,
    Assignment,
    Availability,
    VacationPeriod,
)

router = APIRouter(prefix="/conflicts", tags=["conflicts"])


def check_time_overlap(
    start1: datetime, end1: datetime, start2: datetime, end2: datetime
) -> bool:
    """Check if two time periods overlap."""
    return start1 < end2 and start2 < end1


@router.post("/check", response_model=ConflictCheckResponse)
def check_conflicts(
    request: ConflictCheckRequest,
    db: Session = Depends(get_db),
):
    """Check for scheduling conflicts before assigning a person to an event.

    Detects:
    - Already assigned to this event
    - Time-off periods overlapping with event
    - Double-booked (assigned to another event at the same time)
    """
    conflicts: List[ConflictType] = []

    # Verify person exists
    person = db.query(Person).filter(Person.id == request.person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Person '{request.person_id}' not found",
        )

    # Verify event exists
    event = db.query(Event).filter(Event.id == request.event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event '{request.event_id}' not found",
        )

    # Check 1: Already assigned to this event?
    existing_assignment = (
        db.query(Assignment)
        .filter(
            Assignment.person_id == request.person_id,
            Assignment.event_id == request.event_id,
        )
        .first()
    )
    if existing_assignment:
        conflicts.append(
            ConflictType(
                type="already_assigned",
                message=f"{person.name} is already assigned to this event",
                conflicting_event_id=event.id,
                start_time=event.start_time,
                end_time=event.end_time,
            )
        )

    # Check 2: Time-off conflicts
    availability = (
        db.query(Availability).filter(Availability.person_id == request.person_id).first()
    )
    if availability:
        time_off_periods = (
            db.query(VacationPeriod)
            .filter(VacationPeriod.availability_id == availability.id)
            .all()
        )

        for vacation in time_off_periods:
            # Convert date to datetime for comparison
            vacation_start = datetime.combine(vacation.start_date, datetime.min.time())
            vacation_end = datetime.combine(vacation.end_date, datetime.max.time())

            if check_time_overlap(
                event.start_time, event.end_time, vacation_start, vacation_end
            ):
                conflicts.append(
                    ConflictType(
                        type="time_off",
                        message=f"{person.name} has time-off from {vacation.start_date} to {vacation.end_date}",
                        start_time=vacation_start,
                        end_time=vacation_end,
                    )
                )

    # Check 3: Double-booked (assigned to another overlapping event)
    other_assignments = (
        db.query(Assignment)
        .filter(Assignment.person_id == request.person_id)
        .all()
    )

    for assignment in other_assignments:
        if assignment.event_id == request.event_id:
            continue  # Skip the event we're checking (already handled above)

        other_event = db.query(Event).filter(Event.id == assignment.event_id).first()
        if other_event and check_time_overlap(
            event.start_time, event.end_time, other_event.start_time, other_event.end_time
        ):
            conflicts.append(
                ConflictType(
                    type="double_booked",
                    message=f"{person.name} is already assigned to '{other_event.type}' ({other_event.start_time.strftime('%Y-%m-%d %H:%M')} - {other_event.end_time.strftime('%H:%M')})",
                    conflicting_event_id=other_event.id,
                    start_time=other_event.start_time,
                    end_time=other_event.end_time,
                )
            )

    # Determine if assignment should be allowed
    # Block if already assigned or has time-off
    # Warn but allow if double-booked (might be intentional)
    blocking_conflict_types = {"already_assigned", "time_off"}
    has_blocking_conflicts = any(c.type in blocking_conflict_types for c in conflicts)

    return ConflictCheckResponse(
        has_conflicts=len(conflicts) > 0,
        conflicts=conflicts,
        can_assign=not has_blocking_conflicts,
    )
