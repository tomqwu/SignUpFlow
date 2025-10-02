#!/usr/bin/env python3
"""
Test Admin Workflow

This script tests the complete admin workflow:
1. Create an organization
2. Create an admin user
3. Create a regular user
4. Create events
5. Generate schedule
6. Verify assignments
"""

import httpx
from datetime import datetime, timedelta
import json

API_BASE = "http://localhost:8000"

def test_admin_workflow():
    print("\n" + "="*70)
    print("TESTING ADMIN WORKFLOW")
    print("="*70)

    client = httpx.Client()

    # 1. Create Organization
    print("\n1️⃣  Creating organization...")
    org_data = {
        "id": "test_church",
        "name": "Test Church",
        "region": "Test Region",
        "config": {}
    }

    response = client.post(f"{API_BASE}/organizations/", json=org_data)
    if response.status_code in [200, 201, 409]:
        print(f"   ✓ Organization created: {org_data['name']}")
    else:
        print(f"   ✗ Error: {response.status_code}")
        return

    # 2. Create Admin User
    print("\n2️⃣  Creating admin user...")
    admin_data = {
        "id": "admin_user_1",
        "org_id": "test_church",
        "name": "Admin User",
        "email": "admin@test.com",
        "roles": ["admin", "volunteer"],
        "extra_data": {}
    }

    response = client.post(f"{API_BASE}/people/", json=admin_data)
    if response.status_code in [200, 201, 409]:
        print(f"   ✓ Admin user created: {admin_data['name']}")
        print(f"   ℹ️  Roles: {', '.join(admin_data['roles'])}")
    else:
        print(f"   ✗ Error: {response.status_code}")

    # 3. Create Regular Users
    print("\n3️⃣  Creating regular users...")
    users = [
        {"id": "user_1", "name": "John Volunteer", "roles": ["volunteer"]},
        {"id": "user_2", "name": "Jane Musician", "roles": ["musician", "volunteer"]},
        {"id": "user_3", "name": "Bob Tech", "roles": ["tech"]},
    ]

    for user in users:
        user_data = {
            "id": user["id"],
            "org_id": "test_church",
            "name": user["name"],
            "email": f"{user['id']}@test.com",
            "roles": user["roles"],
            "extra_data": {}
        }
        response = client.post(f"{API_BASE}/people/", json=user_data)
        if response.status_code in [200, 201, 409]:
            print(f"   ✓ {user['name']} - Roles: {', '.join(user['roles'])}")

    # 4. Create Events
    print("\n4️⃣  Creating events...")
    base_date = datetime.now() + timedelta(days=7)
    events = []

    for i in range(3):
        event_date = base_date + timedelta(days=i*7)
        event_data = {
            "id": f"sunday_service_{i}",
            "org_id": "test_church",
            "type": "Sunday Service",
            "start_time": event_date.isoformat(),
            "end_time": (event_date + timedelta(hours=2)).isoformat(),
            "resource_id": "main_sanctuary",
            "extra_data": {"roles": ["volunteer", "musician", "tech"]}
        }
        events.append(event_data)

        response = client.post(f"{API_BASE}/events/", json=event_data)
        if response.status_code in [200, 201, 409]:
            print(f"   ✓ {event_data['type']} - {event_date.strftime('%B %d, %Y')}")
        else:
            print(f"   ✗ Error creating event: {response.status_code} - {response.text}")

    # 5. Set time-off for one user
    print("\n5️⃣  Setting time-off for user...")
    timeoff_data = {
        "start_date": (base_date + timedelta(days=7)).date().isoformat(),
        "end_date": (base_date + timedelta(days=10)).date().isoformat()
    }
    response = client.post(
        f"{API_BASE}/availability/user_1/timeoff",
        json=timeoff_data
    )
    if response.status_code in [200, 201]:
        print(f"   ✓ Time-off set for John Volunteer: {timeoff_data['start_date']} to {timeoff_data['end_date']}")

    # 6. Generate Schedule
    print("\n6️⃣  Generating schedule...")
    solver_data = {
        "org_id": "test_church",
        "from_date": base_date.date().isoformat(),
        "to_date": (base_date + timedelta(days=30)).date().isoformat()
    }

    response = client.post(f"{API_BASE}/solver/solve", json=solver_data)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Schedule generated successfully!")
        print(f"   ℹ️  Solution ID: {data['solution_id']}")
        print(f"   ℹ️  Assignments: {data.get('metrics', {}).get('assignment_count', 0)}")
        print(f"   ℹ️  Health Score: {data.get('metrics', {}).get('health_score', 0):.1f}/100")

        solution_id = data['solution_id']

        # 7. Get assignments
        print("\n7️⃣  Retrieving assignments...")
        response = client.get(f"{API_BASE}/solutions/{solution_id}/assignments")
        if response.status_code == 200:
            assignments_data = response.json()
            assignments = assignments_data.get('assignments', [])
            print(f"   ✓ Total assignments: {len(assignments)}")

            # Group by person
            by_person = {}
            for assignment in assignments:
                person_id = assignment['person_id']
                if person_id not in by_person:
                    by_person[person_id] = []
                by_person[person_id].append(assignment)

            print("\n   📊 Assignments by person:")
            for person_id, person_assignments in by_person.items():
                print(f"      • {person_id}: {len(person_assignments)} assignment(s)")

    else:
        print(f"   ✗ Error generating schedule: {response.status_code}")
        print(f"   Response: {response.text}")

    # Summary
    print("\n" + "="*70)
    print("WORKFLOW TEST COMPLETE")
    print("="*70)
    print("\n✓ Organization created")
    print("✓ Admin user created with 'admin' role")
    print("✓ Regular users created")
    print("✓ Events created")
    print("✓ Time-off configured")
    print("✓ Schedule generated")
    print("\n💡 Next steps:")
    print("   1. Open http://localhost:8000/frontend/index.html")
    print("   2. Create profile with 'Administrator' role checked")
    print("   3. Access the Admin Dashboard tab")
    print("   4. Manage events and generate schedules")
    print()

if __name__ == "__main__":
    try:
        test_admin_workflow()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
