"""Conflict detection router - check for scheduling conflicts."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_user, verify_org_member
from api.models import (
    Assignment,
    Availability,
    Event,
    Person,
    VacationPeriod,
)
from api.schemas.common import PaginationParams, get_pagination_params
from api.schemas.conflicts import (
    ConflictCheckRequest,
    ConflictCheckResponse,
    ConflictList,
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


@router.get("/", response_model=ConflictList, operation_id="listConflicts")
def list_conflicts(
    org_id: str = Query(..., description="Organization scope (required)"),
    person_id: str = Query(..., description="Person whose conflicts to surface"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConflictList:
    """List existing scheduling conflicts for `person_id` within `org_id`.

    Surfaces:
    - `double_booked` — pairs of overlapping assignments
    - `time_off` — assignments overlapping the person's vacation periods

    Reuses `check_time_overlap`. Auth: caller must be a member of `org_id`.
    """
    verify_org_member(current_user, org_id)

    person = db.query(Person).filter(Person.id == person_id, Person.org_id == org_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Person '{person_id}' not found",
        )

    # Pull all of this person's assignments scoped to org-owned events.
    assignments = (
        db.query(Assignment)
        .join(Event, Event.id == Assignment.event_id)
        .filter(Assignment.person_id == person_id, Event.org_id == org_id)
        .all()
    )
    events_by_id: dict[str, Event] = {}
    if assignments:
        events_by_id = {
            e.id: e
            for e in db.query(Event)
            .filter(
                Event.org_id == org_id,
                Event.id.in_([a.event_id for a in assignments]),
            )
            .all()
        }

    conflicts: list[ConflictType] = []

    # Double-booked: each unordered pair of overlapping events yields one
    # conflict per side so the caller can see both event references.
    assigned_events = [events_by_id[a.event_id] for a in assignments if a.event_id in events_by_id]
    for i, ev_a in enumerate(assigned_events):
        for ev_b in assigned_events[i + 1 :]:
            if check_time_overlap(ev_a.start_time, ev_a.end_time, ev_b.start_time, ev_b.end_time):
                conflicts.append(
                    ConflictType(
                        type="double_booked",
                        message=(
                            f"{person.name} is double-booked: '{ev_a.type}' overlaps '{ev_b.type}'"
                        ),
                        conflicting_event_id=ev_b.id,
                        start_time=ev_b.start_time,
                        end_time=ev_b.end_time,
                    )
                )
                conflicts.append(
                    ConflictType(
                        type="double_booked",
                        message=(
                            f"{person.name} is double-booked: '{ev_b.type}' overlaps '{ev_a.type}'"
                        ),
                        conflicting_event_id=ev_a.id,
                        start_time=ev_a.start_time,
                        end_time=ev_a.end_time,
                    )
                )

    # Time-off conflicts: any assignment overlapping a vacation period.
    # Availability is scoped to a person; the person's org membership was
    # already enforced above via Person.org_id == org_id.
    availability = db.query(Availability).filter(Availability.person_id == person_id).first()
    if availability:
        vacations = (
            db.query(VacationPeriod).filter(VacationPeriod.availability_id == availability.id).all()
        )
        for ev in assigned_events:
            for vac in vacations:
                vac_start = datetime.combine(vac.start_date, datetime.min.time())
                vac_end = datetime.combine(vac.end_date, datetime.max.time())
                if check_time_overlap(ev.start_time, ev.end_time, vac_start, vac_end):
                    conflicts.append(
                        ConflictType(
                            type="time_off",
                            message=(
                                f"{person.name} has time-off "
                                f"{vac.start_date}..{vac.end_date} during '{ev.type}'"
                            ),
                            conflicting_event_id=ev.id,
                            start_time=vac_start,
                            end_time=vac_end,
                        )
                    )

    total = len(conflicts)
    page = conflicts[pagination.offset : pagination.offset + pagination.limit]
    return ConflictList(
        items=page,
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )
