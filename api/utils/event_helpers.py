"""
Helper functions for event operations.

Extracted from api/routers/events.py to follow DRY principle and single responsibility.
"""

from datetime import date, datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from api.models import Person, VacationPeriod, Availability, Assignment, Event


def is_person_blocked_on_date(
    db: Session,
    person_id: str,
    target_date: date
) -> bool:
    """
    Check if a person has blocked a specific date via availability/vacation.

    Args:
        db: Database session
        person_id: Person ID to check
        target_date: Date to check (date object, not datetime)

    Returns:
        True if person has blocked this date, False otherwise

    Example:
        >>> is_blocked = is_person_blocked_on_date(db, "person_123", date(2025, 1, 15))
        >>> if is_blocked:
        ...     print("Person is unavailable on this date")
    """
    blocked = db.query(VacationPeriod).join(
        Availability, VacationPeriod.availability_id == Availability.id
    ).filter(
        Availability.person_id == person_id,
        VacationPeriod.start_date <= target_date,
        VacationPeriod.end_date >= target_date
    ).first()

    return blocked is not None


def get_assigned_person_ids(
    db: Session,
    event_id: str
) -> set[str]:
    """
    Get set of person IDs assigned to an event.

    Args:
        db: Database session
        event_id: Event ID to check

    Returns:
        Set of person IDs currently assigned to this event
    """
    assignments = db.query(Assignment).filter(
        Assignment.event_id == event_id
    ).all()

    return {assignment.person_id for assignment in assignments}


def person_has_matching_role(
    person_roles: List[str],
    required_roles: List[str]
) -> bool:
    """
    Check if person has any of the required roles.

    Args:
        person_roles: List of roles the person has
        required_roles: List of required roles (empty = any role OK)

    Returns:
        True if person has matching role or no roles required

    Example:
        >>> person_has_matching_role(["usher", "greeter"], ["usher", "sound"])
        True
        >>> person_has_matching_role(["admin"], ["usher", "sound"])
        False
    """
    if not required_roles:
        return True

    return any(role in person_roles for role in required_roles)


def get_event_required_roles(event: Event) -> List[str]:
    """
    Extract required roles from event extra_data.

    Args:
        event: Event object

    Returns:
        List of required role names

    Example:
        >>> roles = get_event_required_roles(event)
        >>> # Returns ["usher", "greeter", "sound_tech"]
    """
    extra_data = event.extra_data or {}
    role_counts = extra_data.get("role_counts", {})

    if role_counts:
        return list(role_counts.keys())
    else:
        return extra_data.get("roles", [])


def count_people_with_role(
    people: List[Person],
    role: str
) -> int:
    """
    Count how many people have a specific role.

    Args:
        people: List of Person objects
        role: Role name to count

    Returns:
        Number of people with this role
    """
    return sum(
        1 for person in people
        if person.roles and role in person.roles
    )


def validate_time_range(
    start_time: datetime,
    end_time: datetime
) -> Tuple[bool, Optional[str]]:
    """
    Validate that end time is after start time.

    Args:
        start_time: Event start time
        end_time: Event end time

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if times are valid
        - error_message: None if valid, error string if invalid

    Example:
        >>> is_valid, error = validate_time_range(start, end)
        >>> if not is_valid:
        ...     raise HTTPException(status_code=400, detail=error)
    """
    if end_time <= start_time:
        return False, "End time must be after start time"

    return True, None


def get_blocked_assigned_people(
    db: Session,
    event_id: str,
    event_date: date
) -> List[str]:
    """
    Get names of people assigned to event who are blocked on the event date.

    Args:
        db: Database session
        event_id: Event ID to check
        event_date: Date of the event

    Returns:
        List of person names who are both assigned and blocked
    """
    assignments = db.query(Assignment).filter(
        Assignment.event_id == event_id
    ).all()

    blocked_names = []
    for assignment in assignments:
        if is_person_blocked_on_date(db, assignment.person_id, event_date):
            person = db.query(Person).filter(
                Person.id == assignment.person_id
            ).first()
            if person:
                blocked_names.append(person.name)

    return blocked_names
