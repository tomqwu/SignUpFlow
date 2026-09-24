"""Reconcile scheduling work when an administrator changes qualifications."""

from typing import Any, cast

from sqlalchemy.orm import Session

from api.models import Assignment, Event, Person
from api.roles import PERMISSION_ROLES
from api.services.assignment_visibility import member_visible_assignment
from api.timeutils import utcnow


def replace_person_roles(db: Session, person: Person, roles: list[str]) -> int:
    """Replace roles and reopen future live work for removed qualifications.

    Draft candidates remain intact so publication validation can reject stale
    qualifications explicitly. Past assignments remain as completed history.
    """
    org_id = cast(str, person.org_id)
    removed_qualifications = set(person.roles or []) - set(roles) - PERMISSION_ROLES
    reopened = []
    if removed_qualifications:
        reopened = (
            db.query(Assignment)
            .join(Event, Assignment.event_id == Event.id)
            .filter(
                Event.org_id == org_id,
                Event.start_time >= utcnow(),
                Assignment.person_id == person.id,
                Assignment.role.in_(removed_qualifications),
                member_visible_assignment(org_id),
            )
            .all()
        )
        for assignment in reopened:
            db.delete(assignment)

    person.roles = cast(Any, roles)
    return len(reopened)


def release_person_work(db: Session, person: Person) -> int:
    """Reopen a departing person's future live work, keeping their history.

    Leaving the organization and losing every qualification are the same
    domain event: this person can no longer serve. So departure reopens the
    same narrow slice ``replace_person_roles`` does — future, org-scoped,
    member-visible work — and for the same reasons. Past assignments remain as
    completed history, and draft candidates remain intact so publication
    validation can reject a stale roster explicitly rather than silently.
    """
    org_id = cast(str, person.org_id)
    reopened = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Event.org_id == org_id,
            Event.start_time >= utcnow(),
            Assignment.person_id == person.id,
            member_visible_assignment(org_id),
        )
        .all()
    )
    for assignment in reopened:
        db.delete(assignment)
    return len(reopened)
