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
