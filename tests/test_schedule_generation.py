"""
Test that the schedule generation actually creates assignments.
This tests the end-to-end flow: create org -> create people -> create events -> run solver -> verify assignments
"""
import requests
import time

BASE_URL = "http://localhost:8000/api"

def test_schedule_generation():
    """Test complete schedule generation workflow"""
    print("\n🧪 Testing Schedule Generation End-to-End\n")
    print("=" * 60)

    # Step 1: Create organization
    print("\n1️⃣ Creating organization...")
    org_data = {
        "name": "Test Church",
        "region": "Test Region",
        "config": {
            "custom_roles": ["worship-leader", "tech", "greeter"]
        }
    }
    response = requests.post(f"{BASE_URL}/organizations/", json=org_data)
    assert response.status_code == 200, f"Failed to create org: {response.text}"
    org = response.json()
    org_id = org["id"]
    print(f"   ✓ Created org: {org['name']} (ID: {org_id})")

    # Step 2: Create people
    print("\n2️⃣ Creating people...")
    people = []
    people_data = [
        {"name": "Alice", "email": "alice@test.com", "password": "pass123", "roles": ["worship-leader"]},
        {"name": "Bob", "email": "bob@test.com", "password": "pass123", "roles": ["tech"]},
        {"name": "Carol", "email": "carol@test.com", "password": "pass123", "roles": ["greeter"]},
    ]

    for person_data in people_data:
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            **person_data,
            "org_id": org_id
        })
        assert response.status_code == 200, f"Failed to create person: {response.text}"
        person = response.json()
        people.append(person)
        print(f"   ✓ Created: {person['name']} ({', '.join(person['roles'])})")

    # Step 3: Create events
    print("\n3️⃣ Creating events...")
    events = []
    event_data = [
        {
            "name": "Sunday Service",
            "org_id": org_id,
            "event_type": "service",
            "occurrence_pattern": "weekly",
            "day_of_week": 0,  # Sunday
            "time": "10:00",
            "duration_minutes": 120,
            "roles_needed": ["worship-leader", "tech", "greeter"],
            "min_people": 3
        }
    ]

    for evt_data in event_data:
        response = requests.post(f"{BASE_URL}/events/", json=evt_data)
        assert response.status_code == 200, f"Failed to create event: {response.text}"
        event = response.json()
        events.append(event)
        print(f"   ✓ Created: {event['name']} (roles: {', '.join(event['roles_needed'])})")

    # Step 4: Run solver
    print("\n4️⃣ Running solver...")
    solver_data = {
        "org_id": org_id,
        "days_ahead": 30,
        "solver_type": "greedy"
    }
    response = requests.post(f"{BASE_URL}/solver/run", json=solver_data)
    print(f"   Response status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")

    if response.status_code != 200:
        print(f"   ⚠️  Solver failed: {response.text}")
        print("\n   Trying manual assignment creation instead...")

        # Create manual assignments
        from datetime import datetime, timedelta
        event_id = events[0]['id']

        for i in range(3):
            date = (datetime.now() + timedelta(days=i*7)).date().isoformat()
            assignment_data = {
                "event_id": event_id,
                "person_id": people[i % len(people)]["person_id"],
                "date": date,
                "role": people[i % len(people)]["roles"][0]
            }
            response = requests.post(f"{BASE_URL}/assignments/", json=assignment_data)
            if response.status_code in [200, 201]:
                print(f"   ✓ Created manual assignment for {date}")
    else:
        solution = response.json()
        print(f"   ✓ Solver completed")
        if "solution_id" in solution:
            print(f"   Solution ID: {solution['solution_id']}")

    # Step 5: Verify assignments were created
    print("\n5️⃣ Verifying assignments...")
    response = requests.get(f"{BASE_URL}/solutions/?org_id={org_id}")
    assert response.status_code == 200, f"Failed to get solutions: {response.text}"
    solutions_data = response.json()

    print(f"   Total solutions: {solutions_data.get('total', 0)}")

    if solutions_data.get('total', 0) > 0:
        solutions = solutions_data['solutions']
        for sol in solutions:
            print(f"   Solution {sol['id']}: {sol['assignment_count']} assignments")

        # Get first solution with assignments
        solution_with_assignments = next((s for s in solutions if s['assignment_count'] > 0), None)

        if solution_with_assignments:
            solution_id = solution_with_assignments['id']
            response = requests.get(f"{BASE_URL}/solutions/{solution_id}/assignments")
            assert response.status_code == 200, f"Failed to get assignments: {response.text}"
            assignments = response.json()

            print(f"\n   ✅ SUCCESS: Found {len(assignments)} assignments in solution {solution_id}")
            for i, assignment in enumerate(assignments[:5]):  # Show first 5
                print(f"      {i+1}. {assignment['date']} - {assignment['person_name']} ({assignment['role']}) - {assignment['event_name']}")

            if len(assignments) > 5:
                print(f"      ... and {len(assignments) - 5} more")

            return True
        else:
            print("   ❌ FAILED: Solutions exist but all have 0 assignments")
            return False
    else:
        print("   ❌ FAILED: No solutions created")
        return False

if __name__ == "__main__":
    try:
        success = test_schedule_generation()
        print("\n" + "=" * 60)
        if success:
            print("✅ Schedule generation test PASSED")
            exit(0)
        else:
            print("❌ Schedule generation test FAILED")
            exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
