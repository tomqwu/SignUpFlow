"""Semantic validation across loaded files."""

from datetime import date
from pathlib import Path
from typing import Any

from roster_cli.core.loader import (
    load_availability_files,
    load_constraint_files,
    load_events,
    load_holidays,
    load_org,
    load_people,
    load_resources,
    load_teams,
)


class ValidationError(Exception):
    """Validation error with context."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


def validate_workspace(workspace: Path, from_date: date | None = None, to_date: date | None = None) -> None:
    """Validate entire workspace for semantic correctness."""
    errors: list[str] = []

    # Load all files
    try:
        org = load_org(workspace)
    except Exception as e:
        errors.append(f"org.yaml: {e}")
        raise ValidationError(errors)

    try:
        people_file = load_people(workspace)
        people = people_file.people
    except Exception as e:
        errors.append(f"people.yaml: {e}")
        raise ValidationError(errors)

    teams_file = load_teams(workspace)
    teams = teams_file.teams if teams_file else []

    resources_file = load_resources(workspace)
    resources = resources_file.resources if resources_file else []

    try:
        events_file = load_events(workspace)
        events = events_file.events
    except Exception as e:
        errors.append(f"events.yaml: {e}")
        raise ValidationError(errors)

    holidays_file = load_holidays(workspace)
    availability_list = load_availability_files(workspace)
    constraints = load_constraint_files(workspace)

    # Build ID sets
    person_ids = {p.id for p in people}
    team_ids = {t.id for t in teams}
    resource_ids = {r.id for r in resources}
    event_ids = {e.id for e in events}

    # Validate team members
    for team in teams:
        for member_id in team.members:
            if member_id not in person_ids:
                errors.append(f"Team {team.id}: member {member_id} not found in people")

    # Validate event references
    for event in events:
        if event.resource_id and event.resource_id not in resource_ids:
            errors.append(f"Event {event.id}: resource_id {event.resource_id} not found")

        for team_id in event.team_ids:
            if team_id not in team_ids:
                errors.append(f"Event {event.id}: team_id {team_id} not found")

        for assignee in event.assignees:
            if assignee not in person_ids:
                errors.append(f"Event {event.id}: assignee {assignee} not found in people")

        if event.start >= event.end:
            errors.append(f"Event {event.id}: start time must be before end time")

    # Validate availability references
    for avail in availability_list:
        if avail.person_id and avail.person_id not in person_ids:
            errors.append(f"Availability: person_id {avail.person_id} not found")
        if avail.resource_id and avail.resource_id not in resource_ids:
            errors.append(f"Availability: resource_id {avail.resource_id} not found")

    # Validate constraints
    valid_scopes = {"org", "team", "person", "event", "schedule"}
    valid_severities = {"hard", "soft"}

    for constraint in constraints:
        if constraint.scope not in valid_scopes:
            errors.append(f"Constraint {constraint.key}: invalid scope {constraint.scope}")

        if constraint.severity not in valid_severities:
            errors.append(f"Constraint {constraint.key}: invalid severity {constraint.severity}")

        if constraint.severity == "soft" and constraint.weight is None:
            errors.append(f"Constraint {constraint.key}: soft constraint requires weight")

    if errors:
        raise ValidationError(errors)
