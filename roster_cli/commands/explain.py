"""Explain command."""

from pathlib import Path

import typer
from rich.console import Console

from roster_cli.core.loader import load_events, load_people, load_solution

console = Console()


def explain_command(
    solution: Path = typer.Option(..., help="Solution file"),
    dir: Path = typer.Option(..., help="Workspace directory"),
    event: str = typer.Option(None, help="Event ID"),
    person: str = typer.Option(None, help="Person ID"),
) -> None:
    """Explain why a person was/wasn't assigned to an event."""
    if not event and not person:
        console.print("[red]Error:[/red] Must specify --event or --person")
        raise typer.Exit(1)

    try:
        sol = load_solution(solution)
        events_file = load_events(dir)
        people_file = load_people(dir)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    events_map = {e.id: e for e in events_file.events}
    people_map = {p.id: p for p in people_file.people}
    assignment_map = {a.event_id: a.assignees for a in sol.assignments}

    if event:
        if event not in events_map:
            console.print(f"[red]Error:[/red] Event {event} not found")
            raise typer.Exit(1)

        assignees = assignment_map.get(event, [])
        console.print(f"\n[bold]Event: {event}[/bold]")
        console.print(f"Type: {events_map[event].type}")
        console.print(f"Time: {events_map[event].start} - {events_map[event].end}")
        console.print(f"\nAssigned ({len(assignees)}):")
        for person_id in assignees:
            person_name = people_map[person_id].name if person_id in people_map else person_id
            console.print(f"  • {person_name} ({person_id})")

        if not assignees:
            console.print("  (none)")
            console.print("\n[yellow]Possible reasons:[/yellow]")
            console.print("  • No people with required roles available")
            console.print("  • Hard constraints blocked all candidates")
            console.print("  • Check violations in solution for details")

    if person:
        if person not in people_map:
            console.print(f"[red]Error:[/red] Person {person} not found")
            raise typer.Exit(1)

        assigned_events = [
            event_id for event_id, assignees in assignment_map.items() if person in assignees
        ]

        console.print(f"\n[bold]Person: {people_map[person].name} ({person})[/bold]")
        console.print(f"Roles: {', '.join(people_map[person].roles)}")
        console.print(f"\nAssigned to {len(assigned_events)} events:")

        for event_id in assigned_events[:10]:
            if event_id in events_map:
                evt = events_map[event_id]
                console.print(f"  • {event_id}: {evt.start.date()} ({evt.type})")

        if len(assigned_events) > 10:
            console.print(f"  ... and {len(assigned_events) - 10} more")
