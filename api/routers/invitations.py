"""Invitation endpoints for user onboarding."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import time

from api.database import get_db
from api.dependencies import verify_admin_access, verify_org_member, get_organization_by_id, get_current_admin_user
from api.utils.security import generate_invitation_token, generate_auth_token, hash_password
from api.utils.db_helpers import check_email_exists
from api.utils.rate_limit_middleware import rate_limit
from api.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationList,
    InvitationVerify,
    InvitationAccept,
    InvitationAcceptResponse,
)
from api.models import Invitation, Person, Organization
from api.services.email_service import email_service

router = APIRouter(prefix="/invitations", tags=["invitations"])


# Endpoints
@router.post("", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit("create_invitation"))])
def create_invitation(
    request: InvitationCreate,
    org_id: str = Query(..., description="Organization ID"),
    inviter: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Create a new invitation (admin only). Rate limited to 10 requests per 5 minutes per IP.

    Sends an invitation email to a new user to join the organization.
    """
    # Verify organization exists
    org = get_organization_by_id(org_id, db)

    # Verify inviter belongs to the organization
    verify_org_member(inviter, org_id)

    # Check if email already exists
    if check_email_exists(db, request.email, org_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists in this organization"
        )

    # Check if there's already a pending invitation
    existing_invitation = db.query(Invitation).filter(
        Invitation.email == request.email,
        Invitation.org_id == org_id,
        Invitation.status == "pending"
    ).first()
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending invitation already exists for this email"
        )

    # Create invitation
    invitation_id = f"inv_{int(time.time())}_{secrets.token_hex(4)}"
    token = generate_invitation_token()
    expires_at = datetime.utcnow() + timedelta(days=7)  # 7 day expiry

    invitation = Invitation(
        id=invitation_id,
        org_id=org_id,
        email=request.email,
        name=request.name,
        roles=request.roles,
        invited_by=inviter.id,
        token=token,
        status="pending",
        expires_at=expires_at,
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # Send invitation email
    email_sent = email_service.send_invitation_email(
        to_email=request.email,
        admin_name=inviter.name,
        org_name=org.name,
        invitation_token=token,
        app_url="http://localhost:8000"  # TODO: Use environment variable for production
    )

    if not email_sent:
        # Log warning but don't fail the invitation creation
        # (invitation can still be accepted via direct link)
        import logging
        logger = logging.getLogger("invitations")
        logger.warning(f"Failed to send invitation email to {request.email}")

    return invitation


@router.get("", response_model=InvitationList)
async def list_invitations(
    org_id: str = Query(..., description="Organization ID"),
    admin: Person = Depends(get_current_admin_user),
    status_filter: Optional[str] = Query(None, description="Filter by status (pending, accepted, expired, cancelled)"),
    db: Session = Depends(get_db),
):
    """
    List all invitations for an organization (admin only).

    Requires JWT authentication via Authorization header.
    """
    # Verify admin belongs to the organization
    verify_org_member(admin, org_id)

    # Build query
    query = db.query(Invitation).filter(Invitation.org_id == org_id)

    if status_filter:
        query = query.filter(Invitation.status == status_filter)

    # Update expired invitations
    now = datetime.utcnow()
    expired_invitations = query.filter(
        Invitation.status == "pending",
        Invitation.expires_at < now
    ).all()

    for inv in expired_invitations:
        inv.status = "expired"

    if expired_invitations:
        db.commit()

    invitations = query.order_by(Invitation.created_at.desc()).all()

    return InvitationList(
        invitations=invitations,
        total=len(invitations)
    )


@router.get("/{token}", response_model=InvitationVerify, dependencies=[Depends(rate_limit("verify_invitation"))])
def verify_invitation(token: str, db: Session = Depends(get_db)):
    """
    Verify an invitation token. Rate limited to 10 requests per minute per IP.

    Checks if the invitation is valid and not expired.
    """
    invitation = db.query(Invitation).filter(Invitation.token == token).first()

    if not invitation:
        return InvitationVerify(
            valid=False,
            message="Invalid invitation token"
        )

    if invitation.status != "pending":
        return InvitationVerify(
            valid=False,
            invitation=invitation,
            message=f"Invitation is {invitation.status}"
        )

    if invitation.expires_at < datetime.utcnow():
        invitation.status = "expired"
        db.commit()
        return InvitationVerify(
            valid=False,
            invitation=invitation,
            message="Invitation has expired"
        )

    return InvitationVerify(
        valid=True,
        invitation=invitation,
        message="Invitation is valid"
    )


@router.post("/{token}/accept", response_model=InvitationAcceptResponse, status_code=status.HTTP_201_CREATED)
def accept_invitation(
    token: str,
    request: InvitationAccept,
    db: Session = Depends(get_db),
):
    """
    Accept an invitation and create a new account.

    This creates a new Person with the invited roles and marks the invitation as accepted.
    """
    # Verify invitation
    invitation = db.query(Invitation).filter(Invitation.token == token).first()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invitation token"
        )

    if invitation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation is {invitation.status}"
        )

    if invitation.expires_at < datetime.utcnow():
        invitation.status = "expired"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )

    # Check if email already exists (race condition check)
    existing_person = db.query(Person).filter(
        Person.email == invitation.email,
        Person.org_id == invitation.org_id
    ).first()
    if existing_person:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    # Create person
    person_id = f"person_{invitation.email.split('@')[0]}_{int(time.time())}"
    password_hash = hash_password(request.password)

    person = Person(
        id=person_id,
        org_id=invitation.org_id,
        name=invitation.name,
        email=invitation.email,
        password_hash=password_hash,
        roles=invitation.roles,
        timezone=request.timezone,
        status="active",
        invited_by=invitation.invited_by,
        extra_data={}
    )

    db.add(person)

    # Update invitation status
    invitation.status = "accepted"
    invitation.accepted_at = datetime.utcnow()

    db.commit()
    db.refresh(person)

    # Generate auth token for immediate login
    auth_token = generate_auth_token()

    return InvitationAcceptResponse(
        person_id=person.id,
        org_id=person.org_id,
        name=person.name,
        email=person.email,
        roles=person.roles or [],
        timezone=person.timezone,
        token=auth_token,
        message="Account created successfully. You are now logged in."
    )


@router.delete("/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_invitation(
    invitation_id: str,
    admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Cancel a pending invitation (admin only).
    """
    # Get invitation
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    # Verify admin belongs to the same organization
    verify_org_member(admin, invitation.org_id)

    # Cancel invitation
    if invitation.status == "pending":
        invitation.status = "cancelled"
        db.commit()

    return None


@router.post("/{invitation_id}/resend", response_model=InvitationResponse)
def resend_invitation(
    invitation_id: str,
    admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Resend an invitation email (admin only).

    Generates a new token and extends the expiry date.
    """
    # Get invitation
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    # Verify admin belongs to the same organization
    verify_org_member(admin, invitation.org_id)

    # Can only resend pending or expired invitations
    if invitation.status not in ["pending", "expired"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot resend {invitation.status} invitations"
        )

    # Generate new token and extend expiry
    invitation.token = generate_invitation_token()
    invitation.expires_at = datetime.utcnow() + timedelta(days=7)
    invitation.status = "pending"

    db.commit()
    db.refresh(invitation)

    # TODO: Send invitation email with new token
    # This would integrate with an email service in production

    return invitation
