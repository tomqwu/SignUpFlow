"""Simulate command."""

from datetime import date
from pathlib import Path

import typer
from rich.console import Console

from roster_cli.core.diffing import diff_solutions
from roster_cli.core.loader import (
    load_availability_files,
    load_constraint_files,
    load_events,
    load_holidays,
    load_org,
    load_people,
    load_resources,
    load_teams,
    load_yaml,
)
from roster_cli.core.models import Patch
from roster_cli.core.publish_state import get_latest_published
from roster_cli.core.solver.adapter import SolveContext
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver

console = Console()


def simulate_command(
    dir: Path = typer.Option(..., help="Workspace directory"),
    patch: Path = typer.Option(..., help="Patch YAML file"),
    from_date: str = typer.Option(..., help="Start date (YYYY-MM-DD)"),
    to_date: str = typer.Option(..., help="End date (YYYY-MM-DD)"),
) -> None:
    """Simulate changes with a patch and show impact."""
    # Parse dates
    try:
        start = date.fromisoformat(from_date)
        end = date.fromisoformat(to_date)
    except ValueError as e:
        console.print(f"[red]Error:[/red] Invalid date format: {e}")
        raise typer.Exit(1)

    # Load patch
    try:
        patch_data = load_yaml(patch)
        patch_obj = Patch(**patch_data)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load patch: {e}")
        raise typer.Exit(1)

    # Load baseline
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

    # Solve baseline
    console.print("Solving baseline...")
    baseline_context = SolveContext(
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
        mode="strict",
        change_min=False,
    )
    baseline_solver = GreedyHeuristicSolver()
    baseline_solver.build_model(baseline_context)
    baseline_solution = baseline_solver.solve()

    # Apply patch
    console.print("Applying patch...")
    people_patched = people.copy()
    events_patched = events.copy()
    availability_patched = availability.copy()

    for person in patch_obj.add_people:
        people_patched.append(person)
    people_patched = [p for p in people_patched if p.id not in patch_obj.remove_people]

    for event in patch_obj.add_events:
        events_patched.append(event)
    events_patched = [e for e in events_patched if e.id not in patch_obj.remove_events]

    for avail in patch_obj.update_availability:
        # Simple update: remove old and add new
        availability_patched = [
            a
            for a in availability_patched
            if a.person_id != avail.person_id and a.resource_id != avail.resource_id
        ]
        availability_patched.append(avail)

    # Solve with patch
    console.print("Solving with patch...")
    patched_context = SolveContext(
        org=org,
        people=people_patched,
        teams=teams,
        resources=resources,
        events=events_patched,
        constraints=constraints,
        availability=availability_patched,
        holidays=holidays,
        from_date=start,
        to_date=end,
        mode="strict",
        change_min=True,
        published_solution=baseline_solution,
    )
    patched_solver = GreedyHeuristicSolver()
    patched_solver.build_model(patched_context)
    patched_solver.enable_change_minimization(True, org.defaults.change_min_weight)
    patched_solution = patched_solver.solve()

    # Compute diff
    diff_result = diff_solutions(baseline_solution, patched_solution)

    console.print("\n[bold]Simulation Results[/bold]")
    console.print(f"Changes: {diff_result.total_changes}")
    console.print(f"Affected persons: {len(diff_result.affected_persons)}")
    console.print(
        f"\nBaseline health: {baseline_solution.metrics.health_score:.1f}"
    )
    console.print(f"Patched health: {patched_solution.metrics.health_score:.1f}")
    console.print(
        f"Delta: {patched_solution.metrics.health_score - baseline_solution.metrics.health_score:+.1f}"
    )
