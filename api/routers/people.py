"""People router."""


from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import (
    check_admin_permission,
    get_current_admin_user,
    get_current_user,
    verify_org_member,
)
from api.logging_config import logger
from api.models import AuditAction, Organization, Person
from api.schemas.common import PaginationParams, get_pagination_params
from api.schemas.person import PersonCreate, PersonList, PersonResponse, PersonUpdate
from api.utils.audit_logger import log_audit_event
from api.utils.bulk_import import (
    MAX_BULK_IMPORT_ITEMS,
    BulkImportError,
    parse_bulk_people,
)

router = APIRouter(prefix="/people", tags=["people"])


class BulkImportItemError(BaseModel):
    """One row that the bulk importer rejected."""

    index: int = Field(..., description="Position in the original payload (0-based)")
    id: str | None = Field(None, description="Row id, if present")
    reason: str = Field(..., description="Why this row was rejected")


class BulkImportResponse(BaseModel):
    """Result of a bulk people import request."""

    created: int
    skipped: int
    errors: list[BulkImportItemError]


def _to_response_error(err: BulkImportError) -> BulkImportItemError:
    return BulkImportItemError(index=err.index, id=err.id, reason=err.reason)


@router.get("/me", response_model=PersonResponse)
async def get_current_person(current_user: Person = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user


@router.put("/me", response_model=PersonResponse)
async def update_current_person(
    person_data: PersonUpdate,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
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


@router.post("/bulk", response_model=BulkImportResponse, status_code=status.HTTP_200_OK)
def bulk_import_people(
    http_request: Request,
    payload: dict = Body(
        ...,
        description=(
            "JSON-array bulk import. Body shape: {items: [PersonCreate, ...]}. "
            f"Cap of {MAX_BULK_IMPORT_ITEMS} items per request."
        ),
    ),
    org_id: str = Query(..., description="Organization to import people into"),
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Admin-only bulk people import.

    Strictly JSON-array body — no file upload (file uploads are Phase 2 scope).
    Validates each row, persists rows that don't already exist, and returns
    created/skipped counts plus a row-level error list.
    """
    verify_org_member(current_admin, org_id)

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_id}' not found",
        )

    items = payload.get("items")
    if not isinstance(items, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="payload must contain an 'items' array",
        )
    if len(items) > MAX_BULK_IMPORT_ITEMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"items length {len(items)} exceeds cap of {MAX_BULK_IMPORT_ITEMS}",
        )

    parsed = parse_bulk_people(items, expected_org_id=org_id)
    response_errors = [_to_response_error(e) for e in parsed.errors]

    created = 0
    skipped = len(parsed.duplicate_indexes)
    candidate_ids = [p.id for p in parsed.valid]
    existing_ids: set[str] = set()
    if candidate_ids:
        existing_ids = {
            row[0] for row in db.query(Person.id).filter(Person.id.in_(candidate_ids)).all()
        }

    for person_data in parsed.valid:
        if person_data.id in existing_ids:
            skipped += 1
            continue
        person = Person(
            id=person_data.id,
            org_id=org_id,
            name=person_data.name,
            email=person_data.email,
            roles=person_data.roles or [],
            timezone=person_data.timezone,
            language=person_data.language,
            extra_data=person_data.extra_data or {},
        )
        db.add(person)
        created += 1

    db.commit()

    log_audit_event(
        db,
        action=AuditAction.BULK_IMPORT,
        user_id=current_admin.id,
        user_email=current_admin.email,
        organization_id=org_id,
        resource_type="person",
        resource_id=None,
        details={
            "created": created,
            "skipped": skipped,
            "error_count": len(response_errors),
            "submitted": len(items),
        },
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
    )

    return BulkImportResponse(created=created, skipped=skipped, errors=response_errors)


@router.get("/", response_model=PersonList)
def list_people(
    org_id: str | None = Query(None, description="Filter by organization ID"),
    role: str | None = Query(None, description="Filter by role"),
    q: str | None = Query(None, description="Case-insensitive search across name and email"),
    status_filter: str
    | None = Query(
        None, alias="status", description="Filter by Person.status (active/inactive/invited)"
    ),
    pagination: PaginationParams = Depends(get_pagination_params),
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

    if q:
        like = f"%{q}%"
        query = query.filter(or_(Person.name.ilike(like), Person.email.ilike(like)))

    if status_filter:
        query = query.filter(Person.status == status_filter)

    # Note: For JSON field filtering in SQLite, we'd need to load and filter in memory
    # For production with PostgreSQL, we could use JSON operators

    people = query.offset(pagination.offset).limit(pagination.limit).all()

    # Apply role filter in memory if specified
    if role:
        people = [p for p in people if p.roles and role in p.roles]

    total = query.count()
    return {
        "items": people,
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: str, current_user: Person = Depends(get_current_user), db: Session = Depends(get_db)
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
    db: Session = Depends(get_db),
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
                detail="You can only edit your own profile unless you are an admin",
            )

        # Admins can only edit people in their own organization
        if is_admin and not is_self:
            verify_org_member(current_user, person.org_id)

        # Prevent role escalation: non-admins cannot modify roles
        if person_data.roles is not None and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can modify user roles"
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
    db: Session = Depends(get_db),
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
