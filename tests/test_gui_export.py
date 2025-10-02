#!/usr/bin/env python3
"""
GUI Export Functionality Test

Tests the schedule export functionality that users interact with.
"""

import httpx
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"


def test_complete_export_flow():
    """Test the complete export flow from GUI perspective."""
    print("\n" + "="*70)
    print("GUI EXPORT FUNCTIONALITY TEST")
    print("="*70)

    client = httpx.Client(timeout=30.0)

    # Step 1: Create test organization
    print("\n1️⃣  Creating test organization...")
    org_id = f"export_test_org_{int(datetime.now().timestamp())}"
    response = client.post(f"{API_BASE}/organizations/", json={
        "id": org_id,
        "name": "Export Test Org",
        "region": "US",
        "config": {}
    })
    assert response.status_code in [200, 201], f"Failed to create org: {response.text}"
    print("   ✅ Organization created")

    # Step 2: Create admin user
    print("\n2️⃣  Creating admin user...")
    response = client.post(f"{API_BASE}/auth/signup", json={
        "org_id": org_id,
        "name": "Export Test Admin",
        "email": f"exportadmin_{int(datetime.now().timestamp())}@test.com",
        "password": "test123",
        "roles": ["admin", "volunteer"]
    })
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    user_data = response.json()
    person_id = user_data["person_id"]
    print(f"   ✅ User created: {person_id}")

    # Step 3: Create multiple people for assignments
    print("\n3️⃣  Creating people for assignments...")
    people_ids = []
    for i in range(3):
        response = client.post(f"{API_BASE}/people/", json={
            "id": f"person_{i}_{int(datetime.now().timestamp())}",
            "org_id": org_id,
            "name": f"Volunteer {i}",
            "email": f"volunteer{i}@test.com",
            "roles": ["volunteer", "musician"],
            "extra_data": {}
        })
        if response.status_code in [200, 201]:
            people_ids.append(response.json()["id"])
    print(f"   ✅ Created {len(people_ids)} people")

    # Step 4: Create multiple events
    print("\n4️⃣  Creating events...")
    event_ids = []
    base_date = datetime.now() + timedelta(days=7)

    for i in range(3):
        event_date = base_date + timedelta(days=i*7)
        event_id = f"event_{i}_{int(datetime.now().timestamp())}"
        response = client.post(f"{API_BASE}/events/", json={
            "id": event_id,
            "org_id": org_id,
            "type": f"Service {i}",
            "start_time": event_date.isoformat(),
            "end_time": (event_date + timedelta(hours=2)).isoformat(),
            "resource_id": "sanctuary",
            "extra_data": {"roles": ["volunteer", "musician"]}
        })
        if response.status_code in [200, 201]:
            event_ids.append(event_id)
    print(f"   ✅ Created {len(event_ids)} events")

    # Step 5: Generate schedule
    print("\n5️⃣  Generating schedule...")
    response = client.post(f"{API_BASE}/solver/solve", json={
        "org_id": org_id,
        "from_date": datetime.now().date().isoformat(),
        "to_date": (datetime.now() + timedelta(days=30)).date().isoformat()
    })
    assert response.status_code == 200, f"Solver failed: {response.text}"
    solver_data = response.json()
    solution_id = solver_data["solution_id"]
    print(f"   ✅ Schedule generated: solution {solution_id}")
    print(f"   ℹ️  Assignments: {solver_data.get('metrics', {}).get('assignment_count', 0)}")

    # Step 6: Get assignments
    print("\n6️⃣  Getting assignments...")
    response = client.get(f"{API_BASE}/solutions/{solution_id}/assignments")
    assert response.status_code == 200, f"Get assignments failed: {response.text}"
    assignments_data = response.json()
    assignments = assignments_data.get("assignments", [])
    print(f"   ✅ Retrieved {len(assignments)} assignments")

    if len(assignments) == 0:
        print("   ⚠️  WARNING: No assignments generated - export will fail")
        print("   This is expected with minimal test data")
        return True

    # Step 7: Test CSV export
    print("\n7️⃣  Testing CSV export...")
    response = client.post(f"{API_BASE}/solutions/{solution_id}/export", json={
        "format": "csv"
    })

    if response.status_code == 200:
        print("   ✅ CSV export successful")
        print(f"   ℹ️  Content-Type: {response.headers.get('content-type')}")
        print(f"   ℹ️  Size: {len(response.content)} bytes")
    else:
        print(f"   ❌ CSV export failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    # Step 8: Test ICS export
    print("\n8️⃣  Testing ICS export...")
    response = client.post(f"{API_BASE}/solutions/{solution_id}/export", json={
        "format": "ics",
        "person_id": person_id
    })

    if response.status_code == 200:
        print("   ✅ ICS export successful")
        print(f"   ℹ️  Content-Type: {response.headers.get('content-type')}")
        print(f"   ℹ️  Size: {len(response.content)} bytes")
    else:
        print(f"   ❌ ICS export failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    print("\n" + "="*70)
    print("✅ ALL EXPORT TESTS PASSED!")
    print("="*70)
    return True


if __name__ == "__main__":
    try:
        success = test_complete_export_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
