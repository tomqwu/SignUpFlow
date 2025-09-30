"""Diffing utilities for comparing solutions."""

from dataclasses import dataclass

from roster_cli.core.models import SolutionBundle


@dataclass
class DiffResult:
    """Result of comparing two solutions."""

    moved: list[tuple[str, str, str]]  # (event_id, old_person, new_person)
    added: list[tuple[str, str]]  # (event_id, person)
    removed: list[tuple[str, str]]  # (event_id, person)
    affected_persons: set[str]
    total_changes: int


def diff_solutions(prev: SolutionBundle, curr: SolutionBundle) -> DiffResult:
    """Compute structural diff between two solutions."""
    prev_map: dict[str, set[str]] = {}
    for assignment in prev.assignments:
        prev_map[assignment.event_id] = set(assignment.assignees)

    curr_map: dict[str, set[str]] = {}
    for assignment in curr.assignments:
        curr_map[assignment.event_id] = set(assignment.assignees)

    moved: list[tuple[str, str, str]] = []
    added: list[tuple[str, str]] = []
    removed: list[tuple[str, str]] = []
    affected_persons: set[str] = set()

    # Find all event IDs
    all_events = set(prev_map.keys()) | set(curr_map.keys())

    for event_id in all_events:
        prev_assignees = prev_map.get(event_id, set())
        curr_assignees = curr_map.get(event_id, set())

        # Removed assignees
        for person_id in prev_assignees - curr_assignees:
            removed.append((event_id, person_id))
            affected_persons.add(person_id)

        # Added assignees
        for person_id in curr_assignees - prev_assignees:
            added.append((event_id, person_id))
            affected_persons.add(person_id)

        # Simple move detection: if both sets changed, consider as moves
        if prev_assignees != curr_assignees and prev_assignees and curr_assignees:
            # Just track as changes, not precise moves
            pass

    total_changes = len(added) + len(removed)

    return DiffResult(
        moved=moved,
        added=added,
        removed=removed,
        affected_persons=affected_persons,
        total_changes=total_changes,
    )
