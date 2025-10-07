"""Events router."""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.database import get_db
from api.schemas.event import EventCreate, EventUpdate, EventResponse, EventList
from roster_cli.db.models import Event, EventTeam, Organization, Team, Person, Assignment, VacationPeriod, Availability

router = APIRouter(prefix="/events", tags=["events"])


class AvailablePerson(BaseModel):
    """Person available for an event."""
    id: str
    name: str
    email: Optional[str]
    roles: List[str]
    is_assigned: bool
    is_blocked: bool = False  # True if person has blocked this date


class AssignmentRequest(BaseModel):
    """Request to assign/unassign a person."""
    person_id: str
    action: str  # "assign" or "unassign"
    role: Optional[str] = None  # Event-specific role (e.g., "usher", "greeter", "sound_tech")


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event_data: EventCreate, db: Session = Depends(get_db)):
    """Create a new event."""
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
    if event_data.end_time <= event_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

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
    if event_data.team_ids:
        for team_id in event_data.team_ids:
            # Verify team exists
            team = db.query(Team).filter(Team.id == team_id).first()
            if not team:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team '{team_id}' not found",
                )
            event_team = EventTeam(event_id=event.id, team_id=team_id)
            db.add(event_team)

    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=EventList)
def list_events(
    org_id: Optional[str] = Query(None, description="Filter by organization ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    start_after: Optional[datetime] = Query(None, description="Filter events starting after this time"),
    start_before: Optional[datetime] = Query(None, description="Filter events starting before this time"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List events with optional filters."""
    query = db.query(Event)

    if org_id:
        query = query.filter(Event.org_id == org_id)
    if event_type:
        query = query.filter(Event.type == event_type)
    if start_after:
        query = query.filter(Event.start_time >= start_after)
    if start_before:
        query = query.filter(Event.start_time <= start_before)

    query = query.order_by(Event.start_time)
    events = query.offset(skip).limit(limit).all()
    total = query.count()
    return {"events": events, "total": total}


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    """Get event by ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event '{event_id}' not found"
        )
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(event_id: str, event_data: EventUpdate, db: Session = Depends(get_db)):
    """Update event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event '{event_id}' not found"
        )

    # Update fields
    if event_data.type is not None:
        event.type = event_data.type
    if event_data.start_time is not None:
        event.start_time = event_data.start_time
    if event_data.end_time is not None:
        event.end_time = event_data.end_time
    if event_data.resource_id is not None:
        event.resource_id = event_data.resource_id
    if event_data.extra_data is not None:
        event.extra_data = event_data.extra_data

    # Validate times
    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: str, db: Session = Depends(get_db)):
    """Delete event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event '{event_id}' not found"
        )

    db.delete(event)
    db.commit()
    return None


@router.get("/{event_id}/available-people", response_model=List[AvailablePerson])
def get_available_people(event_id: str, db: Session = Depends(get_db)):
    """Get people available for this event based on roles."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event '{event_id}' not found"
        )

    # Get required roles from event extra_data
    role_counts = (event.extra_data or {}).get("role_counts", {})
    required_roles = list(role_counts.keys()) if role_counts else (event.extra_data or {}).get("roles", [])

    # Get all people in the organization
    people = db.query(Person).filter(Person.org_id == event.org_id).all()

    # Get current assignments for this event
    assigned_person_ids = {
        a.person_id for a in db.query(Assignment).filter(Assignment.event_id == event_id).all()
    }

    # Get event date (just the date part, not time)
    event_date = event.start_time.date()

    # Filter people by matching roles
    available = []
    for person in people:
        person_roles = person.roles or []

        # Check if person has any of the required roles
        has_matching_role = not required_roles or any(role in person_roles for role in required_roles)

        if has_matching_role:
            # Check if person has blocked this date via Availability -> VacationPeriod join
            is_blocked = db.query(VacationPeriod).join(
                Availability, VacationPeriod.availability_id == Availability.id
            ).filter(
                Availability.person_id == person.id,
                VacationPeriod.start_date <= event_date,
                VacationPeriod.end_date >= event_date
            ).first() is not None

            available.append(AvailablePerson(
                id=person.id,
                name=person.name,
                email=person.email,
                roles=person_roles,
                is_assigned=person.id in assigned_person_ids,
                is_blocked=is_blocked
            ))

    return available


@router.get("/{event_id}/validation")
def validate_event(event_id: str, db: Session = Depends(get_db)):
    """Validate if event has proper configuration and enough people."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event '{event_id}' not found"
        )

    warnings = []
    is_valid = True

    # Check if event has role_counts
    role_counts = (event.extra_data or {}).get("role_counts", {})

    if not role_counts:
        warnings.append({
            "type": "missing_config",
            "message": "Event has no role requirements specified"
        })
        is_valid = False
    else:
        # Check each role has enough people
        people = db.query(Person).filter(Person.org_id == event.org_id).all()

        for role, needed_count in role_counts.items():
            # Count people with this role
            available_people = [p for p in people if p.roles and role in p.roles]
            available_count = len(available_people)

            if available_count < needed_count:
                warnings.append({
                    "type": "insufficient_people",
                    "role": role,
                    "needed": needed_count,
                    "available": available_count,
                    "message": f"Need {needed_count} {role}(s) but only {available_count} available"
                })
                is_valid = False

    # Check if any assigned people are blocked on this event date
    event_date = event.start_time.date()
    assignments = db.query(Assignment).filter(Assignment.event_id == event_id).all()

    if assignments:
        blocked_people = []
        for assignment in assignments:
            # Check if person has blocked this date
            is_blocked = db.query(VacationPeriod).join(
                Availability, VacationPeriod.availability_id == Availability.id
            ).filter(
                Availability.person_id == assignment.person_id,
                VacationPeriod.start_date <= event_date,
                VacationPeriod.end_date >= event_date
            ).first() is not None

            if is_blocked:
                person = db.query(Person).filter(Person.id == assignment.person_id).first()
                if person:
                    blocked_people.append(person.name)

        if blocked_people:
            warnings.append({
                "type": "blocked_assignments",
                "message": f"People with blocked dates assigned: {', '.join(blocked_people)}",
                "blocked_people": blocked_people
            })
            is_valid = False

    return {
        "event_id": event_id,
        "is_valid": is_valid,
        "warnings": warnings
    }


