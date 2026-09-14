"""Serialized allocation changes for manual, open-shift, and swap workflows."""

from __future__ import annotations

from typing import Any, cast

from sqlalchemy import update
from sqlalchemy.orm import Query, Session

from api.core.timeutils import parse_rrule
from api.models import (
    Assignment,
    AuditAction,
    Availability,
    AvailabilityException,
    Event,
    Organization,
    Person,
    VacationPeriod,
)
from api.services.assignment_response import record_assignment_response, reset_assignment_response
from api.services.assignment_visibility import member_visible_assignment
from api.timeutils import utcnow
from api.utils.audit_logger import log_audit_event


class AllocationConflictError(ValueError):
    """A controlled allocation rejection that leaves the roster unchanged."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def lock_organization_allocations(db: Session, org_id: str) -> None:
    """Serialize allocation writers on one organization row.

    PostgreSQL takes a row lock for this no-op update. SQLite takes its database
    write lock before any occupancy reads, which gives the local runtime the same
    one-writer validation boundary.
    """
    result = db.execute(
        update(Organization)
        .where(Organization.id == org_id)
        .values(updated_at=Organization.updated_at)
    )
    if cast(Any, result).rowcount != 1:
        raise AllocationConflictError(
            "organization_missing", "Organization is no longer available."
        )


def _load_event(db: Session, org_id: str, event_id: str) -> Event:
    event = db.query(Event).filter(Event.org_id == org_id, Event.id == event_id).first()
    if event is None:
        raise AllocationConflictError("event_unavailable", "That event is no longer available.")
    return event


def _load_person(db: Session, org_id: str, person_id: str) -> Person:
    person = db.query(Person).filter(Person.org_id == org_id, Person.id == person_id).first()
    if person is None or person.status != "active":
        raise AllocationConflictError("person_unavailable", "Your membership is no longer active.")
    return person


def _require_future_event(event: Event) -> None:
    if event.start_time < utcnow():
        raise AllocationConflictError("event_closed", "That event is no longer open.")


def _require_qualification(person: Person, role: str) -> None:
    if role not in (person.roles or []):
        raise AllocationConflictError(
            "not_qualified", f"You are not qualified for the {role} role."
        )


def _require_available(db: Session, person: Person, event: Event) -> None:
    availability = db.query(Availability).filter(Availability.person_id == person.id).first()
    if availability is None:
        return

    event_date = event.start_time.date()
    vacation = (
        db.query(VacationPeriod)
        .filter(
            VacationPeriod.availability_id == availability.id,
            VacationPeriod.start_date <= event_date,
            VacationPeriod.end_date >= event_date,
        )
        .first()
    )
    exception = (
        db.query(AvailabilityException)
        .filter(
            AvailabilityException.availability_id == availability.id,
            AvailabilityException.exception_date == event_date,
        )
        .first()
    )
    recurring_blocked = False
    if availability.rrule:
        try:
            recurring_blocked = bool(
                parse_rrule(
                    cast(str, availability.rrule),
                    event.start_time.replace(hour=0, minute=0, second=0, microsecond=0),
                    event.start_time.replace(hour=23, minute=59, second=59, microsecond=999999),
                )
            )
        except (TypeError, ValueError) as exc:
            raise AllocationConflictError(
                "availability_invalid",
                "Your recurring availability rule must be repaired before claiming a shift.",
            ) from exc
    if vacation is not None or exception is not None or recurring_blocked:
        raise AllocationConflictError("unavailable", "You are unavailable for that event.")


def require_person_available(db: Session, *, person: Person, event: Event) -> None:
    """Reject an assignment when the member has a current availability block."""
    _require_available(db, person, event)


def _active_assignments(db: Session, org_id: str) -> Query[Assignment]:
    return (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Event.org_id == org_id,
            Assignment.status != "declined",
            member_visible_assignment(org_id),
        )
    )


def _role_counts(event: Event) -> dict[str, Any]:
    extra_data = cast(dict[str, Any], event.extra_data or {})
    role_counts = extra_data.get("role_counts")
    return cast(dict[str, Any], role_counts) if isinstance(role_counts, dict) else {}


def _require_no_overlap(
    db: Session,
    *,
    org_id: str,
    person_id: str,
    event: Event,
    exclude_assignment_id: int | None = None,
) -> None:
    query = _active_assignments(db, org_id).filter(
        Assignment.person_id == person_id,
        Assignment.event_id != event.id,
        Event.start_time < event.end_time,
        Event.end_time > event.start_time,
    )
    if exclude_assignment_id is not None:
        query = query.filter(Assignment.id != exclude_assignment_id)
    if query.first() is not None:
        raise AllocationConflictError("overlap", "You already have an overlapping assignment.")


def _audit_claim(
    db: Session,
    *,
    assignment: Assignment,
    person: Person,
    source: str,
    prior_person_id: str | None = None,
) -> None:
    details: dict[str, str | int] = {
        "source": source,
        "commitment_revision": cast(int, assignment.commitment_revision),
    }
    if prior_person_id is not None:
        details["prior_person_id"] = prior_person_id
    log_audit_event(
        db,
        action=AuditAction.ASSIGNMENT_ACCEPTED,
        user_id=cast(str, person.id),
        user_email=cast(str, person.email),
        organization_id=cast(str, person.org_id),
        resource_type="assignment",
        resource_id=str(assignment.id),
        details=details,
        commit=False,
    )


def claim_open_shift(
    db: Session,
    *,
    org_id: str,
    event_id: str,
    person_id: str,
    role: str,
    actor_email: str | None = None,
) -> tuple[Assignment, bool]:
    """Claim one open role while holding the tenant allocation lock."""
    lock_organization_allocations(db, org_id)
    event = _load_event(db, org_id, event_id)
    person = _load_person(db, org_id, person_id)
    if actor_email is not None and person.email != actor_email:
        raise AllocationConflictError("actor_changed", "Your account changed; sign in again.")
    _require_future_event(event)

    role_counts = _role_counts(event)
    capacity = role_counts.get(role)
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
        raise AllocationConflictError("role_unavailable", "That role is no longer open.")
    _require_qualification(person, role)
    _require_available(db, person, event)

    existing = (
        _active_assignments(db, org_id)
        .filter(Assignment.event_id == event.id, Assignment.person_id == person.id)
        .first()
    )
    if existing is not None:
        if (
            existing.role == role
            and existing.response_current
            and existing.response_status == "accepted"
        ):
            return existing, False
        raise AllocationConflictError("already_assigned", "You're already on that event.")

    _require_no_overlap(db, org_id=org_id, person_id=cast(str, person.id), event=event)
    occupied = (
        _active_assignments(db, org_id)
        .filter(Assignment.event_id == event.id, Assignment.role == role)
        .count()
    )
    if occupied >= capacity:
        raise AllocationConflictError("role_full", "That role just filled up.")

    assignment = Assignment(
        event_id=event.id,
        person_id=person.id,
        role=role,
        solution_id=None,
        commitment_revision=1,
    )
    record_assignment_response(
        assignment,
        actor_person_id=cast(str, person.id),
        response_status="accepted",
        workflow_status="confirmed",
        expected_revision=1,
    )
    db.add(assignment)
    db.flush()
    _audit_claim(db, assignment=assignment, person=person, source="open_shift_claim")
    return assignment, True


def assign_person_to_event(
    db: Session,
    *,
    org_id: str,
    event_id: str,
    person_id: str,
    role: str | None,
) -> Assignment:
    """Create one coordinator assignment under the shared allocation lock."""
    lock_organization_allocations(db, org_id)
    event = _load_event(db, org_id, event_id)
    person = _load_person(db, org_id, person_id)
    existing = (
        _active_assignments(db, org_id)
        .filter(Assignment.event_id == event.id, Assignment.person_id == person.id)
        .first()
    )
    if existing is not None:
        raise AllocationConflictError("already_assigned", f"{person.name} is already assigned.")

    _require_available(db, person, event)
    _require_no_overlap(db, org_id=org_id, person_id=cast(str, person.id), event=event)
    role_counts = _role_counts(event)
    if role_counts:
        if role not in role_counts:
            raise AllocationConflictError(
                "role_unavailable", "That role is not required for this event."
            )
        _require_qualification(person, role or "")
        occupied = (
            _active_assignments(db, org_id)
            .filter(Assignment.event_id == event.id, Assignment.role == role)
            .count()
        )
        capacity = role_counts[role]
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
            raise AllocationConflictError("role_unavailable", "That role is not available.")
        if occupied >= capacity:
            raise AllocationConflictError("role_full", "That role is already fully staffed.")

    assignment = Assignment(
        event_id=event.id,
        person_id=person.id,
        role=role,
        solution_id=None,
    )
    db.add(assignment)
    db.flush()
    return assignment


def unassign_person_from_event(
    db: Session,
    *,
    org_id: str,
    event_id: str,
    person_id: str,
) -> tuple[int, int | None]:
    """Delete one visible assignment under the shared allocation lock."""
    lock_organization_allocations(db, org_id)
    _load_event(db, org_id, event_id)
    person = _load_person(db, org_id, person_id)
    assignment = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Event.org_id == org_id,
            Assignment.event_id == event_id,
            Assignment.person_id == person.id,
            member_visible_assignment(org_id),
        )
        .first()
    )
    if assignment is None:
        raise AllocationConflictError("not_assigned", f"{person.name} is not assigned.")
    assignment_id = cast(int, assignment.id)
    solution_id = cast(int | None, assignment.solution_id)
    db.delete(assignment)
    db.flush()
    return assignment_id, solution_id


def deny_swap_request(db: Session, *, org_id: str, assignment_id: int) -> bool:
    """Reset one still-current swap request while holding the allocation lock."""
    lock_organization_allocations(db, org_id)
    assignment = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Event.org_id == org_id,
            Assignment.id == assignment_id,
            Assignment.status == "swap_requested",
            member_visible_assignment(org_id),
        )
        .first()
    )
    if assignment is None:
        return False
    reset_assignment_response(assignment)
    db.flush()
    return True


def member_can_take_role(db: Session, *, person: Person, event: Event, role: str) -> bool:
    """Return whether a member is currently eligible for a listed role."""
    try:
        if person.status != "active":
            return False
        _require_qualification(person, role)
        _require_available(db, person, event)
        _require_no_overlap(
            db,
            org_id=cast(str, person.org_id),
            person_id=cast(str, person.id),
            event=event,
        )
    except AllocationConflictError:
        return False
    return True


def cover_swap(
    db: Session,
    *,
    org_id: str,
    assignment_id: int,
    person_id: str,
    actor_email: str | None = None,
) -> tuple[Assignment, bool]:
    """Transfer one visible swap request to one qualified available member."""
    lock_organization_allocations(db, org_id)
    person = _load_person(db, org_id, person_id)
    if actor_email is not None and person.email != actor_email:
        raise AllocationConflictError("actor_changed", "Your account changed; sign in again.")
    assignment = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Event.org_id == org_id,
            Assignment.id == assignment_id,
            member_visible_assignment(org_id),
        )
        .first()
    )
    if assignment is None:
        raise AllocationConflictError("swap_unavailable", "That swap is no longer available.")
    if (
        assignment.person_id == person.id
        and assignment.status == "confirmed"
        and assignment.response_current
        and assignment.response_status == "accepted"
    ):
        return assignment, False
    if assignment.status != "swap_requested":
        raise AllocationConflictError("swap_unavailable", "That swap is no longer available.")
    if assignment.person_id == person.id:
        raise AllocationConflictError("own_swap", "That is your own swap request.")

    event = _load_event(db, org_id, cast(str, assignment.event_id))
    _require_future_event(event)
    role = cast(str | None, assignment.role) or ""
    _require_qualification(person, role)
    _require_available(db, person, event)
    existing = (
        _active_assignments(db, org_id)
        .filter(Assignment.event_id == event.id, Assignment.person_id == person.id)
        .first()
    )
    if existing is not None:
        raise AllocationConflictError("already_assigned", "You're already on that event.")
    _require_no_overlap(
        db,
        org_id=org_id,
        person_id=cast(str, person.id),
        event=event,
        exclude_assignment_id=cast(int, assignment.id),
    )

    prior_person_id = cast(str, assignment.person_id)
    assignment.person_id = person.id
    reset_assignment_response(assignment)
    record_assignment_response(
        assignment,
        actor_person_id=cast(str, person.id),
        response_status="accepted",
        workflow_status="confirmed",
        expected_revision=cast(int, assignment.commitment_revision),
    )
    db.flush()
    _audit_claim(
        db,
        assignment=assignment,
        person=person,
        source="swap_claim",
        prior_person_id=prior_person_id,
    )
    return assignment, True
