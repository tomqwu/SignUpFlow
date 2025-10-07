"""Constraints router."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas.constraint import (
    ConstraintCreate,
    ConstraintUpdate,
    ConstraintResponse,
    ConstraintList,
)
from api.models import Constraint, Organization

router = APIRouter(prefix="/constraints", tags=["constraints"])


@router.post("/", response_model=ConstraintResponse, status_code=status.HTTP_201_CREATED)
def create_constraint(constraint_data: ConstraintCreate, db: Session = Depends(get_db)):
    """Create a new constraint."""
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == constraint_data.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{constraint_data.org_id}' not found",
        )

    # Validate constraint type
    if constraint_data.type not in ["hard", "soft"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Constraint type must be 'hard' or 'soft'",
        )

    # Create constraint
    constraint = Constraint(
        org_id=constraint_data.org_id,
        key=constraint_data.key,
        type=constraint_data.type,
        weight=constraint_data.weight,
        predicate=constraint_data.predicate,
        params=constraint_data.params or {},
    )
    db.add(constraint)
    db.commit()
    db.refresh(constraint)
    return constraint


@router.get("/", response_model=ConstraintList)
def list_constraints(
    org_id: Optional[str] = Query(None, description="Filter by organization ID"),
    constraint_type: Optional[str] = Query(None, description="Filter by type (hard/soft)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List constraints with optional filters."""
    query = db.query(Constraint)

    if org_id:
        query = query.filter(Constraint.org_id == org_id)
    if constraint_type:
        query = query.filter(Constraint.type == constraint_type)

    constraints = query.offset(skip).limit(limit).all()
    total = query.count()
    return {"constraints": constraints, "total": total}


@router.get("/{constraint_id}", response_model=ConstraintResponse)
def get_constraint(constraint_id: int, db: Session = Depends(get_db)):
    """Get constraint by ID."""
    constraint = db.query(Constraint).filter(Constraint.id == constraint_id).first()
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Constraint {constraint_id} not found",
        )
    return constraint


@router.put("/{constraint_id}", response_model=ConstraintResponse)
def update_constraint(
    constraint_id: int, constraint_data: ConstraintUpdate, db: Session = Depends(get_db)
):
    """Update constraint."""
    constraint = db.query(Constraint).filter(Constraint.id == constraint_id).first()
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Constraint {constraint_id} not found",
        )

    # Update fields
    if constraint_data.type is not None:
        if constraint_data.type not in ["hard", "soft"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Constraint type must be 'hard' or 'soft'",
            )
        constraint.type = constraint_data.type
    if constraint_data.weight is not None:
        constraint.weight = constraint_data.weight
    if constraint_data.predicate is not None:
        constraint.predicate = constraint_data.predicate
    if constraint_data.params is not None:
        constraint.params = constraint_data.params

    db.commit()
    db.refresh(constraint)
    return constraint


@router.delete("/{constraint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_constraint(constraint_id: int, db: Session = Depends(get_db)):
    """Delete constraint."""
    constraint = db.query(Constraint).filter(Constraint.id == constraint_id).first()
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Constraint {constraint_id} not found",
        )

    db.delete(constraint)
    db.commit()
    return None
