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

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_user
from api.models import Assignment, AuditAction, Event, Person
from api.schemas.assignment import (
    AssignmentDeclineRequest,
    AssignmentResponse,
    AssignmentSwapRequest,
)
from api.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/assignments", tags=["assignments"])


def _load_own_assignment(assignment_id: int, current_user: Person, db: Session) -> Assignment:
    """Load an assignment that belongs to the caller; 404 if missing, 403 if not theirs."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
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
    )


@router.post("/{assignment_id}/accept", response_model=AssignmentResponse)
def accept_assignment(
    assignment_id: int,
    http_request: Request,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark the caller's assignment as confirmed."""
    assignment = _load_own_assignment(assignment_id, current_user, db)
    assignment.status = "confirmed"
    assignment.decline_reason = None
    db.commit()
    db.refresh(assignment)
    _audit_status_change(
        db,
        action=AuditAction.ASSIGNMENT_ACCEPTED,
        user=current_user,
        assignment=assignment,
        http_request=http_request,
    )
    return assignment


@router.post("/{assignment_id}/decline", response_model=AssignmentResponse)
def decline_assignment(
    assignment_id: int,
    body: AssignmentDeclineRequest,
    http_request: Request,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Decline the caller's assignment with a reason."""
    assignment = _load_own_assignment(assignment_id, current_user, db)
    assignment.status = "declined"
    assignment.decline_reason = body.decline_reason
    db.commit()
    db.refresh(assignment)
    _audit_status_change(
        db,
        action=AuditAction.ASSIGNMENT_DECLINED,
        user=current_user,
        assignment=assignment,
        http_request=http_request,
        details={"decline_reason": body.decline_reason},
    )
    return assignment


@router.post("/{assignment_id}/swap-request", response_model=AssignmentResponse)
def request_swap(
    assignment_id: int,
    body: AssignmentSwapRequest,
    http_request: Request,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Flag the caller's assignment for swap; admin follows up out of band."""
    assignment = _load_own_assignment(assignment_id, current_user, db)
    assignment.status = "swap_requested"
    db.commit()
    db.refresh(assignment)
    details = {"note": body.note} if body.note else {}
    _audit_status_change(
        db,
        action=AuditAction.ASSIGNMENT_SWAP_REQUESTED,
        user=current_user,
        assignment=assignment,
        http_request=http_request,
        details=details,
    )
    return assignment


@router.get("/me", response_model=list[AssignmentResponse])
def list_my_assignments(
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return every assignment belonging to the caller, scoped to their org via the join."""
    rows = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Assignment.person_id == current_user.id,
            Event.org_id == current_user.org_id,
        )
        .order_by(Assignment.assigned_at.desc())
        .all()
    )
    return rows
