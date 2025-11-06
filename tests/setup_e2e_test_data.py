"""Setup comprehensive E2E test data for all tests."""

import os
import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.models import Base, Organization, Person

# Use environment variables for API base URL (supports port 8001 for E2E tests)
APP_URL = os.getenv("E2E_APP_URL", "http://localhost:8000").rstrip("/")
API_BASE = os.getenv("E2E_API_BASE", f"{APP_URL}/api").rstrip("/")


def _resolve_database_url() -> str:
    """Resolve the database URL used by the running API or default to test db."""
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    candidates = [
        "sqlite:///./test_roster.db",
        "sqlite:///./roster.db",
    ]
    for url in candidates:
        path = url.split("///", 1)[-1]
        if os.path.exists(path):
            return url
    return candidates[0]


def _get_session():
    db_url = _resolve_database_url()
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    engine = create_engine(db_url, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _ensure_org(session, org_id: str, name: str) -> None:
    org = session.get(Organization, org_id)
    if org is None:
        org = Organization(id=org_id, name=name, region="Test Region", config={"roles": ["admin", "volunteer"]})
        session.add(org)


def _ensure_admin_role(email: str, org_id: str) -> None:
    SessionLocal = _get_session()
    session = SessionLocal()
    try:
        _ensure_org(session, org_id, org_id.replace("_", " ").title())
        person = session.query(Person).filter(Person.email == email).one_or_none()
        if person is None:
            return
        person.org_id = org_id
        roles = set(person.roles or [])
        if "admin" not in roles:
            roles.add("admin")
            person.roles = list(roles)
        session.commit()
    finally:
        session.close()


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
        # Test Organization users (admin first)
        {"name": "Jane Smith", "email": "jane@test.com", "password": "password", "org_id": "test_org", "roles": ["admin"]},
        {"name": "Sarah Johnson", "email": "sarah@test.com", "password": "password", "org_id": "test_org", "roles": ["volunteer"]},
        {"name": "John Doe", "email": "john@test.com", "password": "password", "org_id": "test_org", "roles": ["volunteer"]},

        # Grace Church users (admin first)
        {"name": "Pastor Grace", "email": "pastor@grace.church", "password": "password", "org_id": "grace_church", "roles": ["admin"]},
        {"name": "Volunteer Grace", "email": "volunteer@grace.church", "password": "password", "org_id": "grace_church", "roles": ["volunteer"]},

        # Alpha Organization users (admin first)
        {"name": "Amy Admin", "email": "amy.admin@alpha.com", "password": "test123", "org_id": "alpha_org", "roles": ["admin"]},
        {"name": "Alex Manager", "email": "alex.manager@alpha.com", "password": "test123", "org_id": "alpha_org", "roles": ["volunteer", "admin"]},
        {"name": "Alice Volunteer", "email": "alice.volunteer@alpha.com", "password": "test123", "org_id": "alpha_org", "roles": ["volunteer"]},

        # Beta Organization users (admin first)
        {"name": "Ben Admin", "email": "ben.admin@beta.com", "password": "test123", "org_id": "beta_org", "roles": ["admin"]},
        {"name": "Bob Volunteer", "email": "bob.volunteer@beta.com", "password": "test123", "org_id": "beta_org", "roles": ["volunteer"]},
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
    super_admin_resp = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": "jane@test.com", "password": "password"},
    )
    super_admin_headers = None
    if super_admin_resp.status_code == 200:
        super_token = super_admin_resp.json().get("token") or super_admin_resp.json().get("access_token")
        if super_token:
            super_admin_headers = {"Authorization": f"Bearer {super_token}"}
    admin_users = [
        ("jane@test.com", "test_org"),
        ("pastor@grace.church", "grace_church"),
        ("amy.admin@alpha.com", "alpha_org"),
        ("ben.admin@beta.com", "beta_org"),
    ]

    for email, org_id in admin_users:
        try:
            resp = requests.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": email,
                    "password": "password" if "test" in email or "grace" in email else "test123",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                roles = data.get("roles") or data.get("user", {}).get("roles") or []
                if "admin" not in roles:
                    _ensure_admin_role(email, org_id)
                    resp = requests.post(
                        f"{API_BASE}/auth/login",
                        json={
                            "email": email,
                            "password": "password" if "test" in email or "grace" in email else "test123",
                        },
                    )
                    if resp.status_code != 200:
                        print(f"  ⚠️  Unable to elevate {email} to admin (login failed after role fix): {resp.status_code}")
                        continue
                    data = resp.json()
                    roles = data.get("roles") or data.get("user", {}).get("roles") or []
                    if "admin" not in roles:
                        print(f"  ⚠️  Unable to elevate {email} to admin (roles still {roles})")
                        continue
                token = data.get("token") or data.get("access_token")
                if token:
                    admin_tokens[org_id] = token
                else:
                    print(f"  ⚠️  Login response for {email} did not include a token")
        except Exception as e:
            print(f"  ⚠️  Could not get token for {email}: {str(e)}")

    for event in events:
        org_id = event["org_id"]
        if org_id in admin_tokens:
            headers = {"Authorization": f"Bearer {admin_tokens[org_id]}"}
            start_dt = datetime.fromisoformat(event["datetime"])
            end_dt = start_dt + timedelta(minutes=event.get("duration", 60))
            payload = {
                "id": event["id"],
                "org_id": org_id,
                "type": event.get("type") or event.get("title", "Generated Event"),
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
                "extra_data": event.get("extra_data") or {"role_counts": {"volunteer": 2, "leader": 1}},
            }
            resp = requests.post(
                f"{API_BASE}/events/",
                json=payload,
                headers=headers,
                timeout=10,
            )
            if resp.status_code in [200, 201]:
                print(f"  ✅ Created event: {payload['type']}")
            elif resp.status_code == 400:
                print(f"  ℹ️  Event already exists: {payload['type']}")
            else:
                print(f"  ⚠️  Failed to create event {payload['type']}: {resp.status_code} - {resp.text}")
        else:
            print(f"  ⚠️  No admin token for org {org_id}, skipping event {event.get('title', event['id'])}")

    print("\n✅ Comprehensive E2E test data setup complete!\n")


if __name__ == "__main__":
    setup_e2e_test_data()
