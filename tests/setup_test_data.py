"""Setup test data for Rostio tests."""

import requests
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api"


def setup_test_data():
    """Create basic test data for tests."""
    print("Setting up test data...")

    # Create test organization
    org_data = {
        "id": "test_org",
        "name": "Test Organization",
        "config": {"roles": ["volunteer", "leader", "admin"]},
    }
    resp = requests.post(f"{API_BASE}/organizations/", json=org_data)
    if resp.status_code in [200, 201]:
        print("✅ Organization created")

    # Create test people
    people = [
        {"id": "sarah", "name": "Sarah Johnson", "email": "sarah@test.com", "org_id": "test_org"},
        {"id": "john", "name": "John Doe", "email": "john@test.com", "org_id": "test_org"},
        {"id": "jane", "name": "Jane Smith", "email": "jane@test.com", "org_id": "test_org"},
    ]

    for person in people:
        resp = requests.post(f"{API_BASE}/people/", json=person)
        if resp.status_code in [200, 201]:
            print(f"✅ Created person: {person['name']}")

    # Create test events
    now = datetime.now()
    events = [
        {
            "id": "event_001",
            "org_id": "test_org",
            "type": "Sunday Service",
            "start_time": (now + timedelta(days=7)).isoformat(),
            "end_time": (now + timedelta(days=7, hours=2)).isoformat(),
        },
        {
            "id": "event_002",
            "org_id": "test_org",
            "type": "Youth Meeting",
            "start_time": (now + timedelta(days=14)).isoformat(),
            "end_time": (now + timedelta(days=14, hours=1)).isoformat(),
        },
    ]

    for event in events:
        resp = requests.post(f"{API_BASE}/events/", json=event)
        if resp.status_code in [200, 201]:
            print(f"✅ Created event: {event['type']}")

    print("✅ Test data setup complete\n")


if __name__ == "__main__":
    setup_test_data()