@router.post("/{event_id}/assignments")
def manage_assignment(event_id: str, request: AssignmentRequest, db: Session = Depends(get_db)):
    """Assign or unassign a person to/from an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event '{event_id}' not found"
        )

    person = db.query(Person).filter(Person.id == request.person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Person '{request.person_id}' not found"
        )

    if request.action == "assign":
        # Check if already assigned
        existing = db.query(Assignment).filter(
            Assignment.event_id == event_id,
            Assignment.person_id == request.person_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Person '{person.name}' is already assigned to this event"
            )

        # Create new assignment (solution_id is None for manual assignments)
        assignment = Assignment(
            event_id=event_id,
            person_id=request.person_id,
            role=request.role,  # Event-specific role
            solution_id=None
        )
        db.add(assignment)
        db.commit()
        role_info = f" as {request.role}" if request.role else ""
        return {"message": f"Assigned {person.name} to event{role_info}", "assignment_id": assignment.id, "role": request.role}

    elif request.action == "unassign":
        # Find and delete assignment
        assignment = db.query(Assignment).filter(
            Assignment.event_id == event_id,
            Assignment.person_id == request.person_id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person '{person.name}' is not assigned to this event"
            )

        db.delete(assignment)
        db.commit()
        return {"message": f"Unassigned {person.name} from event"}

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{request.action}'. Must be 'assign' or 'unassign'"
        )


@router.get("/assignments/all")
def get_all_assignments(org_id: str = Query(..., description="Organization ID"), db: Session = Depends(get_db)):
    """Get all assignments for an organization (both from solutions and manual)."""
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_id}' not found"
        )

    # Get all assignments joined with events to filter by organization
    assignments = db.query(Assignment).join(Event).filter(Event.org_id == org_id).all()

    result = []
    for assignment in assignments:
        event = db.query(Event).filter(Event.id == assignment.event_id).first()
        person = db.query(Person).filter(Person.id == assignment.person_id).first()

        result.append({
            "assignment_id": assignment.id,
            "event_id": assignment.event_id,
            "event_type": event.type if event else None,
            "event_start": event.start_time if event else None,
            "event_end": event.end_time if event else None,
            "person_id": assignment.person_id,
            "person_name": person.name if person else None,
            "role": assignment.role,  # Event-specific role
            "solution_id": assignment.solution_id,
            "is_manual": assignment.solution_id is None
        })

    return {"assignments": result, "total": len(result)}
