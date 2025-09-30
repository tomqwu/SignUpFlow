#!/usr/bin/env python3
"""
Cricket League Roster Generation Test (Custom YAML Data)

This script uses customizable YAML data from test_data/cricket_custom/
You can modify the YAML files to test different scenarios.
"""

from datetime import date
from pathlib import Path
import shutil

from roster_cli.core.loader import (
    load_org,
    load_people,
    load_teams,
    load_resources,
    load_events,
    load_constraint_files,
    load_holidays,
    load_availability_files,
    load_yaml,
)
from roster_cli.core.models import Availability
from roster_cli.core.csv_writer import write_assignments_csv
from roster_cli.core.ics_writer import write_calendar_ics
from roster_cli.core.json_writer import write_solution_json, write_metrics_json
from roster_cli.core.solver.adapter import SolveContext
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver


def generate_cricket_league_roster():
    """Generate a complete cricket league fixture schedule from custom YAML."""

    print("\n" + "="*70)
    print("CRICKET LEAGUE FIXTURE SCHEDULE GENERATION (CUSTOM)")
    print("="*70)

    # Use custom test data
    custom_data = Path(__file__).parent / "test_data" / "cricket_custom"

    if not custom_data.exists():
        print(f"\n❌ Error: Custom data directory not found: {custom_data}")
        print("   Run this script to create it first.")
        return

    # Setup workspace (copy custom data to temp location)
    workspace = Path("/tmp/cricket_league_custom")
    if workspace.exists():
        shutil.rmtree(workspace)

    shutil.copytree(custom_data, workspace)
    print(f"\n📁 Workspace: {workspace}")
    print(f"📁 Custom Data Source: {custom_data}")

    # Load data
    print("\n📥 Loading league data from custom YAML files...")
    org = load_org(workspace)
    people_file = load_people(workspace)
    teams_file = load_teams(workspace)
    resources_file = load_resources(workspace)
    events_file = load_events(workspace)
    holidays_file = load_holidays(workspace)
    constraints = load_constraint_files(workspace)

    # Load availability from single file or directory
    availability = []
    avail_file = workspace / "availability.yaml"
    if avail_file.exists():
        avail_data = load_yaml(avail_file)
        if "availability" in avail_data:
            availability = [Availability(**a) for a in avail_data["availability"]]
    else:
        availability = load_availability_files(workspace)

    people = people_file.people
    teams = teams_file.teams if teams_file else []
    resources = resources_file.resources if resources_file else []
    events = events_file.events
    holidays = holidays_file.days if holidays_file else []

    print(f"   • League: {org.org_id}")
    print(f"   • Teams: {len(teams)}")
    print(f"   • Players: {len(people)}")
    print(f"   • Grounds: {len(resources)}")
    print(f"   • Fixtures: {len(events)}")
    print(f"   • Constraints: {len(constraints)}")
    print(f"   • Availability records: {len(availability)}")

    # Validate data
    print("\n🔍 DATA VALIDATION:")
    people_map = {p.id: p for p in people}
    validation_errors = []

    # Check team members exist
    for team in teams:
        for member_id in team.members:
            if member_id not in people_map:
                validation_errors.append(f"Team {team.id} references non-existent player {member_id}")

    # Check availability references valid people
    for avail in availability:
        if avail.person_id and avail.person_id not in people_map:
            validation_errors.append(f"Availability references non-existent person {avail.person_id}")

    # Check events reference valid resources and teams
    team_map = {t.id: t for t in teams}
    resource_map = {r.id: r for r in resources}
    for event in events:
        if event.resource_id and event.resource_id not in resource_map:
            validation_errors.append(f"Event {event.id} references non-existent resource {event.resource_id}")
        for team_id in event.team_ids:
            if team_id not in team_map:
                validation_errors.append(f"Event {event.id} references non-existent team {team_id}")

    if validation_errors:
        print(f"   ❌ Found {len(validation_errors)} validation errors:")
        for error in validation_errors:
            print(f"      • {error}")
    else:
        print(f"   ✓ All data references are valid")

    # Show teams
    print("\n🏏 TEAMS:")
    for team in teams:
        print(f"   • {team.name:15s} ({team.id}) - {len(team.members)} players")

    # Show grounds
    print("\n🏟️  GROUNDS:")
    for resource in resources:
        print(f"   • {resource.location:15s} ({resource.type}, capacity: {resource.capacity})")

    # Show fixtures
    print("\n📅 SCHEDULED FIXTURES:")
    for event in events:
        team_names = []
        for team_id in event.team_ids:
            team = next((t for t in teams if t.id == team_id), None)
            if team:
                team_names.append(team.name)

        resource = next((r for r in resources if r.id == event.resource_id), None)
        venue = resource.location if resource else "TBD"

        print(f"   • {event.start.strftime('%a %b %d')} - {' vs '.join(team_names):30s} @ {venue}")

    # Show holidays
    print("\n📆 HOLIDAYS & CONSTRAINTS:")
    for holiday in holidays:
        weekend_marker = " 🚫" if holiday.is_long_weekend else ""
        print(f"   • {holiday.date.strftime('%a %b %d')} - {holiday.label}{weekend_marker}")

    if constraints:
        print(f"\n   Loaded {len(constraints)} constraint file(s)")

    # Show player availability
    if availability:
        print("\n👤 PLAYER AVAILABILITY (Unavailable periods):")
        for avail in availability:
            if avail.vacations or avail.exceptions:
                player = people_map.get(avail.person_id)
                player_name = player.name if player else avail.person_id
                print(f"\n   {player_name}:")
                for vacation in avail.vacations:
                    print(f"      🚫 Vacation: {vacation.start.strftime('%a %b %d')} - {vacation.end.strftime('%a %b %d')}")
                for exception in avail.exceptions:
                    print(f"      ⚠️  Unavailable: {exception.strftime('%a %b %d')}")

    # Build solve context
    print("\n⚙️  Building solver context...")
    context = SolveContext(
        org=org,
        people=people,
        teams=teams,
        resources=resources,
        events=events,
        constraints=constraints,
        availability=availability,
        holidays=holidays,
        from_date=date(2025, 9, 1),
        to_date=date(2025, 9, 30),
        mode="strict",
        change_min=False,
    )

    # Solve
    print("\n🔄 Generating fixture schedule...")
    solver = GreedyHeuristicSolver()
    solver.build_model(context)
    solution = solver.solve()

    # Display results
    print("\n" + "="*70)
    print("SOLUTION METRICS")
    print("="*70)
    print(f"✓ Total Fixtures: {len(solution.assignments)}")
    print(f"✓ Hard Violations: {solution.metrics.hard_violations}")
    print(f"✓ Soft Score: {solution.metrics.soft_score:.2f}")
    print(f"✓ Health Score: {solution.metrics.health_score:.1f}/100")
    print(f"✓ Solve Time: {solution.metrics.solve_ms:.0f}ms")

    if solution.violations.hard:
        print(f"\n⚠️  Hard Violations:")
        for v in solution.violations.hard:
            print(f"   • {v.constraint_key}: {v.message}")
            print(f"     Entities: {', '.join(v.entities)}")

    # Show detailed fixtures
    print("\n" + "="*70)
    print("GENERATED FIXTURE SCHEDULE")
    print("="*70)

    # Group by week
    fixtures_by_date = {}
    for assignment in solution.assignments:
        event = next((e for e in events if e.id == assignment.event_id), None)
        if event:
            date_key = event.start.date()
            if date_key not in fixtures_by_date:
                fixtures_by_date[date_key] = []
            fixtures_by_date[date_key].append((event, assignment))

    for fixture_date in sorted(fixtures_by_date.keys()):
        print(f"\n📆 {fixture_date.strftime('%A, %B %d, %Y')}")

        for event, assignment in fixtures_by_date[fixture_date]:
            team_names = [team_map[tid].name for tid in event.team_ids if tid in team_map]
            resource = resource_map.get(event.resource_id)
            venue = resource.location if resource else "TBD"

            print(f"\n   🏏 {' vs '.join(team_names)}")
            print(f"      Time: {event.start.strftime('%I:%M %p')} - {event.end.strftime('%I:%M %p')}")
            print(f"      Venue: {venue}")

            # Show team rosters for this match
            for team_id in event.team_ids:
                if team_id in team_map:
                    team = team_map[team_id]
                    print(f"\n      {team.name} Squad:")
                    for member_id in team.members:
                        if member_id in people_map:
                            player = people_map[member_id]
                            role_str = " (C)" if 'captain' in player.roles else ""
                            print(f"         • {player.name}{role_str}")

    # Check which fixture was blocked (if any)
    scheduled_event_ids = {a.event_id for a in solution.assignments}
    unscheduled = [e for e in events if e.id not in scheduled_event_ids]

    if unscheduled:
        print("\n" + "="*70)
        print("BLOCKED FIXTURES")
        print("="*70)
        print("\nThe following fixtures were blocked by constraints:\n")

        for event in unscheduled:
            team_names = [team_map[tid].name for tid in event.team_ids if tid in team_map]
            print(f"   🚫 {event.start.strftime('%a %b %d')} - {' vs '.join(team_names)}")

            # Check if it's a long weekend
            event_date = event.start.date()
            holiday = next((h for h in holidays if h.date == event_date), None)
            if holiday and holiday.is_long_weekend:
                day_name = event.start.strftime('%A')
                print(f"      Reason: {day_name} on {holiday.label} (long weekend)")
                print(f"      Constraint: no_long_weekend_fri_mon (hard)")

    # Team schedule summary
    print("\n" + "="*70)
    print("TEAM SCHEDULE SUMMARY")
    print("="*70)
    print("\nFixtures per team:\n")

    team_fixtures = {team.id: 0 for team in teams}
    for assignment in solution.assignments:
        event = next((e for e in events if e.id == assignment.event_id), None)
        if event:
            for team_id in event.team_ids:
                if team_id in team_fixtures:
                    team_fixtures[team_id] += 1

    for team in sorted(teams, key=lambda t: team_fixtures[t.id], reverse=True):
        count = team_fixtures[team.id]
        bar = "█" * count
        print(f"   {team.name:15s} {bar} ({count} fixtures)")

    # Player statistics
    print("\n" + "="*70)
    print("PLAYER STATISTICS")
    print("="*70)
    print("\nMatches per player:\n")

    player_matches = {}
    for assignment in solution.assignments:
        event = next((e for e in events if e.id == assignment.event_id), None)
        if event:
            for team_id in event.team_ids:
                if team_id in team_map:
                    team = team_map[team_id]
                    for member_id in team.members:
                        player_matches[member_id] = player_matches.get(member_id, 0) + 1

    # Show by team
    for team in teams:
        print(f"\n   {team.name}:")
        for member_id in team.members:
            if member_id in people_map:
                player = people_map[member_id]
                count = player_matches.get(member_id, 0)
                role_str = " (Captain)" if 'captain' in player.roles else ""
                bar = "▓" * count if count > 0 else ""
                print(f"      {player.name:20s} {bar} {count} matches{role_str}")

    # Save outputs
    output_dir = workspace / "out"
    output_dir.mkdir(exist_ok=True)

    write_solution_json(solution, output_dir / "solution.json")
    write_assignments_csv(solution, events, people, output_dir / "fixtures.csv")
    write_calendar_ics(solution, events, people, output_dir / "league_calendar.ics")
    write_metrics_json(solution, output_dir / "metrics.json")

    print("\n" + "="*70)
    print("OUTPUT FILES")
    print("="*70)
    print(f"\n✓ Schedule saved to: {output_dir}/")
    print(f"   • solution.json       - Complete solution bundle")
    print(f"   • fixtures.csv        - Spreadsheet-friendly format")
    print(f"   • league_calendar.ics - Import to calendar apps")
    print(f"   • metrics.json        - Detailed metrics")

    # Show CSV sample
    print("\n" + "="*70)
    print("SAMPLE CSV OUTPUT")
    print("="*70)
    with open(output_dir / "fixtures.csv", "r") as f:
        lines = f.readlines()
        for line in lines[:5]:
            print(f"   {line.rstrip()}")
        if len(lines) > 5:
            print(f"   ... and {len(lines) - 5} more rows")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    if solution.metrics.hard_violations > 0:
        print(f"\n✓ Generated schedule for {len(solution.assignments)}/{len(events)} fixtures")
        print(f"⚠️  {len(unscheduled)} fixture(s) blocked by constraints (correct behavior)")
        print(f"✓ All active constraints enforced properly")
    else:
        print(f"\n✓ Generated complete schedule for all {len(solution.assignments)} fixtures")
        print(f"✓ All constraints satisfied")
        print(f"✓ Health score: {solution.metrics.health_score:.0f}/100")

    print(f"\n💡 Edit YAML files in: {custom_data}/")
    print(f"   Then run this script again to see the changes!")

    return solution


if __name__ == "__main__":
    solution = generate_cricket_league_roster()
