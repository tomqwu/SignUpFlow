#!/usr/bin/env python3
"""Test roster API functionality."""

from datetime import date
from pathlib import Path
import shutil

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
from roster_cli.core.csv_writer import write_assignments_csv
from roster_cli.core.ics_writer import write_calendar_ics
from roster_cli.core.json_writer import write_metrics_json, write_solution_json
from roster_cli.core.schema_validators import validate_workspace
from roster_cli.core.solver.adapter import SolveContext
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver


def test_cricket_template():
    """Test cricket template end-to-end."""
    print("\n" + "="*60)
    print("Testing Cricket Template API")
    print("="*60)

    # Setup workspace
    workspace = Path("/tmp/test_cricket")
    if workspace.exists():
        shutil.rmtree(workspace)

    # Copy cricket template
    template_src = Path(__file__).parent / "roster_cli" / "templates" / "cricket"
    shutil.copytree(template_src, workspace)
    print(f"✓ Workspace created at {workspace}")

    # Validate
    try:
        validate_workspace(workspace)
        print("✓ Validation passed")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

    # Load data
    print("\nLoading workspace data...")
    org = load_org(workspace)
    people_file = load_people(workspace)
    teams_file = load_teams(workspace)
    resources_file = load_resources(workspace)
    events_file = load_events(workspace)
    holidays_file = load_holidays(workspace)
    availability = load_availability_files(workspace)
    constraints = load_constraint_files(workspace)

    print(f"  - Org: {org.org_id}")
    print(f"  - People: {len(people_file.people)}")
    print(f"  - Teams: {len(teams_file.teams if teams_file else [])}")
    print(f"  - Resources: {len(resources_file.resources if resources_file else [])}")
    print(f"  - Events: {len(events_file.events)}")
    print(f"  - Holidays: {len(holidays_file.days if holidays_file else [])}")
    print(f"  - Constraints: {len(constraints)}")

    # Build solve context
    context = SolveContext(
        org=org,
        people=people_file.people,
        teams=teams_file.teams if teams_file else [],
        resources=resources_file.resources if resources_file else [],
        events=events_file.events,
        constraints=constraints,
        availability=availability,
        holidays=holidays_file.days if holidays_file else [],
        from_date=date(2025, 9, 1),
        to_date=date(2025, 9, 30),
        mode="strict",
        change_min=False,
    )
    print("\n✓ SolveContext created")

    # Solve
    print("\nSolving...")
    solver = GreedyHeuristicSolver()
    solver.build_model(context)
    solution = solver.solve()

    print(f"\n✓ Solution generated:")
    print(f"  - Assignments: {len(solution.assignments)}")
    print(f"  - Hard violations: {solution.metrics.hard_violations}")
    print(f"  - Soft score: {solution.metrics.soft_score:.2f}")
    print(f"  - Fairness (stdev): {solution.metrics.fairness.stdev:.2f}")
    print(f"  - Health score: {solution.metrics.health_score:.1f}/100")
    print(f"  - Solve time: {solution.metrics.solve_ms:.0f}ms")

    # Write outputs
    output_dir = workspace / "out"
    output_dir.mkdir(exist_ok=True)

    write_solution_json(solution, output_dir / "solution.json")
    write_assignments_csv(solution, events_file.events, people_file.people, output_dir / "assignments.csv")
    write_calendar_ics(solution, events_file.events, people_file.people, output_dir / "calendar.ics")
    write_metrics_json(solution, output_dir / "metrics.json")

    print(f"\n✓ Outputs written to {output_dir}")
    print(f"  - solution.json ({(output_dir / 'solution.json').stat().st_size} bytes)")
    print(f"  - assignments.csv ({(output_dir / 'assignments.csv').stat().st_size} bytes)")
    print(f"  - calendar.ics ({(output_dir / 'calendar.ics').stat().st_size} bytes)")
    print(f"  - metrics.json ({(output_dir / 'metrics.json').stat().st_size} bytes)")

    return solution.metrics.hard_violations == 0


