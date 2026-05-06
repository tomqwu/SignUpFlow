"""Resources router — CRUD on venues / rooms / equipment.

Reads require authenticated org membership; writes (create/update/delete)
require admin in the target org. The solver already consumes the data at
solve time; this router lets admins seed it via the API.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_admin_user, get_current_user, verify_org_member
from api.models import Event, Organization, Person, Resource
from api.schemas.common import PaginationParams, get_pagination_params
from api.schemas.resource import (
    ResourceCreate,
    ResourceList,
    ResourceResponse,
    ResourceUpdate,
)

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(
    resource_data: ResourceCreate,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Create a new resource (admin only, scoped to admin's org)."""
    verify_org_member(current_admin, resource_data.org_id)

    org = db.query(Organization).filter(Organization.id == resource_data.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{resource_data.org_id}' not found",
        )

    if db.query(Resource).filter(Resource.id == resource_data.id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Resource with ID '{resource_data.id}' already exists",
        )

    resource = Resource(
        id=resource_data.id,
        org_id=resource_data.org_id,
        type=resource_data.type,
        location=resource_data.location,
        capacity=resource_data.capacity,
        extra_data=resource_data.extra_data or {},
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get("/", response_model=ResourceList)
def list_resources(
    org_id: str = Query(..., description="Organization ID — required (single-tenant scope)"),
    type: str | None = Query(None, description="Filter by resource type"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List resources for one organization. Caller must be a member."""
    verify_org_member(current_user, org_id)

    query = db.query(Resource).filter(Resource.org_id == org_id)
    if type is not None:
        query = query.filter(Resource.type == type)

    total = query.count()
    rows = (
        query.order_by(Resource.created_at.desc())
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


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: str,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single resource by id; tenancy enforced via the row's org_id."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource '{resource_id}' not found",
        )
    verify_org_member(current_user, resource.org_id)
    return resource


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: str,
    update: ResourceUpdate,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Update a resource (admin only). org_id is immutable."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource '{resource_id}' not found",
        )
    verify_org_member(current_admin, resource.org_id)

    if update.type is not None:
        resource.type = update.type
    if update.location is not None:
        resource.location = update.location
    if update.capacity is not None:
        resource.capacity = update.capacity
    if update.extra_data is not None:
        resource.extra_data = update.extra_data

    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: str,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete a resource (admin only).

    Refuses with 409 if any Event still references the resource — preserves
    referential integrity without forcing the admin to discover dangling FKs
    by surprise.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource '{resource_id}' not found",
        )
    verify_org_member(current_admin, resource.org_id)

    referenced = (
        db.query(Event)
        .filter(Event.resource_id == resource_id, Event.org_id == resource.org_id)
        .count()
    )
    if referenced > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Resource '{resource_id}' is referenced by {referenced} event(s); "
                "reassign or delete those events first"
            ),
        )

    db.delete(resource)
    db.commit()
    return None
