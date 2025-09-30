#!/usr/bin/env python3
"""
Sample Roster Generation Test

This script demonstrates generating a complete roster with detailed output.
"""

from datetime import date
from pathlib import Path
import shutil

from roster_cli.core.loader import (
    load_org,
    load_people,
    load_events,
    load_constraint_files,
    load_holidays,
)
from roster_cli.core.csv_writer import write_assignments_csv
from roster_cli.core.ics_writer import write_calendar_ics
from roster_cli.core.json_writer import write_solution_json, write_metrics_json
from roster_cli.core.solver.adapter import SolveContext
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver


def generate_church_roster():
    """Generate a complete church volunteer roster."""

    print("\n" + "="*70)
    print("CHURCH VOLUNTEER ROSTER GENERATION")
    print("="*70)

    # Setup workspace
    workspace = Path("/tmp/sample_church_roster")
    if workspace.exists():
        shutil.rmtree(workspace)

    template_src = Path(__file__).parent.parent / "roster_cli" / "templates" / "church"
    shutil.copytree(template_src, workspace)
    print(f"\n📁 Workspace: {workspace}")

    # Load data
    print("\n📥 Loading data...")
    org = load_org(workspace)
    people_file = load_people(workspace)
    events_file = load_events(workspace)
    holidays_file = load_holidays(workspace)
    constraints = load_constraint_files(workspace)

    people = people_file.people
    events = events_file.events
    holidays = holidays_file.days if holidays_file else []

    print(f"   • Organization: {org.org_id}")
    print(f"   • Volunteers: {len(people)}")
    print(f"   • Events: {len(events)}")
    print(f"   • Constraints: {len(constraints)}")

    # Show people details
    print("\n👥 VOLUNTEERS:")
    for person in people[:10]:
        roles_str = ", ".join(person.roles)
        print(f"   • {person.name:20s} [{roles_str}]")
    if len(people) > 10:
        print(f"   ... and {len(people) - 10} more")

    # Show events
    print("\n📅 SERVICES TO SCHEDULE:")
    for event in events:
        req_roles = ", ".join([f"{r.role}({r.count})" for r in event.required_roles])
        print(f"   • {event.start.date()} - {event.id}")
        print(f"     Required: {req_roles}")

    # Build solve context
    print("\n⚙️  Building solver context...")
    context = SolveContext(
        org=org,
        people=people,
        teams=[],
        resources=[],
        events=events,
        constraints=constraints,
        availability=[],
        holidays=holidays,
        from_date=date(2025, 9, 1),
        to_date=date(2025, 10, 31),
        mode="strict",
        change_min=False,
    )

    # Solve
    print("\n🔄 Solving roster...")
    solver = GreedyHeuristicSolver()
    solver.build_model(context)
    solution = solver.solve()

    # Display results
    print("\n" + "="*70)
    print("SOLUTION METRICS")
    print("="*70)
    print(f"✓ Total Assignments: {len(solution.assignments)}")
    print(f"✓ Hard Violations: {solution.metrics.hard_violations}")
    print(f"✓ Soft Score: {solution.metrics.soft_score:.2f}")
    print(f"✓ Health Score: {solution.metrics.health_score:.1f}/100")
    print(f"✓ Fairness (σ): {solution.metrics.fairness.stdev:.2f}")
    print(f"✓ Solve Time: {solution.metrics.solve_ms:.0f}ms")

    # Show detailed roster
    print("\n" + "="*70)
    print("GENERATED ROSTER")
    print("="*70)

    people_map = {p.id: p for p in people}

    for assignment in solution.assignments:
        event = next((e for e in events if e.id == assignment.event_id), None)
        if not event:
            continue

        print(f"\n📆 {event.start.strftime('%A, %B %d, %Y')}")
        print(f"   Event: {event.id}")
        print(f"   Time: {event.start.strftime('%I:%M %p')} - {event.end.strftime('%I:%M %p')}")

        # Group by role
        role_assignments = {}
        for person_id in assignment.assignees:
            person = people_map.get(person_id)
            if person:
                for role in person.roles:
                    if role not in role_assignments:
                        role_assignments[role] = []
                    role_assignments[role].append(person.name)

        print(f"\n   Assignments:")
        for role in ['kitchen', 'reception', 'childcare', 'av_tech']:
            if role in role_assignments:
                names = sorted(set(role_assignments[role]))
                print(f"      {role.replace('_', ' ').title():15s}: {', '.join(names)}")

    # Fairness report
    print("\n" + "="*70)
    print("FAIRNESS REPORT")
    print("="*70)

    counts = solution.metrics.fairness.per_person_counts
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    print("\nAssignments per volunteer:")
    for person_id, count in sorted_counts:
        person = people_map.get(person_id)
        if person:
            bar = "█" * count
            print(f"   {person.name:20s} {bar} ({count})")

    avg_count = sum(counts.values()) / len(counts) if counts else 0
    print(f"\n   Average: {avg_count:.1f} assignments per volunteer")
    print(f"   Std Dev: {solution.metrics.fairness.stdev:.2f}")

    # Save outputs
    output_dir = workspace / "out"
    output_dir.mkdir(exist_ok=True)

    write_solution_json(solution, output_dir / "solution.json")
    write_assignments_csv(solution, events, people, output_dir / "assignments.csv")
    write_calendar_ics(solution, events, people, output_dir / "calendar.ics")
    write_metrics_json(solution, output_dir / "metrics.json")

    print("\n" + "="*70)
    print("OUTPUT FILES")
    print("="*70)
    print(f"\n✓ Solution saved to: {output_dir}/")
    print(f"   • solution.json    - Complete solution bundle")
    print(f"   • assignments.csv  - Spreadsheet-friendly format")
    print(f"   • calendar.ics     - Import to Google/Outlook/Apple Calendar")
    print(f"   • metrics.json     - Detailed metrics")

    # Show CSV sample
    print("\n" + "="*70)
    print("SAMPLE CSV OUTPUT")
    print("="*70)
    with open(output_dir / "assignments.csv", "r") as f:
        lines = f.readlines()
        for line in lines[:4]:
            print(f"   {line.rstrip()}")
        if len(lines) > 4:
            print(f"   ... and {len(lines) - 4} more rows")

    print("\n" + "="*70)
    print("SUCCESS! 🎉")
    print("="*70)
    print(f"\nGenerated roster for {len(solution.assignments)} services")
    all_volunteers = set()
    for assignment in solution.assignments:
        all_volunteers.update(assignment.assignees)
    print(f"Assigned {len(all_volunteers)} unique volunteers")
    print(f"Health score: {solution.metrics.health_score:.0f}/100")
    print(f"\nAll files are ready in: {output_dir}/")
    print("\n💡 Tip: Import calendar.ics into your calendar app to see the schedule!")

    return solution


if __name__ == "__main__":
    solution = generate_church_roster()
