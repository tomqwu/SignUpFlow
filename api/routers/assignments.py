"""Volunteer-facing assignment self-service.

Volunteers can manage their own assignment lifecycle:
- accept (status -> "confirmed")
- decline (status -> "declined", with required reason)
- request a swap (status -> "swap_requested", optional note)
- list their own assignments

Admins keep their existing entry points in api/routers/events.py
(`POST /events/{id}/assignments` for assign/unassign,
 `GET /events/assignments/all` for org-wide listing).
"""

from typing import cast

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_user
from api.models import Assignment, AuditAction, Event, Person
from api.schemas.assignment import (
    AssignmentDeclineRequest,
    AssignmentResponse,
    AssignmentSwapRequest,
)
from api.schemas.common import ListResponse, PaginationParams, get_pagination_params
from api.services import event_bus
from api.services.assignment_response import (
    StaleAssignmentResponseError,
    record_assignment_response,
)
from api.services.assignment_visibility import member_visible_assignment
from api.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/assignments", tags=["assignments"])


def _load_own_assignment(assignment_id: int, current_user: Person, db: Session) -> Assignment:
    """Load an assignment that belongs to the caller; 404 if missing, 403 if not theirs."""
    assignment = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Assignment.id == assignment_id,
            Event.org_id == current_user.org_id,
            member_visible_assignment(cast(str, current_user.org_id)),
        )
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    if assignment.person_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage your own assignments",
        )
    return assignment


def _audit_status_change(
    db: Session,
    *,
    action: str,
    user: Person,
    assignment: Assignment,
    http_request: Request,
    details: dict | None = None,
) -> None:
    log_audit_event(
        db,
        action=action,
        user_id=user.id,
        user_email=user.email,
        organization_id=user.org_id,
        resource_type="assignment",
        resource_id=str(assignment.id),
        details=details or {},
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
        commit=False,
    )


def _record_and_commit_response(
    db: Session,
    *,
    assignment: Assignment,
    user: Person,
    http_request: Request,
    action: str,
    response_status: str,
    workflow_status: str,
    expected_revision: int | None,
    decline_reason: str | None = None,
    details: dict | None = None,
) -> bool:
    try:
        changed = record_assignment_response(
            assignment,
            actor_person_id=user.id,
            response_status=response_status,
            workflow_status=workflow_status,
            expected_revision=expected_revision,
            decline_reason=decline_reason,
        )
        if not changed:
            return False
        _audit_status_change(
            db,
            action=action,
            user=user,
            assignment=assignment,
            http_request=http_request,
            details={
                **(details or {}),
                "response_status": response_status,
                "commitment_revision": assignment.commitment_revision,
            },
        )
        db.commit()
    except StaleAssignmentResponseError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise
    db.refresh(assignment)
    return True


def _publish_assignment_change(
    background_tasks: BackgroundTasks,
    assignment: Assignment,
    org_id: str,
) -> None:
    # Manual/admin-created assignments have solution_id=None and don't
    # belong to a Solution Review stream. Skip them to avoid publishing
    # under the "solution:None" topic.
    if assignment.solution_id is None:
        return
    background_tasks.add_task(
        event_bus.publish,
        event_bus.solution_topic(org_id, assignment.solution_id),
        {
            "type": "assignment.changed",
            "assignment_id": assignment.id,
            "solution_id": assignment.solution_id,
            "status": assignment.status,
        },
    )


@router.post("/{assignment_id}/accept", response_model=AssignmentResponse)
def accept_assignment(
    assignment_id: int,
    http_request: Request,
    background_tasks: BackgroundTasks,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
    expected_revision: int | None = Query(None, ge=1),
):
    """Record the caller's explicit acceptance of the current commitment."""
    assignment = _load_own_assignment(assignment_id, current_user, db)
    changed = _record_and_commit_response(
        db,
        assignment=assignment,
        user=current_user,
        http_request=http_request,
        action=AuditAction.ASSIGNMENT_ACCEPTED,
        response_status="accepted",
        workflow_status="confirmed",
        expected_revision=expected_revision,
    )
    if changed:
        _publish_assignment_change(background_tasks, assignment, current_user.org_id)
    return assignment


@router.post("/{assignment_id}/decline", response_model=AssignmentResponse)
def decline_assignment(
    assignment_id: int,
    body: AssignmentDeclineRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Decline the caller's assignment with a reason."""
    assignment = _load_own_assignment(assignment_id, current_user, db)
    changed = _record_and_commit_response(
        db,
        assignment=assignment,
        user=current_user,
        http_request=http_request,
        action=AuditAction.ASSIGNMENT_DECLINED,
        response_status="declined",
        workflow_status="declined",
        expected_revision=body.expected_revision,
        decline_reason=body.decline_reason,
        details={"decline_reason": body.decline_reason},
    )
    if changed:
        _publish_assignment_change(background_tasks, assignment, current_user.org_id)
    return assignment


@router.post("/{assignment_id}/swap-request", response_model=AssignmentResponse)
def request_swap(
    assignment_id: int,
    body: AssignmentSwapRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record that the caller needs a replacement for the current commitment."""
    assignment = _load_own_assignment(assignment_id, current_user, db)
    details = {"note": body.note} if body.note else {}
    changed = _record_and_commit_response(
        db,
        assignment=assignment,
        user=current_user,
        http_request=http_request,
        action=AuditAction.ASSIGNMENT_SWAP_REQUESTED,
        response_status="declined",
        workflow_status="swap_requested",
        expected_revision=body.expected_revision,
        decline_reason=body.note,
        details=details,
    )
    if changed:
        _publish_assignment_change(background_tasks, assignment, current_user.org_id)
    return assignment


@router.get("/me", response_model=ListResponse[AssignmentResponse])
def list_my_assignments(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return assignments belonging to the caller, scoped to their org via the join."""
    base = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Assignment.person_id == current_user.id,
            Event.org_id == current_user.org_id,
            member_visible_assignment(cast(str, current_user.org_id)),
        )
    )
    total = base.count()
    rows = (
        base.order_by(Assignment.assigned_at.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
        .all()
    )
    return {
        "items": rows,
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }
