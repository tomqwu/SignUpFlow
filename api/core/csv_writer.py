"""CSV output writer for assignments."""

from pathlib import Path
from typing import Any

from api.core.loader import save_csv
from api.core.models import Event, Person, SolutionBundle


def write_assignments_csv(
    solution: SolutionBundle, events: list[Event], people: list[Person], output_path: Path
) -> None:
    """Write assignments to CSV."""
    event_map = {e.id: e for e in events}
    people_map = {p.id: p for p in people}

    rows: list[dict[str, Any]] = []
    for assignment in solution.assignments:
        event = event_map.get(assignment.event_id)
        if not event:
            continue

        assignee_names = [
            people_map[pid].name for pid in assignment.assignees if pid in people_map
        ]

        rows.append(
            {
                "event_id": assignment.event_id,
                "event_type": event.type,
                "start": event.start.isoformat(),
                "end": event.end.isoformat(),
                "assignees": ", ".join(assignee_names),
                "assignee_ids": ", ".join(assignment.assignees),
                "resource_id": assignment.resource_id or "",
                "team_ids": ", ".join(assignment.team_ids),
            }
        )

    fieldnames = [
        "event_id",
        "event_type",
        "start",
        "end",
        "assignees",
        "assignee_ids",
        "resource_id",
        "team_ids",
    ]
    save_csv(output_path, rows, fieldnames)
