"""Calendar export and subscription endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.database import get_db
from api.utils.calendar_utils import (
    generate_calendar_token,
    generate_ics_from_assignments,
    generate_ics_from_events,
    generate_webcal_url,
    generate_https_feed_url,
)
from roster_cli.db.models import Person, Assignment, Event, Resource, Organization

router = APIRouter(prefix="/calendar", tags=["calendar"])


# Schemas
class CalendarSubscriptionResponse(BaseModel):
    """Calendar subscription response."""
    token: str
    webcal_url: str
    https_url: str
    message: str


class CalendarTokenResetResponse(BaseModel):
    """Calendar token reset response."""
    token: str
    webcal_url: str
    https_url: str
    message: str


# Helper function to get base URL
def get_base_url(request: Request) -> str:
    """Extract base URL from request."""
    scheme = request.url.scheme
    host = request.headers.get("host", f"{request.url.hostname}:{request.url.port}")
    return f"{scheme}://{host}"


@router.get("/export")
def export_personal_schedule(
    person_id: str,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Export personal schedule as ICS file.

    This endpoint downloads an ICS file with all assigned events for a person.
    """
    # Verify person exists
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Person '{person_id}' not found",
        )

    # Get all assignments for this person
    assignments = db.query(Assignment).filter(Assignment.person_id == person_id).all()

    if not assignments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assignments found for this person",
        )

    # Load event and resource data for each assignment
    assignment_data = []
    for assignment in assignments:
        event = db.query(Event).filter(Event.id == assignment.event_id).first()
        if not event:
            continue

        resource = None
        if event.resource_id:
            resource = db.query(Resource).filter(Resource.id == event.resource_id).first()

        assignment_data.append({
            "id": assignment.id,
            "person": {
                "id": person.id,
                "name": person.name,
            },
            "event": {
                "id": event.id,
                "type": event.type,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "extra_data": event.extra_data or {},
                "resource": {
                    "location": resource.location if resource else "TBD",
                } if resource else None,
            },
            "role": assignment.role,  # Event-specific role (usher, greeter, etc.)
        })

    # Generate ICS file
    calendar_name = f"{person.name}'s Schedule"
    ics_content = generate_ics_from_assignments(
        assignment_data,
        calendar_name=calendar_name,
        timezone=person.timezone,
    )

    # Return as downloadable file
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename={person_id}_schedule.ics"
        },
    )


@router.get("/subscribe")
def get_subscription_url(
    person_id: str,
    db: Session = Depends(get_db),
    request: Request = None,
) -> CalendarSubscriptionResponse:
    """
    Get calendar subscription URL for a person.

    Returns a webcal:// URL that can be used to subscribe to the calendar
    in Google Calendar, Apple Calendar, Outlook, etc.
    """
    # Verify person exists
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Person '{person_id}' not found",
        )

    # Generate calendar token if not exists
    if not person.calendar_token:
        person.calendar_token = generate_calendar_token()
        db.commit()
        db.refresh(person)

    # Get base URL
    base_url = get_base_url(request) if request else "http://localhost:8000"

    # Generate subscription URLs
    webcal_url = generate_webcal_url(base_url, person.calendar_token)
    https_url = generate_https_feed_url(base_url, person.calendar_token)

    return CalendarSubscriptionResponse(
        token=person.calendar_token,
        webcal_url=webcal_url,
        https_url=https_url,
        message="Use this URL to subscribe to your calendar in your calendar app",
    )


@router.post("/reset-token")
def reset_calendar_token(
    person_id: str,
    db: Session = Depends(get_db),
    request: Request = None,
) -> CalendarTokenResetResponse:
    """
    Reset calendar subscription token for a person.

    This invalidates the old subscription URL and generates a new one.
    Use this if the subscription URL has been compromised.
    """
    # Verify person exists
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Person '{person_id}' not found",
        )

    # Generate new token
    person.calendar_token = generate_calendar_token()
    db.commit()
    db.refresh(person)

    # Get base URL
    base_url = get_base_url(request) if request else "http://localhost:8000"

    # Generate new subscription URLs
    webcal_url = generate_webcal_url(base_url, person.calendar_token)
    https_url = generate_https_feed_url(base_url, person.calendar_token)

    return CalendarTokenResetResponse(
        token=person.calendar_token,
        webcal_url=webcal_url,
        https_url=https_url,
        message="Calendar token has been reset. Update your calendar subscription with the new URL.",
    )