def test_church_template():
    """Test church template end-to-end."""
    print("\n" + "="*60)
    print("Testing Church Template API")
    print("="*60)

    workspace = Path("/tmp/test_church")
    if workspace.exists():
        shutil.rmtree(workspace)

    template_src = Path(__file__).parent / "roster_cli" / "templates" / "church"
    shutil.copytree(template_src, workspace)
    print(f"✓ Workspace created at {workspace}")

    # Validate
    try:
        validate_workspace(workspace)
        print("✓ Validation passed")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

    # Load data
    print("\nLoading workspace data...")
    org = load_org(workspace)
    people_file = load_people(workspace)
    teams_file = load_teams(workspace)
    resources_file = load_resources(workspace)
    events_file = load_events(workspace)
    holidays_file = load_holidays(workspace)
    availability = load_availability_files(workspace)
    constraints = load_constraint_files(workspace)

    print(f"  - Org: {org.org_id}")
    print(f"  - People: {len(people_file.people)}")
    print(f"  - Events: {len(events_file.events)}")
    print(f"  - Constraints: {len(constraints)}")

    # Build solve context
    context = SolveContext(
        org=org,
        people=people_file.people,
        teams=teams_file.teams if teams_file else [],
        resources=resources_file.resources if resources_file else [],
        events=events_file.events,
        constraints=constraints,
        availability=availability,
        holidays=holidays_file.days if holidays_file else [],
        from_date=date(2025, 9, 1),
        to_date=date(2025, 10, 31),
        mode="strict",
        change_min=False,
    )
    print("\n✓ SolveContext created")

    # Solve
    print("\nSolving...")
    solver = GreedyHeuristicSolver()
    solver.build_model(context)
    solution = solver.solve()

    print(f"\n✓ Solution generated:")
    print(f"  - Assignments: {len(solution.assignments)}")
    print(f"  - Hard violations: {solution.metrics.hard_violations}")
    print(f"  - Soft score: {solution.metrics.soft_score:.2f}")
    print(f"  - Fairness (stdev): {solution.metrics.fairness.stdev:.2f}")
    print(f"  - Health score: {solution.metrics.health_score:.1f}/100")
    print(f"  - Solve time: {solution.metrics.solve_ms:.0f}ms")

    # Write outputs
    output_dir = workspace / "out"
    output_dir.mkdir(exist_ok=True)

    write_solution_json(solution, output_dir / "solution.json")
    write_assignments_csv(solution, events_file.events, people_file.people, output_dir / "assignments.csv")
    write_calendar_ics(solution, events_file.events, people_file.people, output_dir / "calendar.ics")
    write_metrics_json(solution, output_dir / "metrics.json")

    print(f"\n✓ Outputs written to {output_dir}")

    # Show sample assignments
    print("\nSample assignments:")
    for i, assignment in enumerate(solution.assignments[:3]):
        event = next((e for e in events_file.events if e.id == assignment.event_id), None)
        if event:
            print(f"  {event.id} ({event.start.date()}): {len(assignment.assignees)} people")

    return True


def test_oncall_template():
    """Test oncall template end-to-end."""
    print("\n" + "="*60)
    print("Testing On-Call Template API")
    print("="*60)

    workspace = Path("/tmp/test_oncall")
    if workspace.exists():
        shutil.rmtree(workspace)

    template_src = Path(__file__).parent / "roster_cli" / "templates" / "oncall"
    shutil.copytree(template_src, workspace)
    print(f"✓ Workspace created at {workspace}")

    # Validate
    try:
        validate_workspace(workspace)
        print("✓ Validation passed")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

    # Load data
    print("\nLoading workspace data...")
    org = load_org(workspace)
    people_file = load_people(workspace)
    events_file = load_events(workspace)
    holidays_file = load_holidays(workspace)
    constraints = load_constraint_files(workspace)

    print(f"  - Org: {org.org_id}")
    print(f"  - People: {len(people_file.people)}")
    print(f"  - Events: {len(events_file.events)}")
    print(f"  - Constraints: {len(constraints)}")

    # Build solve context
    context = SolveContext(
        org=org,
        people=people_file.people,
        teams=[],
        resources=[],
        events=events_file.events,
        constraints=constraints,
        availability=[],
        holidays=holidays_file.days if holidays_file else [],
        from_date=date(2025, 9, 1),
        to_date=date(2025, 9, 10),
        mode="strict",
        change_min=False,
    )
    print("\n✓ SolveContext created")

    # Solve
    print("\nSolving...")
    solver = GreedyHeuristicSolver()
    solver.build_model(context)
    solution = solver.solve()

    print(f"\n✓ Solution generated:")
    print(f"  - Assignments: {len(solution.assignments)}")
    print(f"  - Hard violations: {solution.metrics.hard_violations}")
    print(f"  - Soft score: {solution.metrics.soft_score:.2f}")
    print(f"  - Fairness (stdev): {solution.metrics.fairness.stdev:.2f}")
    print(f"  - Health score: {solution.metrics.health_score:.1f}/100")
    print(f"  - Solve time: {solution.metrics.solve_ms:.0f}ms")

    # Show assignment distribution
    person_counts = {}
    for assignment in solution.assignments:
        for person_id in assignment.assignees:
            person_counts[person_id] = person_counts.get(person_id, 0) + 1

    print("\nAssignment distribution:")
    for person_id, count in sorted(person_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        person = next((p for p in people_file.people if p.id == person_id), None)
        if person:
            print(f"  {person.name}: {count} shifts")

    # Write outputs
    output_dir = workspace / "out"
    output_dir.mkdir(exist_ok=True)

    write_solution_json(solution, output_dir / "solution.json")
    write_assignments_csv(solution, events_file.events, people_file.people, output_dir / "assignments.csv")
    write_calendar_ics(solution, events_file.events, people_file.people, output_dir / "calendar.ics")
    write_metrics_json(solution, output_dir / "metrics.json")

    print(f"\n✓ Outputs written to {output_dir}")

    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ROSTER API TEST SUITE")
    print("="*60)

    results = []

    # Test all templates
    results.append(("Cricket", test_cricket_template()))
    results.append(("Church", test_church_template()))
    results.append(("On-Call", test_oncall_template()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name} Template")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All API tests passed!")
    else:
        print("\n⚠️  Some tests failed")
