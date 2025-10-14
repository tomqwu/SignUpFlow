"""E2E tests for RBAC security implementation.

Tests comprehensive role-based access control including:
- Volunteer (read-only, self-edit)
- Manager (extended read, limited write)
- Admin (full control within organization)
- Organization isolation
- Role escalation prevention
"""

import pytest
import requests
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api"

# Cache for person_ids (email -> person_id)
_person_id_cache = {}


@pytest.fixture(scope="module")
def test_organizations():
    """Create two test organizations for isolation testing."""
    orgs = [
        {
            "id": "org_alpha",
            "name": "Alpha Organization",
            "config": {"roles": ["volunteer", "manager", "admin"]},
        },
        {
            "id": "org_beta",
            "name": "Beta Organization",
            "config": {"roles": ["volunteer", "manager", "admin"]},
        },
    ]

    for org in orgs:
        resp = requests.post(f"{API_BASE}/organizations/", json=org)
        if resp.status_code in [200, 201, 409]:
            print(f"✓ Organization ready: {org['name']}")

    return orgs


@pytest.fixture(scope="module")
def test_users(test_organizations):
    """Create test users with different roles across organizations."""
    users = [
        # Organization Alpha users
        {
            "name": "Alice Volunteer",
            "email": "alice.volunteer@alpha.com",
            "password": "test123",
            "org_id": "org_alpha",
            "roles": ["volunteer"],
            "person_id": "person_alice_volunteer"
        },
        {
            "name": "Alex Manager",
            "email": "alex.manager@alpha.com",
            "password": "test123",
            "org_id": "org_alpha",
            "roles": ["manager"],
            "person_id": "person_alex_manager"
        },
        {
            "name": "Amy Admin",
            "email": "amy.admin@alpha.com",
            "password": "test123",
            "org_id": "org_alpha",
            "roles": ["admin"],
            "person_id": "person_amy_admin"
        },
        # Organization Beta users
        {
            "name": "Bob Volunteer",
            "email": "bob.volunteer@beta.com",
            "password": "test123",
            "org_id": "org_beta",
            "roles": ["volunteer"],
            "person_id": "person_bob_volunteer"
        },
        {
            "name": "Ben Admin",
            "email": "ben.admin@beta.com",
            "password": "test123",
            "org_id": "org_beta",
            "roles": ["admin"],
            "person_id": "person_ben_admin"
        },
    ]

    for user in users:
        resp = requests.post(f"{API_BASE}/auth/signup", json=user)
        if resp.status_code in [200, 201]:
            print(f"✓ Created user: {user['name']} ({user['roles'][0]})")
        elif resp.status_code == 409:
            print(f"ℹ User exists: {user['name']}")

    return users


def get_auth_token(email: str, password: str) -> tuple[str, dict]:
    """Login and return JWT token and user data."""
    resp = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": email, "password": password}
    )
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    data = resp.json()
    # Cache person_id for later use
    _person_id_cache[email] = data["person_id"]
    return data["token"], data


def get_person_id(email: str) -> str:
    """Get person_id for an email (must login first)."""
    if email not in _person_id_cache:
        token, data = get_auth_token(email, "test123")
        return data["person_id"]
    return _person_id_cache[email]


def get_headers(token: str) -> dict:
    """Get authorization headers."""
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# VOLUNTEER USER TESTS (Read-only + Self-edit)
# ============================================================================

