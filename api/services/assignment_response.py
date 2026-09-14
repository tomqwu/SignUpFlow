"""Truthful member-response transitions for assignment commitments."""

from __future__ import annotations

from sqlalchemy.orm import Session

from api.models import Assignment, Event, Solution, utcnow


class StaleAssignmentResponseError(ValueError):
    """The client responded to an older assignment commitment."""


def record_assignment_response(
    assignment: Assignment,
    *,
    actor_person_id: str,
    response_status: str,
    workflow_status: str,
    expected_revision: int | None,
    decline_reason: str | None = None,
) -> bool:
    """Apply one response in-memory and return whether persistent state changed."""
    revision = assignment.commitment_revision or 1
    if expected_revision is not None and expected_revision != revision:
        raise StaleAssignmentResponseError(
            f"Assignment changed from revision {expected_revision} to {revision}; reload and respond again"
        )

    if (
        assignment.response_current
        and assignment.response_status == response_status
        and assignment.status == workflow_status
        and assignment.decline_reason == decline_reason
    ):
        return False

    assignment.status = workflow_status
    assignment.response_status = response_status
    assignment.responded_by_person_id = actor_person_id
    assignment.responded_at = utcnow()
    assignment.response_revision = revision
    assignment.decline_reason = decline_reason
    return True


def reset_assignment_response(assignment: Assignment) -> None:
    """Create a new commitment revision without fabricating a member response."""
    assignment.commitment_revision = (assignment.commitment_revision or 1) + 1
    assignment.status = "pending"
    assignment.response_status = "pending"
    assignment.responded_by_person_id = None
    assignment.responded_at = None
    assignment.response_revision = None
    assignment.decline_reason = None


def reset_event_assignment_responses(db: Session, event_id: str, org_id: str) -> None:
    """Invalidate responses after a material event commitment changes."""
    rows = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(Assignment.event_id == event_id, Event.org_id == org_id)
        .all()
    )
    for assignment in rows:
        reset_assignment_response(assignment)


def carry_forward_current_responses(
    db: Session,
    *,
    solution: Solution,
    prior_solutions: list[Solution],
    reset_stale_target_responses: bool = False,
) -> None:
    """Carry verified responses to an unchanged assignment in a replacement solution."""
    if not prior_solutions:
        return

    prior_ids = [row.id for row in prior_solutions]
    prior_rows = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Event.org_id == solution.org_id,
            Assignment.solution_id.in_(prior_ids),
        )
        .all()
    )
    verified = {
        (row.event_id, row.person_id, row.role): row for row in prior_rows if row.response_current
    }
    target_rows = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Event.org_id == solution.org_id,
            Assignment.solution_id == solution.id,
        )
        .all()
    )
    for target in target_rows:
        source = verified.get((target.event_id, target.person_id, target.role))
        if source is None:
            if reset_stale_target_responses and target.response_current:
                reset_assignment_response(target)
            continue
        target.status = source.status
        target.response_status = source.response_status
        target.responded_by_person_id = source.responded_by_person_id
        target.responded_at = source.responded_at
        target.response_revision = target.commitment_revision
        target.decline_reason = source.decline_reason
