#!/usr/bin/env python3
"""
Roster API Usage Example

This demonstrates how to use the Roster API programmatically
without the CLI interface.
"""

from datetime import date
from pathlib import Path

from roster_cli.core.loader import (
    load_constraint_files,
    load_events,
    load_holidays,
    load_org,
    load_people,
    load_resources,
    load_teams,
)
from roster_cli.core.csv_writer import write_assignments_csv
from roster_cli.core.ics_writer import write_calendar_ics
from roster_cli.core.json_writer import write_solution_json
from roster_cli.core.schema_validators import validate_workspace
from roster_cli.core.solver.adapter import SolveContext
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver


def solve_schedule(workspace_path: Path, from_date: date, to_date: date) -> None:
    """
    Complete example of solving a schedule using the API.

    Args:
        workspace_path: Path to workspace directory with YAML files
        from_date: Start date for schedule
        to_date: End date for schedule
    """

    # Step 1: Validate workspace
    print("Validating workspace...")
    validate_workspace(workspace_path, from_date, to_date)
    print("✓ Validation passed")

    # Step 2: Load all data files
    print("\nLoading data...")
    org = load_org(workspace_path)
    people_file = load_people(workspace_path)
    teams_file = load_teams(workspace_path)
    resources_file = load_resources(workspace_path)
    events_file = load_events(workspace_path)
    holidays_file = load_holidays(workspace_path)
    constraints = load_constraint_files(workspace_path)

    print(f"Loaded {len(people_file.people)} people")
    print(f"Loaded {len(events_file.events)} events")
    print(f"Loaded {len(constraints)} constraints")

    # Step 3: Build solve context
    print("\nBuilding solve context...")
    context = SolveContext(
        org=org,
        people=people_file.people,
        teams=teams_file.teams if teams_file else [],
        resources=resources_file.resources if resources_file else [],
        events=events_file.events,
        constraints=constraints,
        availability=[],
        holidays=holidays_file.days if holidays_file else [],
        from_date=from_date,
        to_date=to_date,
        mode="strict",
        change_min=False,
    )

    # Step 4: Initialize solver and build model
    print("\nInitializing solver...")
    solver = GreedyHeuristicSolver()
    solver.build_model(context)

    # Step 5: Solve
    print("Solving...")
    solution = solver.solve()

    # Step 6: Display results
    print("\n" + "="*60)
    print("SOLUTION RESULTS")
    print("="*60)
    print(f"Assignments created: {len(solution.assignments)}")
    print(f"Hard violations: {solution.metrics.hard_violations}")
    print(f"Soft score: {solution.metrics.soft_score:.2f}")
    print(f"Fairness (stdev): {solution.metrics.fairness.stdev:.2f}")
    print(f"Health score: {solution.metrics.health_score:.1f}/100")
    print(f"Solve time: {solution.metrics.solve_ms:.0f}ms")

    if solution.violations.hard:
        print("\n⚠️  Hard violations:")
        for v in solution.violations.hard[:5]:
            print(f"  - {v.constraint_key}: {v.message}")

    # Step 7: Write outputs
    output_dir = workspace_path / "out"
    output_dir.mkdir(exist_ok=True)

    write_solution_json(solution, output_dir / "solution.json")
    write_assignments_csv(solution, events_file.events, people_file.people, output_dir / "assignments.csv")
    write_calendar_ics(solution, events_file.events, people_file.people, output_dir / "calendar.ics")

    print(f"\n✓ Outputs written to {output_dir}/")

    # Step 8: Access solution data programmatically
    print("\nSample assignments:")
    for assignment in solution.assignments[:3]:
        event = next((e for e in events_file.events if e.id == assignment.event_id), None)
        if event:
            people_names = [
                next((p.name for p in people_file.people if p.id == pid), pid)
                for pid in assignment.assignees
            ]
            print(f"  {event.id}: {', '.join(people_names[:3])}")
            if len(people_names) > 3:
                print(f"    ... and {len(people_names) - 3} more")


def main() -> None:
    """Run example."""
    # Use church template as example
    workspace = Path("/tmp/test_church")

    if not workspace.exists():
        print("Please run test_api.py first to create test workspaces")
        return

    solve_schedule(
        workspace_path=workspace,
        from_date=date(2025, 9, 1),
        to_date=date(2025, 10, 31),
    )


if __name__ == "__main__":
    main()
