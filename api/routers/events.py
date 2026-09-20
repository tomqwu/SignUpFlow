"""Events router."""

from datetime import datetime
from typing import Any, cast

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_admin_user, get_current_user, verify_org_member
from api.models import (
    Assignment,
    Event,
    EventTeam,
    Notification,
    NotificationStatus,
    NotificationType,
    Organization,
    Person,
    Resource,
    Solution,
    Team,
)
from api.schemas.common import PaginationParams, get_pagination_params
from api.schemas.event import EventCreate, EventList, EventResponse, EventUpdate
from api.services import event_bus
from api.services.allocation_service import (
    AllocationConflictError,
    assign_person_to_event,
    unassign_person_from_event,
)
from api.services.assignment_response import reset_event_assignment_responses
from api.services.notification_service import dispatch_notification_ids
from api.timeutils import utcnow
from api.utils.event_helpers import (
    count_people_with_role,
    get_assigned_person_ids,
    get_blocked_assigned_people,
    get_event_required_roles,
    is_person_blocked_on_date,
    person_has_matching_role,
    validate_time_range,
)
from api.utils.response_messages import error_response, success_response, validation_warning

router = APIRouter(prefix="/events", tags=["events"])


class AvailablePerson(BaseModel):
    """Person available for an event."""

    id: str
    name: str
    email: str | None
    roles: list[str]
    is_assigned: bool
    is_blocked: bool = False  # True if person has blocked this date


