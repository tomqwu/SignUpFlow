"""Organization router."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationList,
)
from api.models import Organization
from api.utils.rate_limit_middleware import rate_limit
from api.utils.recaptcha_middleware import require_recaptcha
from api.services.billing_service import BillingService
from api.services.usage_service import UsageService
from api.logging_config import logger

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit("create_org")), Depends(require_recaptcha)])
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

    # Auto-create Free plan subscription
    billing_service = BillingService(db)
    subscription = billing_service.create_free_subscription(org.id)

    if subscription:
        # Initialize volunteer usage metrics (0/10 for Free plan)
        usage_service = UsageService(db)
        usage_service.track_volunteer_added(org.id)  # Will create metric with 0 volunteers
        logger.info(f"Free plan subscription created for org {org.id}")
    else:
        logger.error(f"Failed to create free subscription for org {org.id}")

    return org


@router.get("/", response_model=OrganizationList)
def list_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all organizations."""
    orgs = db.query(Organization).offset(skip).limit(limit).all()
    total = db.query(Organization).count()
    return {"organizations": orgs, "total": total}


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
def update_organization(
    org_id: str, org_data: OrganizationUpdate, db: Session = Depends(get_db)
):
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
