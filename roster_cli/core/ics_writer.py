"""ICS calendar output writer."""

from pathlib import Path

from ics import Calendar, Event as ICSEvent

from roster_cli.core.models import Event, Person, SolutionBundle


def write_calendar_ics(
    solution: SolutionBundle,
    events: list[Event],
    people: list[Person],
    output_path: Path,
    scope: str = "org",
    scope_id: str | None = None,
) -> None:
    """Write ICS calendar file for given scope."""
    event_map = {e.id: e for e in events}
    people_map = {p.id: p for p in people}

    calendar = Calendar()

    for assignment in solution.assignments:
        event = event_map.get(assignment.event_id)
        if not event:
            continue

        # Filter by scope
        if scope == "person" and scope_id:
            if scope_id not in assignment.assignees:
                continue
        elif scope == "team" and scope_id:
            if scope_id not in assignment.team_ids:
                continue

        # Create ICS event
        ics_event = ICSEvent()
        ics_event.name = f"{event.type} - {event.id}"
        ics_event.begin = event.start
        ics_event.end = event.end

        # Add attendees
        assignee_names = [
            people_map[pid].name for pid in assignment.assignees if pid in people_map
        ]
        if assignee_names:
            ics_event.description = f"Assigned: {', '.join(assignee_names)}"

        calendar.events.add(ics_event)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(calendar.serialize_iter())
