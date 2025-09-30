"""Events router."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas.event import EventCreate, EventUpdate, EventResponse, EventList
from roster_cli.db.models import Event, EventTeam, Organization, Team

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event_data: EventCreate, db: Session = Depends(get_db)):
    """Create a new event."""
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == event_data.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{event_data.org_id}' not found",
        )

    # Check if event already exists
    existing = db.query(Event).filter(Event.id == event_data.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Event with ID '{event_data.id}' already exists",
        )

    # Validate times
    if event_data.end_time <= event_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    # Create event
    event = Event(
        id=event_data.id,
        org_id=event_data.org_id,
        type=event_data.type,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        resource_id=event_data.resource_id,
        extra_data=event_data.extra_data or {},
    )
    db.add(event)
    db.flush()

    # Add event teams
    if event_data.team_ids:
        for team_id in event_data.team_ids:
            # Verify team exists
            team = db.query(Team).filter(Team.id == team_id).first()
            if not team:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team '{team_id}' not found",
                )
            event_team = EventTeam(event_id=event.id, team_id=team_id)
            db.add(event_team)

    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=EventList)
def list_events(
    org_id: Optional[str] = Query(None, description="Filter by organization ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    start_after: Optional[datetime] = Query(None, description="Filter events starting after this time"),
    start_before: Optional[datetime] = Query(None, description="Filter events starting before this time"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List events with optional filters."""
    query = db.query(Event)

    if org_id:
        query = query.filter(Event.org_id == org_id)
    if event_type:
        query = query.filter(Event.type == event_type)
    if start_after:
        query = query.filter(Event.start_time >= start_after)
    if start_before:
        query = query.filter(Event.start_time <= start_before)

    query = query.order_by(Event.start_time)
    events = query.offset(skip).limit(limit).all()
    total = query.count()
    return {"events": events, "total": total}


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    """Get event by ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event '{event_id}' not found"
        )
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(event_id: str, event_data: EventUpdate, db: Session = Depends(get_db)):
    """Update event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event '{event_id}' not found"
        )

    # Update fields
    if event_data.type is not None:
        event.type = event_data.type
    if event_data.start_time is not None:
        event.start_time = event_data.start_time
    if event_data.end_time is not None:
        event.end_time = event_data.end_time
    if event_data.resource_id is not None:
        event.resource_id = event_data.resource_id
    if event_data.extra_data is not None:
        event.extra_data = event_data.extra_data

    # Validate times
    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: str, db: Session = Depends(get_db)):
    """Delete event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Event '{event_id}' not found"
        )

    db.delete(event)
    db.commit()
    return None
