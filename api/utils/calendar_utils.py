"""
Calendar utilities for ICS file generation and subscription URLs.

This module handles:
- Generating ICS calendar files from events and assignments
- Creating unique calendar subscription tokens
- Building webcal:// subscription URLs
"""

import secrets
from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event as ICalEvent, vText
from icalendar import vCalAddress, vDatetime


def generate_calendar_token() -> str:
    """
    Generate a unique, secure token for calendar subscriptions.

    Returns:
        A 32-character hexadecimal token
    """
    return secrets.token_hex(32)


def generate_ics_from_assignments(
    assignments: List[dict],
    calendar_name: str = "My Schedule",
    timezone: str = "UTC"
) -> str:
    """
    Generate an ICS calendar file from a list of assignments.

    Args:
        assignments: List of assignment dicts with event data
        calendar_name: Name of the calendar
        timezone: Timezone for the events (default: UTC)

    Returns:
        ICS file content as string
    """
    cal = Calendar()
    cal.add('prodid', '-//Rostio//Calendar Export//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', calendar_name)
    cal.add('x-wr-timezone', timezone)

    for assignment in assignments:
        event = ICalEvent()

        # Required fields
        event_data = assignment.get('event', {})
        event.add('uid', f"rostio-assignment-{assignment.get('id')}@rostio.app")
        event.add('dtstamp', datetime.utcnow().replace(tzinfo=ZoneInfo('UTC')))

        # Event times
        start_time = event_data.get('start_time')
        end_time = event_data.get('end_time')

        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

        # Ensure timezone-aware
        if start_time and start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=ZoneInfo('UTC'))
        if end_time and end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=ZoneInfo('UTC'))

        event.add('dtstart', vDatetime(start_time))
        event.add('dtend', vDatetime(end_time))

        # Event details
        event_type = event_data.get('type', 'Event')
        person_name = assignment.get('person', {}).get('name', 'You')

        # Summary (title)
        summary = f"{event_type}"
        if assignment.get('role'):
            summary = f"{event_type} - {assignment.get('role')}"
        event.add('summary', summary)

        # Description
        description_parts = []
        if assignment.get('role'):
            description_parts.append(f"Role: {assignment.get('role')}")
        description_parts.append(f"Assigned to: {person_name}")

        extra_data = event_data.get('extra_data', {})
        if extra_data.get('notes'):
            description_parts.append(f"\nNotes: {extra_data['notes']}")

        event.add('description', '\n'.join(description_parts))

        # Location
        resource = event_data.get('resource', {})
        if resource:
            location = resource.get('location', '')
            event.add('location', location)

        # Status
        event.add('status', 'CONFIRMED')

        # Add to calendar
        cal.add_component(event)

    return cal.to_ical().decode('utf-8')


def generate_ics_from_events(
    events: List[dict],
    calendar_name: str = "Organization Events",
    timezone: str = "UTC",
    include_assignments: bool = True
) -> str:
    """
    Generate an ICS calendar file from a list of events (for admin export).

    Args:
        events: List of event dicts
        calendar_name: Name of the calendar
        timezone: Timezone for the events
        include_assignments: Whether to include assignment info in description

    Returns:
        ICS file content as string
    """
    cal = Calendar()
    cal.add('prodid', '-//Rostio//Calendar Export//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', calendar_name)
    cal.add('x-wr-timezone', timezone)

    for event_data in events:
        event = ICalEvent()

        # Required fields
        event.add('uid', f"rostio-event-{event_data.get('id')}@rostio.app")
        event.add('dtstamp', datetime.utcnow().replace(tzinfo=ZoneInfo('UTC')))

        # Event times
        start_time = event_data.get('start_time')
        end_time = event_data.get('end_time')

        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

        # Ensure timezone-aware
        if start_time and start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=ZoneInfo('UTC'))
        if end_time and end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=ZoneInfo('UTC'))

        event.add('dtstart', vDatetime(start_time))
        event.add('dtend', vDatetime(end_time))

        # Summary
        event_type = event_data.get('type', 'Event')
        event.add('summary', event_type)

        # Description
        description_parts = []

        extra_data = event_data.get('extra_data', {})
        if extra_data.get('notes'):
            description_parts.append(f"Notes: {extra_data['notes']}")

        # Include assignments if requested
        if include_assignments and event_data.get('assignments'):
            description_parts.append("\nAssignments:")
            for assignment in event_data['assignments']:
                person_name = assignment.get('person', {}).get('name', 'Unknown')
                role = assignment.get('role', 'Volunteer')
                description_parts.append(f"- {person_name} ({role})")

        if description_parts:
            event.add('description', '\n'.join(description_parts))

        # Location
        resource = event_data.get('resource', {})
        if resource:
            location = resource.get('location', '')
            event.add('location', location)

        # Status
        event.add('status', 'CONFIRMED')

        # Add to calendar
        cal.add_component(event)

    return cal.to_ical().decode('utf-8')


def generate_webcal_url(base_url: str, token: str) -> str:
    """
    Generate a webcal:// subscription URL for a calendar token.

    Args:
        base_url: Base URL of the application (e.g., "https://rostio.app")
        token: Unique calendar token

    Returns:
        webcal:// URL for calendar subscription
    """
    # Remove protocol from base_url if present
    if base_url.startswith('https://'):
        base_url = base_url.replace('https://', '')
    elif base_url.startswith('http://'):
        base_url = base_url.replace('http://', '')

    return f"webcal://{base_url}/api/calendar/feed/{token}"


def generate_https_feed_url(base_url: str, token: str) -> str:
    """
    Generate an https:// feed URL for a calendar token (alternative to webcal://).

    Args:
        base_url: Base URL of the application (e.g., "https://rostio.app")
        token: Unique calendar token

    Returns:
        https:// URL for calendar feed
    """
    # Ensure https:// protocol
    if not base_url.startswith('http'):
        base_url = f"https://{base_url}"

    # Remove trailing slash
    base_url = base_url.rstrip('/')

    return f"{base_url}/api/calendar/feed/{token}"
