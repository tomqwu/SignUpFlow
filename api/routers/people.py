"""People router."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_user, get_current_admin_user, verify_org_member, check_admin_permission
from api.schemas.person import PersonCreate, PersonUpdate, PersonResponse, PersonList
from api.models import Person, Organization
from api.logging_config import logger

router = APIRouter(prefix="/people", tags=["people"])


@router.get("/me", response_model=PersonResponse)
async def get_current_person(current_user: Person = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user


@router.put("/me", response_model=PersonResponse)
async def update_current_person(
    person_data: PersonUpdate,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current authenticated user's profile."""
    # Update allowed fields
    if person_data.name is not None:
        current_user.name = person_data.name
    if person_data.timezone is not None:
        current_user.timezone = person_data.timezone
    if person_data.language is not None:
        current_user.language = person_data.language
    if person_data.extra_data is not None:
        current_user.extra_data = person_data.extra_data

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def create_person(
    person_data: PersonCreate,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new person (admin only)."""
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == person_data.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{person_data.org_id}' not found",
        )

    # Verify admin belongs to the organization
    verify_org_member(current_admin, person_data.org_id)

    # Check if person already exists
    existing = db.query(Person).filter(Person.id == person_data.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Person with ID '{person_data.id}' already exists",
        )

    # Create person
    person = Person(
        id=person_data.id,
        org_id=person_data.org_id,
        name=person_data.name,
        email=person_data.email,
        roles=person_data.roles or [],
        timezone=person_data.timezone,
        extra_data=person_data.extra_data or {},
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.get("/", response_model=PersonList)
def list_people(
    org_id: Optional[str] = Query(None, description="Filter by organization ID"),
    role: Optional[str] = Query(None, description="Filter by role"),
    skip: int = 0,
    limit: int = 100,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List people. Users can only see people from their own organization."""
    query = db.query(Person)

    # Enforce organization isolation - users can only see people from their own org
    if org_id:
        # Verify user has access to this organization
        verify_org_member(current_user, org_id)
        query = query.filter(Person.org_id == org_id)
    else:
        # Default to current user's organization
        query = query.filter(Person.org_id == current_user.org_id)

    # Note: For JSON field filtering in SQLite, we'd need to load and filter in memory
    # For production with PostgreSQL, we could use JSON operators

    people = query.offset(skip).limit(limit).all()

    # Apply role filter in memory if specified
    if role:
        people = [p for p in people if p.roles and role in p.roles]

    total = query.count()
    return {"people": people, "total": total}


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: str,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get person by ID. Users can only view people from their own organization."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Person '{person_id}' not found"
        )

    # Verify user belongs to the same organization
    verify_org_member(current_user, person.org_id)

    return person


@router.put("/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: str,
    person_data: PersonUpdate,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update person. Users can edit themselves, admins can edit anyone in their org."""
    try:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Person '{person_id}' not found"
            )

        # Check permissions
        is_admin = check_admin_permission(current_user)
        is_self = current_user.id == person_id

        if not is_self and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own profile unless you are an admin"
            )

        # Admins can only edit people in their own organization
        if is_admin and not is_self:
            verify_org_member(current_user, person.org_id)

        # Prevent role escalation: non-admins cannot modify roles
        if person_data.roles is not None and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can modify user roles"
            )

        # Update fields
        if person_data.name is not None:
            person.name = person_data.name
        if person_data.email is not None:
            person.email = person_data.email
        if person_data.roles is not None:
            person.roles = person_data.roles
        if person_data.timezone is not None:
            person.timezone = person_data.timezone
        if person_data.language is not None:
            person.language = person_data.language
        if person_data.extra_data is not None:
            person.extra_data = person_data.extra_data

        db.commit()
        db.refresh(person)
        return person
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating person {person_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    person_id: str,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete person (admin only)."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Person '{person_id}' not found"
        )

    # Verify admin belongs to the same organization
    verify_org_member(current_admin, person.org_id)

    db.delete(person)
    db.commit()
    return None
