#!/usr/bin/env python3
"""
Complete API Client Example

This demonstrates the full workflow of using the Roster API:
1. Create an organization
2. Add people, teams, events
3. Add constraints
4. Solve the schedule
5. Retrieve and export the solution
"""

import httpx
from datetime import datetime, date, timedelta
import json

# API Base URL
API_URL = "http://localhost:8000"


def main():
    """Run complete API workflow."""
    print("\n" + "=" * 70)
    print("ROSTER API CLIENT EXAMPLE")
    print("=" * 70)

    with httpx.Client(base_url=API_URL, timeout=30.0) as client:
        # 1. Health check
        print("\n[1/8] Checking API health...")
        response = client.get("/health")
        print(f"✓ API Status: {response.json()['status']}")

        # 2. Create organization
        print("\n[2/8] Creating organization...")
        org_data = {
            "id": "demo_cricket_league",
            "name": "Demo Cricket League",
            "region": "AU-NSW",
            "config": {
                "change_min_weight": 100,
                "fairness_weight": 50,
                "cooldown_days": 7,
            },
        }
        response = client.post("/organizations/", json=org_data)
        if response.status_code == 201:
            print(f"✓ Created organization: {org_data['name']}")
        elif response.status_code == 409:
            print(f"ℹ Organization already exists")
        else:
            print(f"✗ Error: {response.text}")
            return

        # 3. Add people
        print("\n[3/8] Adding people...")
        people = [
            {"id": "player_01", "org_id": org_data["id"], "name": "Alice Smith", "roles": ["batsman", "captain"]},
            {"id": "player_02", "org_id": org_data["id"], "name": "Bob Johnson", "roles": ["bowler"]},
            {"id": "player_03", "org_id": org_data["id"], "name": "Charlie Brown", "roles": ["wicketkeeper"]},
            {"id": "player_04", "org_id": org_data["id"], "name": "Diana Prince", "roles": ["all-rounder"]},
            {"id": "player_05", "org_id": org_data["id"], "name": "Eve Adams", "roles": ["batsman"]},
            {"id": "player_06", "org_id": org_data["id"], "name": "Frank Miller", "roles": ["bowler"]},
        ]

        for person in people:
            response = client.post("/people/", json=person)
            if response.status_code in [201, 409]:
                print(f"  ✓ {person['name']}")

        # 4. Create teams
        print("\n[4/8] Creating teams...")
        teams = [
            {
                "id": "team_lions",
                "org_id": org_data["id"],
                "name": "Lions",
                "description": "Team Lions",
                "member_ids": ["player_01", "player_02", "player_03"],
            },
            {
                "id": "team_tigers",
                "org_id": org_data["id"],
                "name": "Tigers",
                "description": "Team Tigers",
                "member_ids": ["player_04", "player_05", "player_06"],
            },
        ]

        for team in teams:
            response = client.post("/teams/", json=team)
            if response.status_code in [201, 409]:
                print(f"  ✓ {team['name']} ({len(team['member_ids'])} members)")

        # 5. Create events
        print("\n[5/8] Creating events...")
        base_date = datetime.now() + timedelta(days=7)
        events = []

        for i in range(4):  # Create 4 matches over 2 weeks
            event_date = base_date + timedelta(days=i * 3)
            event = {
                "id": f"match_{i+1:02d}",
                "org_id": org_data["id"],
                "type": "cricket_match",
                "start_time": event_date.isoformat(),
                "end_time": (event_date + timedelta(hours=4)).isoformat(),
                "team_ids": ["team_lions", "team_tigers"] if i % 2 == 0 else ["team_tigers", "team_lions"],
            }
            events.append(event)
            response = client.post("/events/", json=event)
            if response.status_code in [201, 409]:
                print(f"  ✓ Match {i+1}: {event_date.strftime('%Y-%m-%d')}")

        # 6. Add constraints
        print("\n[6/8] Adding constraints...")
        constraints = [
            {
                "org_id": org_data["id"],
                "key": "min_rest_hours",
                "type": "hard",
                "predicate": "enforce_min_gap_hours",
                "params": {"hours": 24},
            },
            {
                "org_id": org_data["id"],
                "key": "fairness",
                "type": "soft",
                "weight": 50,
                "predicate": "balance_assignments",
                "params": {},
            },
        ]

        for constraint in constraints:
            response = client.post("/constraints/", json=constraint)
            if response.status_code in [201, 409]:
                print(f"  ✓ {constraint['key']} ({constraint['type']})")

        # 7. Solve the schedule
        print("\n[7/8] Solving schedule...")
        solve_request = {
            "org_id": org_data["id"],
            "from_date": base_date.date().isoformat(),
            "to_date": (base_date + timedelta(days=14)).date().isoformat(),
            "mode": "strict",
            "change_min": False,
        }

        response = client.post("/solver/solve", json=solve_request)
        if response.status_code == 200:
            solution = response.json()
            print(f"\n  ✓ Solution generated!")
            print(f"    Solution ID: {solution['solution_id']}")
            print(f"    Assignments: {solution['assignment_count']}")
            print(f"    Hard violations: {solution['metrics']['hard_violations']}")
            print(f"    Health score: {solution['metrics']['health_score']:.1f}/100")
            print(f"    Solve time: {solution['metrics']['solve_ms']:.0f}ms")

            solution_id = solution["solution_id"]
        else:
            print(f"  ✗ Error solving: {response.text}")
            return

        # 8. Get solution details
        print(f"\n[8/8] Retrieving solution details...")

        # Get assignments
        response = client.get(f"/solutions/{solution_id}/assignments")
        if response.status_code == 200:
            data = response.json()
            print(f"\n  ✓ Retrieved {data['total']} assignments:")
            for assignment in data["assignments"][:5]:
                print(f"    • {assignment['person_name']} → {assignment['event_id']} ({assignment['event_start']})")
            if data['total'] > 5:
                print(f"    ... and {data['total'] - 5} more")

        # Export as CSV
        print(f"\n  Exporting solution...")
        export_request = {"format": "csv", "scope": "org"}
        response = client.post(f"/solutions/{solution_id}/export", json=export_request)
        if response.status_code == 200:
            csv_content = response.text
            print(f"  ✓ CSV export ({len(csv_content)} bytes)")
            # Show first few lines
            lines = csv_content.split('\n')[:4]
            for line in lines:
                print(f"    {line}")

        # Export as JSON
        export_request = {"format": "json", "scope": "org"}
        response = client.post(f"/solutions/{solution_id}/export", json=export_request)
        if response.status_code == 200:
            json_content = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"  ✓ JSON export ready")

        # List all solutions
        print(f"\n  Solutions for organization:")
        response = client.get(f"/solutions/?org_id={org_data['id']}")
        if response.status_code == 200:
            data = response.json()
            for sol in data["solutions"]:
                print(f"    • Solution {sol['id']}: {sol['assignment_count']} assignments, health={sol['health_score']:.0f}")

    print("\n" + "=" * 70)
    print("COMPLETE! 🎉")
    print("=" * 70)
    print(f"\nAPI Documentation: {API_URL}/docs")
    print(f"Alternative Docs: {API_URL}/redoc")
    print("\nYou can now:")
    print(f"  • View all organizations: GET {API_URL}/organizations/")
    print(f"  • View all people: GET {API_URL}/people/?org_id={org_data['id']}")
    print(f"  • View all events: GET {API_URL}/events/?org_id={org_data['id']}")
    print(f"  • View solutions: GET {API_URL}/solutions/?org_id={org_data['id']}")
    print()


if __name__ == "__main__":
    main()
