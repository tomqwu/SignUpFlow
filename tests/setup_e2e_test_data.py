"""Setup comprehensive E2E test data for all tests."""

import requests
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api"


def setup_e2e_test_data():
    """Create comprehensive test data for E2E tests."""
    print("\n🧪 Setting up comprehensive E2E test data...")

    # Create test organizations
    organizations = [
        {"id": "test_org", "name": "Test Organization", "location": "Test City", "timezone": "America/New_York"},
        {"id": "grace_church", "name": "Grace Church", "location": "New York", "timezone": "America/New_York"},
        {"id": "alpha_org", "name": "Alpha Organization", "location": "Alpha City", "timezone": "America/Los_Angeles"},
        {"id": "beta_org", "name": "Beta Organization", "location": "Beta City", "timezone": "America/Chicago"},
    ]

    for org in organizations:
        resp = requests.post(f"{API_BASE}/organizations/", json=org)
        if resp.status_code in [200, 201]:
            print(f"  ✅ Created organization: {org['name']}")
        elif resp.status_code == 400:
            print(f"  ℹ️  Organization already exists: {org['name']}")
        else:
            print(f"  ⚠️  Failed to create {org['name']}: {resp.status_code} - {resp.text}")

    # Create test users
    users = [
        # Test Organization users
        {"name": "Sarah Johnson", "email": "sarah@test.com", "password": "password", "org_id": "test_org", "roles": ["volunteer"]},
        {"name": "John Doe", "email": "john@test.com", "password": "password", "org_id": "test_org", "roles": ["volunteer"]},
        {"name": "Jane Smith", "email": "jane@test.com", "password": "password", "org_id": "test_org", "roles": ["admin"]},

        # Grace Church users
        {"name": "Pastor Grace", "email": "pastor@grace.church", "password": "password", "org_id": "grace_church", "roles": ["admin"]},
        {"name": "Volunteer Grace", "email": "volunteer@grace.church", "password": "password", "org_id": "grace_church", "roles": ["volunteer"]},

        # Alpha Organization users
        {"name": "Alice Volunteer", "email": "alice.volunteer@alpha.com", "password": "test123", "org_id": "alpha_org", "roles": ["volunteer"]},
        {"name": "Alex Manager", "email": "alex.manager@alpha.com", "password": "test123", "org_id": "alpha_org", "roles": ["volunteer", "admin"]},
        {"name": "Amy Admin", "email": "amy.admin@alpha.com", "password": "test123", "org_id": "alpha_org", "roles": ["admin"]},

        # Beta Organization users
        {"name": "Bob Volunteer", "email": "bob.volunteer@beta.com", "password": "test123", "org_id": "beta_org", "roles": ["volunteer"]},
        {"name": "Ben Admin", "email": "ben.admin@beta.com", "password": "test123", "org_id": "beta_org", "roles": ["admin"]},
    ]

    for user in users:
        resp = requests.post(f"{API_BASE}/auth/signup", json=user)
        if resp.status_code in [200, 201]:
            print(f"  ✅ Created user: {user['name']} ({user['email']})")
        elif resp.status_code == 400 and ("already registered" in resp.text or "already exists" in resp.text):
            print(f"  ℹ️  User already exists: {user['name']}")
        else:
            print(f"  ⚠️  Failed to create {user['name']}: {resp.status_code} - {resp.text}")

    # Create test events for different orgs
    now = datetime.now()
    events = [
        # Test org events
        {
            "id": "event_001",
            "org_id": "test_org",
            "title": "Sunday Service",
            "datetime": (now + timedelta(days=7)).isoformat(),
            "duration": 120,
        },
        {
            "id": "event_002",
            "org_id": "test_org",
            "title": "Youth Meeting",
            "datetime": (now + timedelta(days=14)).isoformat(),
            "duration": 60,
        },

        # Grace Church events
        {
            "id": "grace_event_001",
            "org_id": "grace_church",
            "title": "Sunday Worship",
            "datetime": (now + timedelta(days=7)).isoformat(),
            "duration": 120,
        },

        # Alpha org events
        {
            "id": "alpha_event_001",
            "org_id": "alpha_org",
            "title": "Team Meeting",
            "datetime": (now + timedelta(days=3)).isoformat(),
            "duration": 60,
        },

        # Beta org events
        {
            "id": "beta_event_001",
            "org_id": "beta_org",
            "title": "Project Kickoff",
            "datetime": (now + timedelta(days=5)).isoformat(),
            "duration": 90,
        },
    ]

    # Get admin tokens for creating events
    admin_tokens = {}
    admin_users = [
        ("jane@test.com", "test_org"),
        ("pastor@grace.church", "grace_church"),
        ("amy.admin@alpha.com", "alpha_org"),
        ("ben.admin@beta.com", "beta_org"),
    ]

    for email, org_id in admin_users:
        try:
            resp = requests.post(f"{API_BASE}/auth/login", json={"email": email, "password": "password" if "test" in email or "grace" in email else "test123"})
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                admin_tokens[org_id] = token
        except Exception as e:
            print(f"  ⚠️  Could not get token for {email}: {str(e)}")

    for event in events:
        org_id = event["org_id"]
        if org_id in admin_tokens:
            headers = {"Authorization": f"Bearer {admin_tokens[org_id]}"}
            resp = requests.post(f"{API_BASE}/events/?org_id={org_id}", json=event, headers=headers)
            if resp.status_code in [200, 201]:
                print(f"  ✅ Created event: {event['title']}")
            elif resp.status_code == 400:
                print(f"  ℹ️  Event already exists: {event['title']}")
            else:
                print(f"  ⚠️  Failed to create event {event['title']}: {resp.status_code}")
        else:
            print(f"  ⚠️  No admin token for org {org_id}, skipping event {event['title']}")

    print("\n✅ Comprehensive E2E test data setup complete!\n")


if __name__ == "__main__":
    setup_e2e_test_data()