class AssignmentRequest(BaseModel):
    """Request to assign/unassign a person."""

    person_id: str
    action: str  # "assign" or "unassign"
    role: str | None = None  # Event-specific role (e.g., "usher", "greeter", "sound_tech")


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Create a new event (admin only)."""
    # Verify admin belongs to the organization
    verify_org_member(current_admin, event_data.org_id)

    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == event_data.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{event_data.org_id}' not found",
        )

    # Check if event already exists
    existing = db.query(Event).filter(Event.id == event_data.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Event with ID '{event_data.id}' already exists",
        )

    # Validate times
    is_valid, error_message = validate_time_range(event_data.start_time, event_data.end_time)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    if event_data.resource_id is not None:
        resource = (
            db.query(Resource)
            .filter(
                Resource.id == event_data.resource_id,
                Resource.org_id == event_data.org_id,
            )
            .first()
        )
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    teams: list[Team] = []
    for team_id in event_data.team_ids or []:
        team = db.query(Team).filter(Team.id == team_id, Team.org_id == event_data.org_id).first()
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        teams.append(team)

    # Create event
    event = Event(
        id=event_data.id,
        org_id=event_data.org_id,
        type=event_data.type,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        resource_id=event_data.resource_id,
        extra_data=event_data.extra_data or {},
    )
    db.add(event)
    db.flush()

    # Add event teams
    if teams:
        for team in teams:
            event_team = EventTeam(event_id=event.id, team_id=team.id)
            db.add(event_team)

    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=EventList)
def list_events(
    org_id: str | None = Query(None, description="Filter by organization ID"),
    event_type: str | None = Query(None, description="Filter by event type"),
    start_after: datetime
    | None = Query(None, description="Filter events starting after this time"),
    start_before: datetime
    | None = Query(None, description="Filter events starting before this time"),
    q: str | None = Query(None, description="Case-insensitive search on event type and id"),
    status_filter: str
    | None = Query(
        None,
        alias="status",
        description="Filter by computed status: 'upcoming', 'past', or 'ongoing'",
    ),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List events within the authenticated member's tenant."""
    effective_org_id = org_id or current_user.org_id
    verify_org_member(current_user, effective_org_id)
    query = db.query(Event).filter(Event.org_id == effective_org_id)
    if event_type:
        query = query.filter(Event.type == event_type)
    if start_after:
        query = query.filter(Event.start_time >= start_after)
    if start_before:
        query = query.filter(Event.start_time <= start_before)

    if q:
        like = f"%{q}%"
        query = query.filter(or_(Event.type.ilike(like), Event.id.ilike(like)))

    if status_filter:
        now = utcnow()
        if status_filter == "upcoming":
            query = query.filter(Event.start_time > now)
        elif status_filter == "past":
            query = query.filter(Event.end_time < now)
        elif status_filter == "ongoing":
            query = query.filter(Event.start_time <= now, Event.end_time >= now)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status '{status_filter}'. Must be 'upcoming', 'past', or 'ongoing'",
            )

    query = query.order_by(Event.start_time)
    events = query.offset(pagination.offset).limit(pagination.limit).all()
    total = query.count()
    return {
        "items": events,
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: str,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get an event within the authenticated member's tenant."""
    event = (
        db.query(Event).filter(Event.id == event_id, Event.org_id == current_user.org_id).first()
    )
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: str,
    event_data: EventUpdate,
    background_tasks: BackgroundTasks,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Update event (admin only)."""
    event = (
        db.query(Event).filter(Event.id == event_id, Event.org_id == current_admin.org_id).first()
    )
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Verify admin belongs to the same organization as the event
    verify_org_member(current_admin, event.org_id)

    old_datetime = event.start_time.strftime("%A, %B %d, %Y at %I:%M %p")
    old_location = (event.extra_data or {}).get("location") or (
        event.resource.location if event.resource else None
    )

    material_change = any(
        value is not None and value != getattr(event, field)
        for field, value in (
            ("type", event_data.type),
            ("start_time", event_data.start_time),
            ("end_time", event_data.end_time),
            ("resource_id", event_data.resource_id),
            ("extra_data", event_data.extra_data),
        )
    )

    # Update fields
    if event_data.type is not None:
        event.type = event_data.type
    if event_data.start_time is not None:
        event.start_time = event_data.start_time
    if event_data.end_time is not None:
        event.end_time = event_data.end_time
    if event_data.resource_id is not None:
        resource = (
            db.query(Resource)
            .filter(
                Resource.id == event_data.resource_id,
                Resource.org_id == event.org_id,
            )
            .first()
        )
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        event.resource_id = event_data.resource_id
    if event_data.extra_data is not None:
        event.extra_data = event_data.extra_data

    # Validate times
    is_valid, error_message = validate_time_range(event.start_time, event.end_time)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    if material_change:
        visible_assignments = (
            db.query(Assignment)
            .join(Person, Person.id == Assignment.person_id)
            .outerjoin(Solution, Solution.id == Assignment.solution_id)
            .filter(
                Assignment.event_id == event.id,
                Person.org_id == event.org_id,
                Assignment.response_status != "declined",
                or_(Assignment.solution_id.is_(None), Solution.is_published.is_(True)),
            )
            .all()
        )
        reset_event_assignment_responses(db, event.id, event.org_id)
        for assignment in visible_assignments:
            delivery_key = (
                f"event:{event.id}:update:{assignment.id}:" f"r{assignment.commitment_revision}"
            )
            existing = (
                db.query(Notification)
                .filter(
                    Notification.org_id == event.org_id,
                    Notification.delivery_key == delivery_key,
                )
                .first()
            )
            if existing is None:
                db.add(
                    Notification(
                        org_id=event.org_id,
                        recipient_id=assignment.person_id,
                        type=NotificationType.UPDATE,
                        status=NotificationStatus.PENDING,
                        event_id=event.id,
                        delivery_key=delivery_key,
                        template_data={
                            "old_datetime": old_datetime,
                            "old_location": old_location,
                            "role": assignment.role,
                        },
                    )
                )
        if event.series_id is not None:
            setattr(event, "is_exception", True)

    db.commit()
    db.refresh(event)
    if material_change:
        notification_refs = [
            (row.id, row.org_id)
            for row in db.query(Notification)
            .filter(
                Notification.org_id == event.org_id,
                Notification.delivery_key.like(f"event:{event.id}:update:%"),
                Notification.status == NotificationStatus.PENDING,
            )
            .all()
        ]
        dispatch_notification_ids(background_tasks, notification_refs)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: str,
    background_tasks: BackgroundTasks,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    """Cancel an event (admin only), telling whoever was scheduled for it."""
    event = (
        db.query(Event).filter(Event.id == event_id, Event.org_id == current_admin.org_id).first()
    )
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Verify admin belongs to the same organization as the event
    verify_org_member(current_admin, event.org_id)

    notification_refs = _queue_cancellation_notices(db, event)

    db.delete(event)
    db.commit()
    dispatch_notification_ids(background_tasks, notification_refs)
    return None


def _queue_cancellation_notices(db: Session, event: Event) -> list[tuple[int, str]]:
    """Record one cancellation notice per assignee before the event row goes away.

    The notice deliberately stores ``event_id=None`` and a self-contained
    snapshot in ``template_data``. ``Event.notifications`` cascades with
    ``delete-orphan``, so a notice still pointing at the event would be deleted
    in the same transaction, and the renderer could not re-read a deleted event
    to fill in the email.
    """
    assignments = db.query(Assignment).filter(Assignment.event_id == event.id).all()
    if not assignments:
        return []

    event_data: dict[str, Any] = event.extra_data or {}
    snapshot: dict[str, Any] = {
        "event_id": event.id,
        "event_title": event_data.get("title") or event.type,
        "event_datetime": event.start_time.strftime("%A, %B %d, %Y at %I:%M %p"),
        "event_location": event_data.get("location")
        or (event.resource.location if event.resource else None),
    }

    queued: list[tuple[int, str]] = []
    # One notice per person, even when they hold several roles at this event.
    for person_id in dict.fromkeys(a.person_id for a in assignments):
        role = next((a.role for a in assignments if a.person_id == person_id and a.role), None)
        delivery_key = f"event:{event.id}:cancel:{person_id}"
        already = (
            db.query(Notification)
            .filter(
                Notification.org_id == event.org_id,
                Notification.delivery_key == delivery_key,
            )
            .first()
        )
        if already is not None:
            continue
        notification = Notification(
            org_id=event.org_id,
            recipient_id=person_id,
            type=NotificationType.CANCELLATION,
            status=NotificationStatus.PENDING,
            event_id=None,
            delivery_key=delivery_key,
            template_data={**snapshot, "role": role or "Volunteer"},
        )
        db.add(notification)
        db.flush()
        queued.append((cast(int, notification.id), cast(str, event.org_id)))
    return queued


@router.get("/{event_id}/available-people", response_model=list[AvailablePerson])
def get_available_people(
    event_id: str,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[AvailablePerson]:
    """
    Get people available for this event based on roles.

    Returns list of people who have matching roles, with flags indicating
    if they're already assigned or have blocked the event date.
    """
    event = (
        db.query(Event).filter(Event.id == event_id, Event.org_id == current_admin.org_id).first()
    )
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Get required roles from event
    required_roles = get_event_required_roles(event)

    # Get all people in the organization
    people = db.query(Person).filter(Person.org_id == event.org_id).all()

    # Get current assignments for this event
    assigned_person_ids = get_assigned_person_ids(db, event_id, event.org_id)

    # Get event date (just the date part, not time)
    event_date = event.start_time.date()

    # Filter people by matching roles
    available = []
    for person in people:
        person_roles = person.roles or []

        # Check if person has any of the required roles
        if person_has_matching_role(person_roles, required_roles):
            # Check if person has blocked this date
            is_blocked = is_person_blocked_on_date(db, person.id, event_date)

            available.append(
                AvailablePerson(
                    id=person.id,
                    name=person.name,
                    email=person.email,
                    roles=person_roles,
                    is_assigned=person.id in assigned_person_ids,
                    is_blocked=is_blocked,
                )
            )

    return available


@router.get("/{event_id}/validation")
def validate_event(
    event_id: str,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Validate if event has proper configuration and enough people.

    Checks:
    1. Event has role requirements configured
    2. Enough people available for each role
    3. No assigned people are blocked on the event date

    Returns:
        Dictionary with is_valid flag and list of validation warnings
    """
    event = (
        db.query(Event).filter(Event.id == event_id, Event.org_id == current_admin.org_id).first()
    )
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    warnings = []
    is_valid = True

    # Check if event has role_counts
    role_counts = (event.extra_data or {}).get("role_counts", {})

    if not role_counts:
        warnings.append(validation_warning("missing_config", "events.validation.no_roles"))
        is_valid = False
    else:
        # Check each role has enough people
        people = db.query(Person).filter(Person.org_id == event.org_id).all()

        for role, needed_count in role_counts.items():
            # Count people with this role
            available_count = count_people_with_role(people, role)

            if available_count < needed_count:
                warnings.append(
                    validation_warning(
                        "insufficient_people",
                        "events.validation.need_more_people",
                        needed=needed_count,
                        role=role,
                        available=available_count,
                    )
                )
                is_valid = False

    # Check if any assigned people are blocked on this event date
    event_date = event.start_time.date()
    blocked_people = get_blocked_assigned_people(db, event_id, event_date, event.org_id)

    if blocked_people:
        warnings.append(
            validation_warning(
                "blocked_assignments",
                "events.validation.blocked_people_assigned",
                people=", ".join(blocked_people),
            )
        )
        is_valid = False

    return {"event_id": event_id, "is_valid": is_valid, "warnings": warnings}


@router.post("/{event_id}/assignments")
def manage_assignment(
    event_id: str,
    request: AssignmentRequest,
    background_tasks: BackgroundTasks,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Assign or unassign a person through the serialized allocation boundary."""
    event = (
        db.query(Event).filter(Event.id == event_id, Event.org_id == current_admin.org_id).first()
    )
    if not event:
        raise error_response("events.errors.event_not_found", status_code=status.HTTP_404_NOT_FOUND)

    # Verify admin belongs to the same organization as the event
    verify_org_member(current_admin, event.org_id)

    person = (
        db.query(Person)
        .filter(Person.id == request.person_id, Person.org_id == event.org_id)
        .first()
    )
    if not person:
        raise error_response(
            "events.errors.person_not_found", status_code=status.HTTP_404_NOT_FOUND
        )

    # Verify person belongs to the same organization
    verify_org_member(current_admin, person.org_id)

    if request.action == "assign":
        try:
            assignment = assign_person_to_event(
                db,
                org_id=cast(str, event.org_id),
                event_id=event_id,
                person_id=request.person_id,
                role=request.role,
            )
            db.commit()
            db.refresh(assignment)
        except AllocationConflictError as exc:
            db.rollback()
            code = (
                status.HTTP_404_NOT_FOUND
                if exc.code in {"event_unavailable", "person_unavailable", "organization_missing"}
                else status.HTTP_409_CONFLICT
            )
            raise HTTPException(status_code=code, detail=exc.message) from exc
        except Exception:
            db.rollback()
            raise

        return success_response(
            "events.assign.success",
            {"assignment_id": assignment.id, "role": request.role},
            person=person.name,
        )

    elif request.action == "unassign":
        try:
            deleted_assignment_id, deleted_solution_id = unassign_person_from_event(
                db,
                org_id=cast(str, event.org_id),
                event_id=event_id,
                person_id=request.person_id,
            )
            db.commit()
        except AllocationConflictError as exc:
            db.rollback()
            code = (
                status.HTTP_404_NOT_FOUND
                if exc.code
                in {
                    "event_unavailable",
                    "person_unavailable",
                    "organization_missing",
                    "not_assigned",
                }
                else status.HTTP_409_CONFLICT
            )
            raise HTTPException(status_code=code, detail=exc.message) from exc
        except Exception:
            db.rollback()
            raise
        if deleted_solution_id is not None:
            background_tasks.add_task(
                event_bus.publish,
                event_bus.solution_topic(cast(str, event.org_id), deleted_solution_id),
                {
                    "type": "assignment.changed",
                    "assignment_id": deleted_assignment_id,
                    "solution_id": deleted_solution_id,
                    "status": "deleted",
                },
            )
        return success_response("events.assign.unassigned", person=person.name)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{request.action}'. Must be 'assign' or 'unassign'",
        )


@router.get("/assignments/all")
def get_all_assignments(
    org_id: str = Query(..., description="Organization ID"),
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all assignments for an organization (both from solutions and manual)."""
    verify_org_member(current_admin, org_id)

    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Organization '{org_id}' not found"
        )

    # Get all assignments joined with events to filter by organization
    rows = (
        db.query(Assignment, Event, Person)
        .join(Event, Event.id == Assignment.event_id)
        .join(Person, Person.id == Assignment.person_id)
        .filter(Event.org_id == org_id, Person.org_id == org_id)
        .all()
    )

    result = []
    for assignment, event, person in rows:
        result.append(
            {
                "assignment_id": assignment.id,
                "event_id": assignment.event_id,
                "event_type": event.type,
                "event_start": event.start_time,
                "event_end": event.end_time,
                "person_id": assignment.person_id,
                "person_name": person.name,
                "role": assignment.role,  # Event-specific role
                "solution_id": assignment.solution_id,
                "is_manual": assignment.solution_id is None,
                "status": assignment.status,
                "response_status": assignment.response_status,
                "responded_by_person_id": assignment.responded_by_person_id,
                "responded_at": assignment.responded_at,
                "commitment_revision": assignment.commitment_revision,
                "response_revision": assignment.response_revision,
                "response_current": assignment.response_current,
            }
        )

    return {"assignments": result, "total": len(result)}
