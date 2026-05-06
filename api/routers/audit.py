"""Admin-only audit log read endpoint."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_admin_user
from api.models import AuditAction, AuditLog, Person
from api.schemas.audit import AuditLogResponse
from api.schemas.common import ListResponse, PaginationParams, get_pagination_params
from api.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=ListResponse[AuditLogResponse])
def list_audit_logs(
    http_request: Request,
    user_id: str | None = Query(None, description="Filter by user_id"),
    action: str | None = Query(None, description="Filter by action (e.g., auth.login.success)"),
    resource_type: str | None = Query(None, description="Filter by resource_type"),
    start_date: datetime | None = Query(None, description="Inclusive lower bound on timestamp"),
    end_date: datetime | None = Query(None, description="Inclusive upper bound on timestamp"),
    audit_status: str
    | None = Query(None, alias="status", description="success / failure / denied"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Return audit log rows scoped to the caller's organization.

    Admin-only. Each call is itself recorded as a `data.exported` audit event
    so reads of the audit log are themselves auditable.
    """
    query = db.query(AuditLog).filter(AuditLog.organization_id == current_admin.org_id)

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if action is not None:
        query = query.filter(AuditLog.action == action)
    if resource_type is not None:
        query = query.filter(AuditLog.resource_type == resource_type)
    if start_date is not None:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date is not None:
        query = query.filter(AuditLog.timestamp <= end_date)
    if audit_status is not None:
        query = query.filter(AuditLog.status == audit_status)

    total = query.count()
    rows = (
        query.order_by(AuditLog.timestamp.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
        .all()
    )

    log_audit_event(
        db,
        action=AuditAction.DATA_EXPORTED,
        user_id=current_admin.id,
        user_email=current_admin.email,
        organization_id=current_admin.org_id,
        resource_type="audit_log",
        details={
            "filters": {
                k: v
                for k, v in {
                    "user_id": user_id,
                    "action": action,
                    "resource_type": resource_type,
                    "status": audit_status,
                }.items()
                if v is not None
            },
            "limit": pagination.limit,
            "offset": pagination.offset,
            "result_count": len(rows),
        },
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
    )

    return {
        "items": rows,
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }
