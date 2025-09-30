"""Export command."""

from pathlib import Path

import typer
from rich.console import Console

from roster_cli.core.csv_writer import write_assignments_csv
from roster_cli.core.ics_writer import write_calendar_ics
from roster_cli.core.loader import load_events, load_people, load_solution

console = Console()


def export_command(
    solution: Path = typer.Option(..., help="Solution file"),
    dir: Path = typer.Option(..., help="Workspace directory"),
    scope: str = typer.Option("org", help="Scope: org|person:<id>|team:<id>"),
    ics_out: Path = typer.Option(None, help="ICS output path"),
    csv_out: Path = typer.Option(None, help="CSV output path"),
) -> None:
    """Export solution to ICS/CSV for specific scope."""
    try:
        sol = load_solution(solution)
        events_file = load_events(dir)
        people_file = load_people(dir)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Parse scope
    scope_type = "org"
    scope_id = None
    if ":" in scope:
        scope_type, scope_id = scope.split(":", 1)

    # Export ICS
    if ics_out:
        write_calendar_ics(
            sol, events_file.events, people_file.people, ics_out, scope_type, scope_id
        )
        console.print(f"[green]✓[/green] ICS written to {ics_out}")

    # Export CSV
    if csv_out:
        # Filter assignments by scope
        if scope_type == "person" and scope_id:
            from roster_cli.core.models import Assignment

            filtered_assignments = [
                a for a in sol.assignments if scope_id in a.assignees
            ]
            from dataclasses import replace

            filtered_sol = sol.model_copy()
            filtered_sol.assignments = filtered_assignments

            write_assignments_csv(
                filtered_sol, events_file.events, people_file.people, csv_out
            )
        elif scope_type == "team" and scope_id:
            filtered_assignments = [
                a for a in sol.assignments if scope_id in a.team_ids
            ]
            filtered_sol = sol.model_copy()
            filtered_sol.assignments = filtered_assignments

            write_assignments_csv(
                filtered_sol, events_file.events, people_file.people, csv_out
            )
        else:
            write_assignments_csv(sol, events_file.events, people_file.people, csv_out)

        console.print(f"[green]✓[/green] CSV written to {csv_out}")

    if not ics_out and not csv_out:
        console.print("[yellow]Warning:[/yellow] No output files specified")