def test_volunteer_can_view_own_organization_people(test_users):
    """Volunteer can view people from their own organization."""
    token, _ = get_auth_token("alice.volunteer@alpha.com", "test123")
    headers = get_headers(token)

    resp = requests.get(f"{API_BASE}/people/?org_id=org_alpha", headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert "people" in data
    assert len(data["people"]) >= 1
    print("✓ Volunteer can view own organization people")


def test_volunteer_cannot_view_other_organization_people(test_users):
    """Volunteer cannot view people from other organizations."""
    token, _ = get_auth_token("alice.volunteer@alpha.com", "test123")
    headers = get_headers(token)

    # Try to access Beta organization data
    resp = requests.get(f"{API_BASE}/people/?org_id=org_beta", headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Volunteer blocked from viewing other org people")


def test_volunteer_can_edit_own_profile(test_users):
    """Volunteer can edit their own profile (name, timezone, language)."""
    token, _ = get_auth_token("alice.volunteer@alpha.com", "test123")
    headers = get_headers(token)

    update_data = {
        "name": "Alice Volunteer Updated",
        "timezone": "America/New_York",
        "language": "en"
    }

    resp = requests.put(
        f"{API_BASE}/people/{get_person_id('alice.volunteer@alpha.com')}",
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update
    updated = resp.json()
    assert updated["name"] == "Alice Volunteer Updated"
    print("✓ Volunteer can edit own profile")


def test_volunteer_cannot_edit_own_roles(test_users):
    """Volunteer cannot escalate their own roles."""
    token, _ = get_auth_token("alice.volunteer@alpha.com", "test123")
    headers = get_headers(token)

    # Try to make self admin
    update_data = {
        "roles": ["admin", "volunteer"]
    }

    resp = requests.put(
        f"{API_BASE}/people/{get_person_id('alice.volunteer@alpha.com')}",
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    assert "Only admins can modify user roles" in resp.text
    print("✓ Volunteer blocked from role escalation")


def test_volunteer_cannot_edit_other_users(test_users):
    """Volunteer cannot edit other users."""
    token, _ = get_auth_token("alice.volunteer@alpha.com", "test123")
    headers = get_headers(token)

    update_data = {"name": "Hacked Name"}

    resp = requests.put(
        f"{API_BASE}/people/{get_person_id('alex.manager@alpha.com')}",
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Volunteer blocked from editing other users")


def test_volunteer_cannot_create_events(test_users):
    """Volunteer cannot create events."""
    token, _ = get_auth_token("alice.volunteer@alpha.com", "test123")
    headers = get_headers(token)

    now = datetime.now()
    event_data = {
        "id": "event_volunteer_test",
        "org_id": "org_alpha",
        "type": "Test Event",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1, hours=2)).isoformat(),
    }

    resp = requests.post(f"{API_BASE}/events/", json=event_data, headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    assert "Admin access required" in resp.text
    print("✓ Volunteer blocked from creating events")


def test_volunteer_cannot_delete_events(test_users):
    """Volunteer cannot delete events."""
    # First create an event as admin
    admin_token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    admin_headers = get_headers(admin_token)

    now = datetime.now()
    event_data = {
        "id": "event_to_delete_volunteer",
        "org_id": "org_alpha",
        "type": "Test Event",
        "start_time": (now + timedelta(days=2)).isoformat(),
        "end_time": (now + timedelta(days=2, hours=1)).isoformat(),
    }
    resp = requests.post(f"{API_BASE}/events/", json=event_data, headers=admin_headers)
    if resp.status_code not in [200, 201, 409]:
        print(f"Warning: Event creation failed: {resp.text}")

    # Try to delete as volunteer
    volunteer_token, _ = get_auth_token("alice.volunteer@alpha.com", "test123")
    volunteer_headers = get_headers(volunteer_token)

    resp = requests.delete(
        f"{API_BASE}/events/event_to_delete_volunteer",
        headers=volunteer_headers
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Volunteer blocked from deleting events")


def test_volunteer_cannot_create_teams(test_users):
    """Volunteer cannot create teams."""
    token, _ = get_auth_token("alice.volunteer@alpha.com", "test123")
    headers = get_headers(token)

    team_data = {
        "id": "team_volunteer_test",
        "org_id": "org_alpha",
        "name": "Volunteer Team",
        "member_ids": []
    }

    resp = requests.post(f"{API_BASE}/teams/", json=team_data, headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Volunteer blocked from creating teams")


def test_volunteer_cannot_run_solver(test_users):
    """Volunteer cannot generate schedules (expensive AI operation)."""
    token, _ = get_auth_token("alice.volunteer@alpha.com", "test123")
    headers = get_headers(token)

    from datetime import date
    solve_data = {
        "org_id": "org_alpha",
        "from_date": date.today().isoformat(),
        "to_date": (date.today() + timedelta(days=30)).isoformat(),
    }

    resp = requests.post(f"{API_BASE}/solver/solve", json=solve_data, headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Volunteer blocked from running solver")


# ============================================================================
# ADMIN USER TESTS (Full control within organization)
# ============================================================================

def test_admin_can_create_events(test_users):
    """Admin can create events in their organization."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    now = datetime.now()
    event_data = {
        "id": f"event_admin_test_{int(now.timestamp())}",
        "org_id": "org_alpha",
        "type": "Admin Created Event",
        "start_time": (now + timedelta(days=5)).isoformat(),
        "end_time": (now + timedelta(days=5, hours=2)).isoformat(),
    }

    resp = requests.post(f"{API_BASE}/events/", json=event_data, headers=headers)
    assert resp.status_code in [200, 201], f"Expected 200/201, got {resp.status_code}: {resp.text}"
    print("✓ Admin can create events")


def test_admin_can_edit_events(test_users):
    """Admin can edit events in their organization."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    # Create event first
    now = datetime.now()
    event_id = f"event_admin_edit_{int(now.timestamp())}"
    event_data = {
        "id": event_id,
        "org_id": "org_alpha",
        "type": "Event to Edit",
        "start_time": (now + timedelta(days=6)).isoformat(),
        "end_time": (now + timedelta(days=6, hours=2)).isoformat(),
    }
    requests.post(f"{API_BASE}/events/", json=event_data, headers=headers)

    # Edit it
    update_data = {"type": "Edited Event"}
    resp = requests.put(f"{API_BASE}/events/{event_id}", json=update_data, headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    print("✓ Admin can edit events")


def test_admin_can_delete_events(test_users):
    """Admin can delete events in their organization."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    # Create event first
    now = datetime.now()
    event_id = f"event_admin_delete_{int(now.timestamp())}"
    event_data = {
        "id": event_id,
        "org_id": "org_alpha",
        "type": "Event to Delete",
        "start_time": (now + timedelta(days=7)).isoformat(),
        "end_time": (now + timedelta(days=7, hours=1)).isoformat(),
    }
    requests.post(f"{API_BASE}/events/", json=event_data, headers=headers)

    # Delete it
    resp = requests.delete(f"{API_BASE}/events/{event_id}", headers=headers)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"
    print("✓ Admin can delete events")


def test_admin_can_create_teams(test_users):
    """Admin can create teams in their organization."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    now = datetime.now()
    team_data = {
        "id": f"team_admin_{int(now.timestamp())}",
        "org_id": "org_alpha",
        "name": "Admin Team",
        "description": "Created by admin",
        "member_ids": []
    }

    resp = requests.post(f"{API_BASE}/teams/", json=team_data, headers=headers)
    assert resp.status_code in [200, 201], f"Expected 200/201, got {resp.status_code}: {resp.text}"
    print("✓ Admin can create teams")


def test_admin_can_edit_user_profiles(test_users):
    """Admin can edit any user in their organization."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    update_data = {
        "name": "Alice Volunteer (Admin Updated)",
        "timezone": "America/Los_Angeles"
    }

    resp = requests.put(
        f"{API_BASE}/people/{get_person_id('alice.volunteer@alpha.com')}",
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    print("✓ Admin can edit user profiles")


def test_admin_can_modify_user_roles(test_users):
    """Admin can modify user roles in their organization."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    # Promote volunteer to manager
    update_data = {
        "roles": ["volunteer", "manager"]
    }

    resp = requests.put(
        f"{API_BASE}/people/{get_person_id('alice.volunteer@alpha.com')}",
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify role change
    updated = resp.json()
    assert "manager" in updated["roles"]
    print("✓ Admin can modify user roles")


def test_admin_can_run_solver(test_users):
    """Admin can generate schedules."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    from datetime import date
    solve_data = {
        "org_id": "org_alpha",
        "from_date": date.today().isoformat(),
        "to_date": (date.today() + timedelta(days=30)).isoformat(),
    }

    resp = requests.post(f"{API_BASE}/solver/solve", json=solve_data, headers=headers)
    # May fail if no events, but should not be 403
    assert resp.status_code != 403, f"Admin should not get 403: {resp.text}"
    print("✓ Admin can run solver (not blocked by permissions)")


# ============================================================================
# ORGANIZATION ISOLATION TESTS
# ============================================================================

def test_admin_cannot_create_events_in_other_org(test_users):
    """Admin from org A cannot create events in org B."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    now = datetime.now()
    event_data = {
        "id": f"event_cross_org_{int(now.timestamp())}",
        "org_id": "org_beta",  # Different org!
        "type": "Cross Org Event",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1, hours=1)).isoformat(),
    }

    resp = requests.post(f"{API_BASE}/events/", json=event_data, headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    assert "not a member of this organization" in resp.text
    print("✓ Admin blocked from creating events in other org")


def test_admin_cannot_edit_users_in_other_org(test_users):
    """Admin from org A cannot edit users in org B."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    update_data = {"name": "Hacked by Alpha Admin"}

    resp = requests.put(
        f"{API_BASE}/people/{get_person_id('bob.volunteer@beta.com')}",  # Beta org user
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Admin blocked from editing users in other org")


def test_admin_cannot_view_other_org_people(test_users):
    """Admin from org A cannot view people from org B."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    resp = requests.get(f"{API_BASE}/people/?org_id=org_beta", headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Admin blocked from viewing other org people")


def test_admin_cannot_view_other_org_teams(test_users):
    """Admin from org A cannot view teams from org B."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    resp = requests.get(f"{API_BASE}/teams/?org_id=org_beta", headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Admin blocked from viewing other org teams")


def test_admin_cannot_run_solver_for_other_org(test_users):
    """Admin from org A cannot generate schedules for org B."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    from datetime import date
    solve_data = {
        "org_id": "org_beta",  # Different org!
        "from_date": date.today().isoformat(),
        "to_date": (date.today() + timedelta(days=30)).isoformat(),
    }

    resp = requests.post(f"{API_BASE}/solver/solve", json=solve_data, headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Admin blocked from running solver for other org")


# ============================================================================
# CROSS-ORG DATA LEAK TESTS
# ============================================================================

def test_no_cross_org_data_leak_in_people_list(test_users):
    """Ensure people list only returns users from requester's org."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    # Get people without org_id filter (should default to user's org)
    resp = requests.get(f"{API_BASE}/people/", headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    people = data["people"]

    # All returned people should be from org_alpha
    for person in people:
        assert person["org_id"] == "org_alpha", f"Data leak: {person['name']} from {person['org_id']}"

    print("✓ No cross-org data leak in people list")


def test_no_cross_org_data_leak_in_teams_list(test_users):
    """Ensure teams list only returns teams from requester's org."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)

    # Get teams without org_id filter (should default to user's org)
    resp = requests.get(f"{API_BASE}/teams/", headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    teams = data["teams"]

    # All returned teams should be from org_alpha
    for team in teams:
        assert team["org_id"] == "org_alpha", f"Data leak: {team['name']} from {team['org_id']}"

    print("✓ No cross-org data leak in teams list")


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_unauthenticated_request_fails():
    """Unauthenticated requests should fail with 401 or 403."""
    # Try to list people without token
    resp = requests.get(f"{API_BASE}/people/")
    assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}: {resp.text}"
    print("✓ Unauthenticated request blocked")


def test_invalid_token_fails():
    """Invalid token should fail with 401."""
    headers = {"Authorization": "Bearer invalid_token_12345"}
    resp = requests.get(f"{API_BASE}/people/", headers=headers)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
    print("✓ Invalid token rejected")


# ============================================================================
# COMPREHENSIVE WORKFLOW TESTS
# ============================================================================

def test_complete_admin_workflow(test_users):
    """Test complete admin workflow: create event, assign people, manage team."""
    token, _ = get_auth_token("amy.admin@alpha.com", "test123")
    headers = get_headers(token)
    now = datetime.now()

    # 1. Create event
    event_id = f"workflow_event_{int(now.timestamp())}"
    event_data = {
        "id": event_id,
        "org_id": "org_alpha",
        "type": "Workflow Test Event",
        "start_time": (now + timedelta(days=10)).isoformat(),
        "end_time": (now + timedelta(days=10, hours=2)).isoformat(),
    }
    resp = requests.post(f"{API_BASE}/events/", json=event_data, headers=headers)
    assert resp.status_code in [200, 201], f"Event creation failed: {resp.text}"

    # 2. Create team
    team_id = f"workflow_team_{int(now.timestamp())}"
    team_data = {
        "id": team_id,
        "org_id": "org_alpha",
        "name": "Workflow Team",
        "member_ids": [get_person_id('alice.volunteer@alpha.com')]
    }
    resp = requests.post(f"{API_BASE}/teams/", json=team_data, headers=headers)
    assert resp.status_code in [200, 201], f"Team creation failed: {resp.text}"

    # 3. Update event
    resp = requests.put(
        f"{API_BASE}/events/{event_id}",
        json={"type": "Updated Workflow Event"},
        headers=headers
    )
    assert resp.status_code == 200, f"Event update failed: {resp.text}"

    # 4. Delete event
    resp = requests.delete(f"{API_BASE}/events/{event_id}", headers=headers)
    assert resp.status_code == 204, f"Event deletion failed: {resp.text}"

    print("✓ Complete admin workflow successful")


def test_complete_volunteer_workflow(test_users):
    """Test complete volunteer workflow: view schedule, edit profile, view team."""
    token, _ = get_auth_token("alice.volunteer@alpha.com", "test123")
    headers = get_headers(token)

    # 1. View own profile
    resp = requests.get(f"{API_BASE}/people/me", headers=headers)
    assert resp.status_code == 200, f"View profile failed: {resp.text}"

    # 2. Edit own profile
    resp = requests.put(
        f"{API_BASE}/people/me",
        json={"name": "Alice V (Updated)", "timezone": "UTC"},
        headers=headers
    )
    assert resp.status_code == 200, f"Edit profile failed: {resp.text}"

    # 3. View people in organization
    resp = requests.get(f"{API_BASE}/people/?org_id=org_alpha", headers=headers)
    assert resp.status_code == 200, f"View people failed: {resp.text}"

    # 4. View teams in organization
    resp = requests.get(f"{API_BASE}/teams/?org_id=org_alpha", headers=headers)
    assert resp.status_code == 200, f"View teams failed: {resp.text}"

    # 5. Verify cannot create event (should fail)
    now = datetime.now()
    event_data = {
        "id": f"volunteer_attempt_{int(now.timestamp())}",
        "org_id": "org_alpha",
        "type": "Unauthorized Event",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1, hours=1)).isoformat(),
    }
    resp = requests.post(f"{API_BASE}/events/", json=event_data, headers=headers)
    assert resp.status_code == 403, f"Volunteer should not create event: {resp.text}"

    print("✓ Complete volunteer workflow successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
