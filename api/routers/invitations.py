"""Invitation endpoints for user onboarding."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import time
import hashlib

from api.database import get_db
from api.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationList,
    InvitationVerify,
    InvitationAccept,
    InvitationAcceptResponse,
)
from roster_cli.db.models import Invitation, Person, Organization

router = APIRouter(prefix="/invitations", tags=["invitations"])


# Helper functions
def generate_invitation_token() -> str:
    """Generate a unique invitation token."""
    return secrets.token_urlsafe(32)


def generate_auth_token() -> str:
    """Generate a simple session token."""
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def check_admin_permission(person: Person) -> bool:
    """Check if person has admin or super_admin role."""
    if not person or not person.roles:
        return False
    return "admin" in person.roles or "super_admin" in person.roles


# Endpoints
@router.post("", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def create_invitation(
    request: InvitationCreate,
    org_id: str = Query(..., description="Organization ID"),
    invited_by_id: str = Query(..., description="Person ID of the inviter"),
    db: Session = Depends(get_db),
):
    """
    Create a new invitation (admin only).

    Sends an invitation email to a new user to join the organization.
    """
    # Verify inviter exists and has admin permissions
    inviter = db.query(Person).filter(Person.id == invited_by_id).first()
    if not inviter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inviter not found"
        )

    if not check_admin_permission(inviter):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can send invitations"
        )

    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Verify inviter belongs to the organization
    if inviter.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot invite users to a different organization"
        )

    # Check if email already exists
    existing_person = db.query(Person).filter(
        Person.email == request.email,
        Person.org_id == org_id
    ).first()
    if existing_person:
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
        invited_by=invited_by_id,
        token=token,
        status="pending",
        expires_at=expires_at,
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # TODO: Send invitation email with token
    # This would integrate with an email service in production
    # For now, the token is returned in the response

    return invitation


@router.get("", response_model=InvitationList)
def list_invitations(
    org_id: str = Query(..., description="Organization ID"),
    person_id: str = Query(..., description="Person ID requesting the list"),
    status_filter: Optional[str] = Query(None, description="Filter by status (pending, accepted, expired, cancelled)"),
    db: Session = Depends(get_db),
):
    """
    List all invitations for an organization (admin only).
    """
    # Verify person exists and has admin permissions
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )

    if not check_admin_permission(person):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view invitations"
        )

    # Verify person belongs to the organization
    if person.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view invitations for a different organization"
        )

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


@router.get("/{token}", response_model=InvitationVerify)
def verify_invitation(token: str, db: Session = Depends(get_db)):
    """
    Verify an invitation token.

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
    person_id: str = Query(..., description="Person ID requesting cancellation"),
    db: Session = Depends(get_db),
):
    """
    Cancel a pending invitation (admin only).
    """
    # Verify person exists and has admin permissions
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )

    if not check_admin_permission(person):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can cancel invitations"
        )

    # Get invitation
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    # Verify person belongs to the same organization
    if person.org_id != invitation.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot cancel invitations for a different organization"
        )

    # Cancel invitation
    if invitation.status == "pending":
        invitation.status = "cancelled"
        db.commit()

    return None


@router.post("/{invitation_id}/resend", response_model=InvitationResponse)
def resend_invitation(
    invitation_id: str,
    person_id: str = Query(..., description="Person ID requesting resend"),
    db: Session = Depends(get_db),
):
    """
    Resend an invitation email (admin only).

    Generates a new token and extends the expiry date.
    """
    # Verify person exists and has admin permissions
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )

    if not check_admin_permission(person):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can resend invitations"
        )

    # Get invitation
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    # Verify person belongs to the same organization
    if person.org_id != invitation.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot resend invitations for a different organization"
        )

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
