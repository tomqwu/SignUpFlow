"""Solve command."""

from datetime import date
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from roster_cli.core.csv_writer import write_assignments_csv
from roster_cli.core.ics_writer import write_calendar_ics
from roster_cli.core.json_writer import write_metrics_json, write_solution_json
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
from roster_cli.core.publish_state import get_latest_published
from roster_cli.core.schema_validators import ValidationError, validate_workspace
from roster_cli.core.solver.adapter import SolveContext
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver

console = Console()


def solve_command(
    dir: Path = typer.Option(..., help="Workspace directory"),
    from_date: str = typer.Option(..., help="Start date (YYYY-MM-DD)"),
    to_date: str = typer.Option(..., help="End date (YYYY-MM-DD)"),
    mode: str = typer.Option("strict", help="Mode: strict|relaxed"),
    change_min: bool = typer.Option(True, help="Enable change minimization"),
    out: Path = typer.Option(None, help="Output directory (default: <dir>/out)"),
) -> None:
    """Solve and generate schedule."""
    # Parse dates
    try:
        start = date.fromisoformat(from_date)
        end = date.fromisoformat(to_date)
    except ValueError as e:
        console.print(f"[red]Error:[/red] Invalid date format: {e}")
        raise typer.Exit(1)

    # Validate
    try:
        validate_workspace(dir, start, end)
    except ValidationError as e:
        console.print("[red]Validation failed:[/red]")
        for error in e.errors:
            console.print(f"  • {error}")
        raise typer.Exit(1)

    # Load data
    console.print("Loading workspace...")
    org = load_org(dir)
    people_file = load_people(dir)
    teams_file = load_teams(dir)
    resources_file = load_resources(dir)
    events_file = load_events(dir)
    holidays_file = load_holidays(dir)
    availability = load_availability_files(dir)
    constraints = load_constraint_files(dir)

    people = people_file.people
    teams = teams_file.teams if teams_file else []
    resources = resources_file.resources if resources_file else []
    events = events_file.events
    holidays = holidays_file.days if holidays_file else []

    published = get_latest_published(dir) if change_min else None

    # Build context
    context = SolveContext(
        org=org,
        people=people,
        teams=teams,
        resources=resources,
        events=events,
        constraints=constraints,
        availability=availability,
        holidays=holidays,
        from_date=start,
        to_date=end,
        mode=mode,
        change_min=change_min,
        published_solution=published,
    )

    # Solve
    console.print("Solving...")
    solver = GreedyHeuristicSolver()
    solver.build_model(context)
    if change_min and published:
        solver.enable_change_minimization(True, org.defaults.change_min_weight)

    solution = solver.solve()

    # Output
    output_dir = out if out else dir / "out"
    output_dir.mkdir(parents=True, exist_ok=True)

    write_solution_json(solution, output_dir / "solution.json")
    write_assignments_csv(solution, events, people, output_dir / "assignments.csv")
    write_calendar_ics(solution, events, people, output_dir / "calendar.ics")
    write_metrics_json(solution, output_dir / "metrics.json")

    # Display results
    console.print("\n[bold]Solution Summary[/bold]")
    table = Table()
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Hard violations", str(solution.metrics.hard_violations))
    table.add_row("Soft score", f"{solution.metrics.soft_score:.2f}")
    table.add_row("Fairness (stdev)", f"{solution.metrics.fairness.stdev:.2f}")
    table.add_row("Solve time", f"{solution.metrics.solve_ms:.0f} ms")
    table.add_row("Health score", f"{solution.metrics.health_score:.1f}/100")

    console.print(table)

    if solution.metrics.hard_violations > 0:
        console.print("\n[red]Hard constraint violations:[/red]")
        for v in solution.violations.hard[:5]:
            console.print(f"  • {v.constraint_key}: {v.message}")
        if len(solution.violations.hard) > 5:
            console.print(f"  ... and {len(solution.violations.hard) - 5} more")

    console.print(f"\n[green]✓[/green] Solution written to {output_dir}")
    console.print(f"  • solution.json")
    console.print(f"  • assignments.csv")
    console.print(f"  • calendar.ics")
    console.print(f"  • metrics.json")

    if solution.metrics.hard_violations > 0:
        raise typer.Exit(1)