@router.get("/org/export")
def export_organization_events(
    org_id: str,
    person_id: str,  # For auth - must be admin
    include_assignments: bool = True,
    db: Session = Depends(get_db),
):
    """
    Export all organization events as ICS file (admin only).

    This endpoint is for administrators to export all events in the organization.
    """
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{org_id}' not found",
        )

    # Verify person exists and is admin
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person or person.org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required.",
        )

    # Check if person is admin
    if not person.roles or "admin" not in person.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required.",
        )

    # Get all events for this organization
    events = db.query(Event).filter(Event.org_id == org_id).all()

    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No events found for this organization",
        )

    # Load event data with resources and assignments
    event_data = []
    for event in events:
        resource = None
        if event.resource_id:
            resource = db.query(Resource).filter(Resource.id == event.resource_id).first()

        event_dict = {
            "id": event.id,
            "type": event.type,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "extra_data": event.extra_data or {},
            "resource": {
                "location": resource.location if resource else "TBD",
            } if resource else None,
        }

        # Add assignments if requested
        if include_assignments:
            assignments = db.query(Assignment).filter(Assignment.event_id == event.id).all()
            event_dict["assignments"] = []
            for assignment in assignments:
                person_assigned = db.query(Person).filter(Person.id == assignment.person_id).first()
                if person_assigned:
                    event_dict["assignments"].append({
                        "person": {
                            "name": person_assigned.name,
                        },
                        "role": None,  # Could be extracted from extra_data
                    })

        event_data.append(event_dict)

    # Generate ICS file
    calendar_name = f"{org.name} - All Events"
    ics_content = generate_ics_from_events(
        event_data,
        calendar_name=calendar_name,
        timezone="UTC",
        include_assignments=include_assignments,
    )

    # Return as downloadable file
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename={org_id}_events.ics"
        },
    )


@router.get("/feed/{token}")
def calendar_feed(token: str, db: Session = Depends(get_db)):
    """
    Public calendar feed endpoint for subscriptions.

    This endpoint is accessed by calendar applications using the subscription URL.
    It returns an ICS file that is automatically refreshed by the calendar app.
    """
    # Find person by calendar token
    person = db.query(Person).filter(Person.calendar_token == token).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid calendar token",
        )

    # Get all assignments for this person
    assignments = db.query(Assignment).filter(Assignment.person_id == person.id).all()

    # Load event and resource data for each assignment
    assignment_data = []
    for assignment in assignments:
        event = db.query(Event).filter(Event.id == assignment.event_id).first()
        if not event:
            continue

        resource = None
        if event.resource_id:
            resource = db.query(Resource).filter(Resource.id == event.resource_id).first()

        assignment_data.append({
            "id": assignment.id,
            "person": {
                "id": person.id,
                "name": person.name,
            },
            "event": {
                "id": event.id,
                "type": event.type,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "extra_data": event.extra_data or {},
                "resource": {
                    "location": resource.location if resource else "TBD",
                } if resource else None,
            },
            "role": assignment.role,  # Event-specific role (usher, greeter, etc.)
        })

    # Generate ICS file
    calendar_name = f"{person.name}'s Schedule"
    ics_content = generate_ics_from_assignments(
        assignment_data,
        calendar_name=calendar_name,
        timezone=person.timezone,
    )

    # Return ICS file with proper headers for calendar subscription
    return Response(
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": "inline; filename=schedule.ics",
            "Cache-Control": "no-cache, must-revalidate",
        },
    )
