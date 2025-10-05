"""Database helper functions for common query patterns."""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from roster_cli.db.models import (
    Person,
    Organization,
    Team,
    Event,
    Assignment,
    VacationPeriod,
    Availability
)


def get_person_with_org_check(
    db: Session,
    person_id: str,
    org_id: str
) -> Optional[Person]:
    """Get person by ID and verify they belong to the organization."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if person and person.org_id == org_id:
        return person
    return None


def check_email_exists(
    db: Session,
    email: str,
    org_id: str
) -> bool:
    """Check if email already exists in the organization."""
    return db.query(Person).filter(
        Person.email == email,
        Person.org_id == org_id
    ).first() is not None


def get_team_members(
    db: Session,
    team_id: str
) -> List[Person]:
    """Get all members of a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return []
    # Get people through the team_members association
    return [tm.person for tm in team.members]


def get_person_assignments(
    db: Session,
    person_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Assignment]:
    """Get all assignments for a person, optionally filtered by date range."""
    query = db.query(Assignment).filter(Assignment.person_id == person_id)

    if start_date or end_date:
        # Join with Event to filter by date
        query = query.join(Event, Assignment.event_id == Event.id)

        if start_date:
            query = query.filter(Event.start_time >= start_date)
        if end_date:
            query = query.filter(Event.end_time <= end_date)

    return query.all()


def is_person_blocked_on_date(
    db: Session,
    person_id: str,
    date: datetime
) -> tuple[bool, Optional[str]]:
    """
    Check if person is blocked on a specific date.

    Returns:
        Tuple of (is_blocked: bool, reason: Optional[str])
    """
    # Check vacation periods through availability relationship
    # VacationPeriod has availability_id, not person_id directly
    # We need to join through Availability to check vacation periods
    availability_records = db.query(Availability).filter(
        Availability.person_id == person_id
    ).all()

    for avail in availability_records:
        for vacation in avail.vacations:
            if vacation.start_date <= date.date() <= vacation.end_date:
                return True, vacation.reason

    # Note: Availability uses rrule for recurring patterns
    # This would require rrule parsing to check availability properly
    # For now, just return False if no vacation periods block the date

    return False, None


def get_event_assignments(
    db: Session,
    event_id: str
) -> List[Assignment]:
    """Get all assignments for an event."""
    return db.query(Assignment).filter(Assignment.event_id == event_id).all()


def get_organization_events(
    db: Session,
    org_id: str,
    event_type: Optional[str] = None,
    start_after: Optional[datetime] = None,
    start_before: Optional[datetime] = None
) -> List[Event]:
    """Get organization events with optional filters."""
    query = db.query(Event).filter(Event.org_id == org_id)

    if event_type:
        query = query.filter(Event.type == event_type)
    if start_after:
        query = query.filter(Event.start_time >= start_after)
    if start_before:
        query = query.filter(Event.start_time <= start_before)

    return query.order_by(Event.start_time).all()


def get_available_people_for_event(
    db: Session,
    event: Event,
    role_filter: Optional[str] = None
) -> List[Person]:
    """
    Get all people available for an event.

    Filters out people who are:
    - Already assigned to the event
    - Blocked/on vacation on the event date
    - Don't have the required role (if role_filter specified)
    """
    # Get all people in the organization
    query = db.query(Person).filter(Person.org_id == event.org_id)

    # Filter by role if specified
    if role_filter:
        # SQLAlchemy JSON contains query
        query = query.filter(Person.roles.contains([role_filter]))

    all_people = query.all()

    # Get already assigned people
    assigned_ids = {
        a.person_id
        for a in db.query(Assignment).filter(Assignment.event_id == event.id).all()
    }

    # Filter available people
    available = []
    for person in all_people:
        if person.id in assigned_ids:
            continue

        is_blocked, _ = is_person_blocked_on_date(db, person.id, event.start_time)
        if not is_blocked:
            available.append(person)

    return available
