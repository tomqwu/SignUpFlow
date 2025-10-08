"""Shared FastAPI dependencies for authentication and authorization."""

from typing import Optional
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Person, Organization
from api.security import verify_token

# HTTP Bearer token security scheme
security = HTTPBearer()


def check_admin_permission(person: Person) -> bool:
    """Check if person has admin or super_admin role."""
    if not person or not person.roles:
        return False
    return "admin" in person.roles or "super_admin" in person.roles


def get_person_by_id(
    person_id: str,
    db: Session = Depends(get_db),
) -> Person:
    """Get person by ID or raise 404."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Person '{person_id}' not found"
        )
    return person


def get_organization_by_id(
    org_id: str,
    db: Session = Depends(get_db),
) -> Organization:
    """Get organization by ID or raise 404."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_id}' not found"
        )
    return org


def verify_admin_access(
    person_id: str = Query(..., description="Person ID"),
    db: Session = Depends(get_db),
) -> Person:
    """Verify person exists and has admin permissions."""
    person = get_person_by_id(person_id, db)
    if not check_admin_permission(person):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return person


def verify_org_member(
    person: Person,
    org_id: str,
) -> None:
    """Verify person belongs to the specified organization."""
    if person.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: not a member of this organization"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Person:
    """
    Get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        Person object of the authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = verify_token(token)

    # Extract person_id from token payload
    person_id: str = payload.get("sub")
    if person_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get person from database
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return person


async def get_current_admin_user(
    current_user: Person = Depends(get_current_user)
) -> Person:
    """
    Get current user and verify they have admin permissions.

    Args:
        current_user: Current authenticated user

    Returns:
        Person object if user is admin

    Raises:
        HTTPException: If user is not an admin
    """
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
