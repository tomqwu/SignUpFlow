"""Diff command."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from roster_cli.core.diffing import diff_solutions
from roster_cli.core.loader import load_solution, save_json

console = Console()


def diff_command(
    prev: Path = typer.Option(..., help="Previous solution file"),
    curr: Path = typer.Option(..., help="Current solution file"),
    out: Path = typer.Option(None, help="Output diff JSON path"),
) -> None:
    """Compare two solutions and show differences."""
    try:
        prev_solution = load_solution(prev)
        curr_solution = load_solution(curr)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load solutions: {e}")
        raise typer.Exit(1)

    diff_result = diff_solutions(prev_solution, curr_solution)

    # Display summary
    console.print("\n[bold]Solution Diff[/bold]")
    table = Table()
    table.add_column("Change Type", style="cyan")
    table.add_column("Count", style="magenta")

    table.add_row("Added assignments", str(len(diff_result.added)))
    table.add_row("Removed assignments", str(len(diff_result.removed)))
    table.add_row("Total changes", str(diff_result.total_changes))
    table.add_row("Affected persons", str(len(diff_result.affected_persons)))

    console.print(table)

    # Show sample changes
    if diff_result.added:
        console.print("\n[green]Sample added:[/green]")
        for event_id, person_id in diff_result.added[:3]:
            console.print(f"  • Event {event_id}: +{person_id}")

    if diff_result.removed:
        console.print("\n[red]Sample removed:[/red]")
        for event_id, person_id in diff_result.removed[:3]:
            console.print(f"  • Event {event_id}: -{person_id}")

    # Write output
    if out:
        diff_data = {
            "added": [{"event_id": e, "person_id": p} for e, p in diff_result.added],
            "removed": [{"event_id": e, "person_id": p} for e, p in diff_result.removed],
            "moved": [{"event_id": e, "old": o, "new": n} for e, o, n in diff_result.moved],
            "affected_persons": list(diff_result.affected_persons),
            "total_changes": diff_result.total_changes,
        }
        save_json(out, diff_data)
        console.print(f"\n[green]✓[/green] Diff written to {out}")
