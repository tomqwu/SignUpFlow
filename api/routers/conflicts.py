"""Conflict detection router - check for scheduling conflicts."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_admin_user, verify_org_member
from api.models import (
    Assignment,
    Availability,
    Event,
    Person,
    VacationPeriod,
)
from api.schemas.common import ListResponse, PaginationParams, get_pagination_params
from api.schemas.conflicts import (
    ConflictCheckRequest,
    ConflictCheckResponse,
    ConflictType,
)

router = APIRouter(prefix="/conflicts", tags=["conflicts"])


def check_time_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
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
    conflicts: list[ConflictType] = []

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
            db.query(VacationPeriod).filter(VacationPeriod.availability_id == availability.id).all()
        )

        for vacation in time_off_periods:
            # Convert date to datetime for comparison
            vacation_start = datetime.combine(vacation.start_date, datetime.min.time())
            vacation_end = datetime.combine(vacation.end_date, datetime.max.time())

            if check_time_overlap(event.start_time, event.end_time, vacation_start, vacation_end):
                conflicts.append(
                    ConflictType(
                        type="time_off",
                        message=f"{person.name} has time-off from {vacation.start_date} to {vacation.end_date}",
                        start_time=vacation_start,
                        end_time=vacation_end,
                    )
                )

    # Check 3: Double-booked (assigned to another overlapping event)
    other_assignments = db.query(Assignment).filter(Assignment.person_id == request.person_id).all()

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


def _person_conflicts(person: Person, db: Session) -> list[ConflictType]:
    """Detect every conflict on this person's existing assignments.

    Looks at:
    - time-off overlap with each assignment's event
    - double-booked: any pair of assignments whose events overlap

    Does NOT raise `already_assigned` (the assignment exists by definition).
    """
    rows: list[ConflictType] = []

    assignments = db.query(Assignment).filter(Assignment.person_id == person.id).all()
    if not assignments:
        return rows

    # Pre-load events keyed by id
    event_ids = [a.event_id for a in assignments]
    events_by_id: dict[str, Event] = {
        e.id: e for e in db.query(Event).filter(Event.id.in_(event_ids)).all()
    }

    # Time-off overlaps
    availability = db.query(Availability).filter(Availability.person_id == person.id).first()
    if availability:
        vacations = (
            db.query(VacationPeriod).filter(VacationPeriod.availability_id == availability.id).all()
        )
        for assignment in assignments:
            event = events_by_id.get(assignment.event_id)
            if event is None:
                continue
            for vacation in vacations:
                v_start = datetime.combine(vacation.start_date, datetime.min.time())
                v_end = datetime.combine(vacation.end_date, datetime.max.time())
                if check_time_overlap(event.start_time, event.end_time, v_start, v_end):
                    rows.append(
                        ConflictType(
                            type="time_off",
                            message=(
                                f"{person.name} has time-off from {vacation.start_date} "
                                f"to {vacation.end_date} but is assigned to {event.type}"
                            ),
                            conflicting_event_id=event.id,
                            start_time=v_start,
                            end_time=v_end,
                        )
                    )

    # Double-booked: any pair of overlapping assignments for this person
    for i, a in enumerate(assignments):
        ev_a = events_by_id.get(a.event_id)
        if ev_a is None:
            continue
        for b in assignments[i + 1 :]:
            ev_b = events_by_id.get(b.event_id)
            if ev_b is None:
                continue
            if check_time_overlap(ev_a.start_time, ev_a.end_time, ev_b.start_time, ev_b.end_time):
                rows.append(
                    ConflictType(
                        type="double_booked",
                        message=(
                            f"{person.name} is double-booked: '{ev_a.type}' "
                            f"and '{ev_b.type}' overlap"
                        ),
                        conflicting_event_id=ev_b.id,
                        start_time=ev_b.start_time,
                        end_time=ev_b.end_time,
                    )
                )
    return rows


@router.get("/", response_model=ListResponse[ConflictType])
def list_conflicts(
    org_id: str = Query(..., description="Organization ID"),
    person_id: str | None = Query(None, description="Optional filter to a single person"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """List currently-detected conflicts across an org (admin-only).

    Scans every Assignment in the org (or just the named person's) and
    surfaces `time_off` and `double_booked` conflicts. `already_assigned`
    is intentionally omitted because the assignment exists.
    """
    verify_org_member(current_admin, org_id)

    people_query = db.query(Person).filter(Person.org_id == org_id)
    if person_id is not None:
        people_query = people_query.filter(Person.id == person_id)

    all_rows: list[ConflictType] = []
    for person in people_query.all():
        all_rows.extend(_person_conflicts(person, db))

    page = all_rows[pagination.offset : pagination.offset + pagination.limit]
    return ListResponse[ConflictType](
        items=page,
        total=len(all_rows),
        limit=pagination.limit,
        offset=pagination.offset,
    )
