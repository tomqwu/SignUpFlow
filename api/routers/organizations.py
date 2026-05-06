"""Organization router."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_admin_user, verify_org_member
from api.models import AuditAction, Organization, Person
from api.schemas.common import PaginationParams, get_pagination_params
from api.schemas.organization import (
    OrganizationCreate,
    OrganizationList,
    OrganizationResponse,
    OrganizationUpdate,
)
from api.timeutils import utcnow
from api.utils.audit_logger import log_audit_event
from api.utils.rate_limit_middleware import rate_limit

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("create_org"))],
)
def create_organization(org_data: OrganizationCreate, db: Session = Depends(get_db)):
    """Create a new organization. Rate limited to 2 requests per hour per IP.

    Automatically creates Free plan subscription with 10 volunteer limit.
    """
    # Check if organization already exists
    existing = db.query(Organization).filter(Organization.id == org_data.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Organization with ID '{org_data.id}' already exists",
        )

    # Create organization
    org = Organization(
        id=org_data.id,
        name=org_data.name,
        region=org_data.region,
        config=org_data.config or {},
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    return org


@router.get("/", response_model=OrganizationList)
def list_organizations(
    include_cancelled: bool = Query(
        False, description="Include organizations that have been cancelled (admin view)"
    ),
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    """List all organizations. Excludes cancelled by default."""
    query = db.query(Organization)
    if not include_cancelled:
        query = query.filter(Organization.cancelled_at.is_(None))

    orgs = query.offset(pagination.offset).limit(pagination.limit).all()
    total = query.count()
    return {
        "items": orgs,
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: str, db: Session = Depends(get_db)):
    """Get organization by ID."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_id}' not found",
        )
    return org


@router.put("/{org_id}", response_model=OrganizationResponse)
def update_organization(org_id: str, org_data: OrganizationUpdate, db: Session = Depends(get_db)):
    """Update organization."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_id}' not found",
        )

    # Update fields
    if org_data.name is not None:
        org.name = org_data.name
    if org_data.region is not None:
        org.region = org_data.region
    if org_data.config is not None:
        org.config = org_data.config

    db.commit()
    db.refresh(org)
    return org


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(org_id: str, db: Session = Depends(get_db)):
    """Delete organization and all related data."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_id}' not found",
        )

    db.delete(org)
    db.commit()
    return None


@router.post("/{org_id}/cancel", response_model=OrganizationResponse)
def cancel_organization(
    org_id: str,
    http_request: Request,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Soft-cancel the organization (admin only).

    Sets `cancelled_at` to now and schedules a 30-day data-retention window
    via `data_retention_until`. The org is excluded from the default list
    until restored.
    """
    verify_org_member(current_admin, org_id)
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_id}' not found",
        )

    now = utcnow()
    org.cancelled_at = now
    org.data_retention_until = now + timedelta(days=30)
    db.commit()
    db.refresh(org)

    log_audit_event(
        db,
        action=AuditAction.ORG_CANCELLED,
        user_id=current_admin.id,
        user_email=current_admin.email,
        organization_id=org_id,
        resource_type="organization",
        resource_id=org_id,
        details={"data_retention_until": org.data_retention_until.isoformat()},
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
    )
    return org


@router.post("/{org_id}/restore", response_model=OrganizationResponse)
def restore_organization(
    org_id: str,
    http_request: Request,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Restore a cancelled organization (admin only). Clears cancellation fields."""
    verify_org_member(current_admin, org_id)
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_id}' not found",
        )

    org.cancelled_at = None
    org.data_retention_until = None
    org.deletion_scheduled_at = None
    db.commit()
    db.refresh(org)

    log_audit_event(
        db,
        action=AuditAction.ORG_RESTORED,
        user_id=current_admin.id,
        user_email=current_admin.email,
        organization_id=org_id,
        resource_type="organization",
        resource_id=org_id,
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
    )
    return org
