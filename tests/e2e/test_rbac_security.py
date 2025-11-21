"""E2E tests for RBAC security implementation.

Tests comprehensive role-based access control including:
- Volunteer (read-only, self-edit)
- Manager (extended read, limited write)
- Admin (full control within organization)
- Organization isolation
- Role escalation prevention
"""

import os
import pytest
import requests
import time
from datetime import datetime, timedelta
from passlib.context import CryptContext

from tests.e2e.helpers import AppConfig

pytestmark = pytest.mark.usefixtures("api_server")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cache for person_ids (email -> person_id)
_person_id_cache = {}


@pytest.fixture(scope="module")
def test_organizations(app_config: AppConfig):
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
        resp = requests.post(f"{app_config.app_url}/api/organizations/", json=org)
        if resp.status_code in [200, 201, 409]:
            print(f"✓ Organization ready: {org['name']}")

    return orgs


@pytest.fixture(scope="module")
def test_users(test_organizations, app_config: AppConfig):
    """Create test users with different roles across organizations.

    Strategy:
    1. Create ALL users via signup (so they have passwords)
    2. First user in each org becomes admin automatically
    3. For non-admin users, admin updates their roles after signup
    """

    # All users to create
    timestamp = int(time.time() * 1000)

    def unique_email(label: str, domain: str) -> str:
        safe_label = label.replace(" ", ".").lower()
        return f"{safe_label}.{timestamp}@{domain}"

    _person_id_cache.clear()

    all_user_data = [
        # Organization Alpha users
        {
            "name": "Amy Admin",
            "email": unique_email("amy.admin", "alpha.com"),
            "password": "test123",
            "org_id": "org_alpha",
            "desired_roles": ["admin"],  # First user, becomes admin automatically
            "is_first": True,
        },
        {
            "name": "Alice Volunteer",
            "email": unique_email("alice.volunteer", "alpha.com"),
            "password": "test123",
            "org_id": "org_alpha",
            "desired_roles": ["volunteer"],
            "is_first": False,
        },
        {
            "name": "Alex Manager",
            "email": unique_email("alex.manager", "alpha.com"),
            "password": "test123",
            "org_id": "org_alpha",
            "desired_roles": ["manager"],
            "is_first": False,
        },
        # Organization Beta users
        {
            "name": "Ben Admin",
            "email": unique_email("ben.admin", "beta.com"),
            "password": "test123",
            "org_id": "org_beta",
            "desired_roles": ["admin"],  # First user, becomes admin automatically
            "is_first": True,
        },
        {
            "name": "Bob Volunteer",
            "email": unique_email("bob.volunteer", "beta.com"),
            "password": "test123",
            "org_id": "org_beta",
            "desired_roles": ["volunteer"],
            "is_first": False,
        },
    ]

    admin_tokens = {}

    # Step 1: Create all users via signup
    for user in all_user_data:
        signup_data = {
            "name": user["name"],
            "email": user["email"],
            "password": user["password"],
            "org_id": user["org_id"],
        }
        resp = requests.post(f"{app_config.app_url}/api/auth/signup", json=signup_data)
        if resp.status_code in [200, 201]:
            data = resp.json()
            _person_id_cache[user["email"]] = data["person_id"]
            if user["is_first"]:
                admin_tokens[user["org_id"]] = data["token"]
                print(f"✓ Created admin: {user['name']}")
            else:
                print(f"✓ Created user: {user['name']} (will update roles)")
        elif resp.status_code == 409:
            # User exists
            if user["is_first"]:
                try:
                    token, data = get_auth_token(app_config, user["email"], user["password"])
                    admin_tokens[user["org_id"]] = token
                    print(f"ℹ User exists, logged in: {user['name']}")
                except AssertionError as e:
                    print(f"⚠ User exists but login failed: {user['name']} - {e}")
            else:
                print(f"ℹ User exists: {user['name']}")
        else:
            print(f"⚠ Failed to create {user['name']}: {resp.status_code} - {resp.text}")

    # Step 2: Update roles for non-admin users
    for user in all_user_data:
        if not user["is_first"]:  # Skip admins (already have correct roles)
            org_id = user["org_id"]

            # Check if we have admin token for this org
            if org_id not in admin_tokens:
                print(f"⚠ Skipping {user['name']} - no admin token for {org_id}")
                continue

            headers = {"Authorization": f"Bearer {admin_tokens[org_id]}"}

            person_id = _person_id_cache.get(user["email"])
            if person_id:
                update_data = {"roles": user["desired_roles"]}
                resp = requests.put(
                    f"{app_config.app_url}/api/people/{person_id}",
                    json=update_data,
                    headers=headers
                )
                if resp.status_code == 200:
                    print(f"✓ Updated roles for {user['name']}: {user['desired_roles']}")
                else:
                    print(f"⚠ Failed to update roles for {user['name']}: {resp.status_code}")

    # Return all users for reference
    user_lookup = {
        "alpha_volunteer": next(u for u in all_user_data if u["name"] == "Alice Volunteer"),
        "alpha_manager": next(u for u in all_user_data if u["name"] == "Alex Manager"),
        "alpha_admin": next(u for u in all_user_data if u["name"] == "Amy Admin"),
        "beta_volunteer": next(u for u in all_user_data if u["name"] == "Bob Volunteer"),
        "beta_admin": next(u for u in all_user_data if u["name"] == "Ben Admin"),
    }
    return user_lookup


def get_auth_token(app_config: AppConfig, email: str, password: str) -> tuple[str, dict]:
    """Login and return JWT token and user data."""
    resp = requests.post(
        f"{app_config.app_url}/api/auth/login",
        json={"email": email, "password": password}
    )
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    data = resp.json()
    # Cache person_id for later use
    _person_id_cache[email] = data["person_id"]
    return data["token"], data


def get_person_id(app_config: AppConfig, email: str, password: str) -> str:
    """Get person_id for an email (must login first)."""
    if email not in _person_id_cache:
        token, data = get_auth_token(app_config, email, password)
        return data["person_id"]
    return _person_id_cache[email]


def get_headers(token: str) -> dict:
    """Get authorization headers."""
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# VOLUNTEER USER TESTS (Read-only + Self-edit)
# ============================================================================

def test_volunteer_can_view_own_organization_people(test_users, app_config: AppConfig):
    """Volunteer can view people from their own organization."""
    volunteer = test_users["alpha_volunteer"]
    token, _ = get_auth_token(app_config, volunteer["email"], volunteer["password"])
    headers = get_headers(token)

    resp = requests.get(
        f"{app_config.app_url}/api/people/?org_id={volunteer['org_id']}",
        headers=headers,
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert "people" in data
    assert len(data["people"]) >= 1
    print("✓ Volunteer can view own organization people")


def test_volunteer_cannot_view_other_organization_people(test_users, app_config: AppConfig):
    """Volunteer cannot view people from other organizations."""
    volunteer = test_users["alpha_volunteer"]
    token, _ = get_auth_token(app_config, volunteer["email"], volunteer["password"])
    headers = get_headers(token)

    # Try to access Beta organization data
    resp = requests.get(f"{app_config.app_url}/api/people/?org_id=org_beta", headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Volunteer blocked from viewing other org people")


def test_volunteer_can_edit_own_profile(test_users, app_config: AppConfig):
    """Volunteer can edit their own profile (name, timezone, language)."""
    volunteer = test_users["alpha_volunteer"]
    token, _ = get_auth_token(app_config, volunteer["email"], volunteer["password"])
    headers = get_headers(token)

    update_data = {
        "name": "Alice Volunteer Updated",
        "timezone": "America/New_York",
        "language": "en"
    }

    resp = requests.put(
        f"{app_config.app_url}/api/people/{get_person_id(app_config, volunteer['email'], volunteer['password'])}",
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify update
    updated = resp.json()
    assert updated["name"] == "Alice Volunteer Updated"
    print("✓ Volunteer can edit own profile")


def test_volunteer_cannot_edit_own_roles(test_users, app_config: AppConfig):
    """Volunteer cannot escalate their own roles."""
    volunteer = test_users["alpha_volunteer"]
    token, _ = get_auth_token(app_config, volunteer["email"], volunteer["password"])
    headers = get_headers(token)

    # Try to make self admin
    update_data = {
        "roles": ["admin", "volunteer"]
    }

    resp = requests.put(
        f"{app_config.app_url}/api/people/{get_person_id(app_config, volunteer['email'], volunteer['password'])}",
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    assert "Only admins can modify user roles" in resp.text
    print("✓ Volunteer blocked from role escalation")


def test_volunteer_cannot_edit_other_users(test_users, app_config: AppConfig):
    """Volunteer cannot edit other users."""
    volunteer = test_users["alpha_volunteer"]
    manager = test_users["alpha_manager"]
    token, _ = get_auth_token(app_config, volunteer["email"], volunteer["password"])
    headers = get_headers(token)

    update_data = {"name": "Hacked Name"}

    resp = requests.put(
        f"{app_config.app_url}/api/people/{get_person_id(app_config, manager['email'], manager['password'])}",
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Volunteer blocked from editing other users")


def test_volunteer_cannot_create_events(test_users, app_config: AppConfig):
    """Volunteer cannot create events."""
    volunteer = test_users["alpha_volunteer"]
    token, _ = get_auth_token(app_config, volunteer["email"], volunteer["password"])
    headers = get_headers(token)

    now = datetime.now()
    event_data = {
        "id": "event_volunteer_test",
        "org_id": volunteer["org_id"],
        "type": "Test Event",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1, hours=2)).isoformat(),
    }

    resp = requests.post(f"{app_config.app_url}/api/events/", json=event_data, headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    assert "Admin access required" in resp.text
    print("✓ Volunteer blocked from creating events")


def test_volunteer_cannot_delete_events(test_users, app_config: AppConfig):
    """Volunteer cannot delete events."""
    # First create an event as admin
    admin = test_users["alpha_admin"]
    admin_token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    admin_headers = get_headers(admin_token)

    now = datetime.now()
    event_data = {
        "id": "event_to_delete_volunteer",
        "org_id": admin["org_id"],
        "type": "Test Event",
        "start_time": (now + timedelta(days=2)).isoformat(),
        "end_time": (now + timedelta(days=2, hours=1)).isoformat(),
    }
    resp = requests.post(f"{app_config.app_url}/api/events/", json=event_data, headers=admin_headers)
    if resp.status_code not in [200, 201, 409]:
        print(f"Warning: Event creation failed: {resp.text}")

    # Try to delete as volunteer
    volunteer = test_users["alpha_volunteer"]
    volunteer_token, _ = get_auth_token(app_config, volunteer["email"], volunteer["password"])
    volunteer_headers = get_headers(volunteer_token)

    resp = requests.delete(
        f"{app_config.app_url}/api/events/event_to_delete_volunteer",
        headers=volunteer_headers
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Volunteer blocked from deleting events")


def test_volunteer_cannot_create_teams(test_users, app_config: AppConfig):
    """Volunteer cannot create teams."""
    volunteer = test_users["alpha_volunteer"]
    token, _ = get_auth_token(app_config, volunteer["email"], volunteer["password"])
    headers = get_headers(token)

    team_data = {
        "id": "team_volunteer_test",
        "org_id": volunteer["org_id"],
        "name": "Volunteer Team",
        "member_ids": []
    }

    resp = requests.post(f"{app_config.app_url}/api/teams/", json=team_data, headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Volunteer blocked from creating teams")


def test_volunteer_cannot_run_solver(test_users, app_config: AppConfig):
    """Volunteer cannot generate schedules (expensive AI operation)."""
    volunteer = test_users["alpha_volunteer"]
    token, _ = get_auth_token(app_config, volunteer["email"], volunteer["password"])
    headers = get_headers(token)

    from datetime import date
    solve_data = {
        "org_id": "org_alpha",
        "from_date": date.today().isoformat(),
        "to_date": (date.today() + timedelta(days=30)).isoformat(),
    }

    resp = requests.post(f"{app_config.app_url}/api/solver/solve", json=solve_data, headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Volunteer blocked from running solver")


# ============================================================================
# ADMIN USER TESTS (Full control within organization)
# ============================================================================

def test_admin_can_create_events(test_users, app_config: AppConfig):
    """Admin can create events in their organization."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    now = datetime.now()
    event_data = {
        "id": f"event_admin_test_{int(now.timestamp())}",
        "org_id": "org_alpha",
        "type": "Admin Created Event",
        "start_time": (now + timedelta(days=5)).isoformat(),
        "end_time": (now + timedelta(days=5, hours=2)).isoformat(),
    }

    resp = requests.post(f"{app_config.app_url}/api/events/", json=event_data, headers=headers)
    assert resp.status_code in [200, 201], f"Expected 200/201, got {resp.status_code}: {resp.text}"
    print("✓ Admin can create events")


def test_admin_can_edit_events(test_users, app_config: AppConfig):
    """Admin can edit events in their organization."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
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
    requests.post(f"{app_config.app_url}/api/events/", json=event_data, headers=headers)

    # Edit it
    update_data = {"type": "Edited Event"}
    resp = requests.put(f"{app_config.app_url}/api/events/{event_id}", json=update_data, headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    print("✓ Admin can edit events")


def test_admin_can_delete_events(test_users, app_config: AppConfig):
    """Admin can delete events in their organization."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
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
    requests.post(f"{app_config.app_url}/api/events/", json=event_data, headers=headers)

    # Delete it
    resp = requests.delete(f"{app_config.app_url}/api/events/{event_id}", headers=headers)
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}: {resp.text}"
    print("✓ Admin can delete events")


def test_admin_can_create_teams(test_users, app_config: AppConfig):
    """Admin can create teams in their organization."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    now = datetime.now()
    team_data = {
        "id": f"team_admin_{int(now.timestamp())}",
        "org_id": "org_alpha",
        "name": "Admin Team",
        "description": "Created by admin",
        "member_ids": []
    }

    resp = requests.post(f"{app_config.app_url}/api/teams/", json=team_data, headers=headers)
    assert resp.status_code in [200, 201], f"Expected 200/201, got {resp.status_code}: {resp.text}"
    print("✓ Admin can create teams")


def test_admin_can_edit_user_profiles(test_users, app_config: AppConfig):
    """Admin can edit any user in their organization."""
    admin = test_users["alpha_admin"]
    volunteer = test_users["alpha_volunteer"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    update_data = {
        "name": "Alice Volunteer (Admin Updated)",
        "timezone": "America/Los_Angeles"
    }

    resp = requests.put(
        f"{app_config.app_url}/api/people/{get_person_id(app_config, volunteer['email'], volunteer['password'])}",
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    print("✓ Admin can edit user profiles")


def test_admin_can_modify_user_roles(test_users, app_config: AppConfig):
    """Admin can modify user roles in their organization."""
    admin = test_users["alpha_admin"]
    volunteer = test_users["alpha_volunteer"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    # Promote volunteer to manager
    update_data = {
        "roles": ["volunteer", "manager"]
    }

    resp = requests.put(
        f"{app_config.app_url}/api/people/{get_person_id(app_config, volunteer['email'], volunteer['password'])}",
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    # Verify role change
    updated = resp.json()
    assert "manager" in updated["roles"]
    print("✓ Admin can modify user roles")


def test_admin_can_run_solver(test_users, app_config: AppConfig):
    """Admin can generate schedules."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    from datetime import date
    solve_data = {
        "org_id": "org_alpha",
        "from_date": date.today().isoformat(),
        "to_date": (date.today() + timedelta(days=30)).isoformat(),
    }

    resp = requests.post(f"{app_config.app_url}/api/solver/solve", json=solve_data, headers=headers)
    # May fail if no events, but should not be 403
    assert resp.status_code != 403, f"Admin should not get 403: {resp.text}"
    print("✓ Admin can run solver (not blocked by permissions)")


# ============================================================================
# ORGANIZATION ISOLATION TESTS
# ============================================================================

def test_admin_cannot_create_events_in_other_org(test_users, app_config: AppConfig):
    """Admin from org A cannot create events in org B."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    now = datetime.now()
    event_data = {
        "id": f"event_cross_org_{int(now.timestamp())}",
        "org_id": "org_beta",  # Different org!
        "type": "Cross Org Event",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1, hours=1)).isoformat(),
    }

    resp = requests.post(f"{app_config.app_url}/api/events/", json=event_data, headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    assert "not a member of this organization" in resp.text
    print("✓ Admin blocked from creating events in other org")


def test_admin_cannot_edit_users_in_other_org(test_users, app_config: AppConfig):
    """Admin from org A cannot edit users in org B."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    update_data = {"name": "Hacked by Alpha Admin"}

    beta_volunteer = test_users["beta_volunteer"]
    resp = requests.put(
        f"{app_config.app_url}/api/people/{get_person_id(app_config, beta_volunteer['email'], beta_volunteer['password'])}",  # Beta org user
        json=update_data,
        headers=headers
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Admin blocked from editing users in other org")


def test_admin_cannot_view_other_org_people(test_users, app_config: AppConfig):
    """Admin from org A cannot view people from org B."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    resp = requests.get(f"{app_config.app_url}/api/people/?org_id=org_beta", headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Admin blocked from viewing other org people")


def test_admin_cannot_view_other_org_teams(test_users, app_config: AppConfig):
    """Admin from org A cannot view teams from org B."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    resp = requests.get(f"{app_config.app_url}/api/teams/?org_id=org_beta", headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Admin blocked from viewing other org teams")


def test_admin_cannot_run_solver_for_other_org(test_users, app_config: AppConfig):
    """Admin from org A cannot generate schedules for org B."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    from datetime import date
    solve_data = {
        "org_id": "org_beta",  # Different org!
        "from_date": date.today().isoformat(),
        "to_date": (date.today() + timedelta(days=30)).isoformat(),
    }

    resp = requests.post(f"{app_config.app_url}/api/solver/solve", json=solve_data, headers=headers)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
    print("✓ Admin blocked from running solver for other org")


# ============================================================================
# CROSS-ORG DATA LEAK TESTS
# ============================================================================

def test_no_cross_org_data_leak_in_people_list(test_users, app_config: AppConfig):
    """Ensure people list only returns users from requester's org."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    # Get people without org_id filter (should default to user's org)
    resp = requests.get(f"{app_config.app_url}/api/people/", headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    people = data["people"]

    # All returned people should be from org_alpha
    for person in people:
        assert person["org_id"] == "org_alpha", f"Data leak: {person['name']} from {person['org_id']}"

    print("✓ No cross-org data leak in people list")


def test_no_cross_org_data_leak_in_teams_list(test_users, app_config: AppConfig):
    """Ensure teams list only returns teams from requester's org."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
    headers = get_headers(token)

    # Get teams without org_id filter (should default to user's org)
    resp = requests.get(f"{app_config.app_url}/api/teams/", headers=headers)
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

def test_unauthenticated_request_fails(app_config: AppConfig):
    """Unauthenticated requests should fail with 401 or 403."""
    # Try to list people without token
    resp = requests.get(f"{app_config.app_url}/api/people/")
    assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}: {resp.text}"
    print("✓ Unauthenticated request blocked")


def test_invalid_token_fails(app_config: AppConfig):
    """Invalid token should fail with 401."""
    headers = {"Authorization": "Bearer invalid_token_12345"}
    resp = requests.get(f"{app_config.app_url}/api/people/", headers=headers)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
    print("✓ Invalid token rejected")


# ============================================================================
# COMPREHENSIVE WORKFLOW TESTS
# ============================================================================

def test_complete_admin_workflow(test_users, app_config: AppConfig):
    """Test complete admin workflow: create event, assign people, manage team."""
    admin = test_users["alpha_admin"]
    token, _ = get_auth_token(app_config, admin["email"], admin["password"])
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
    resp = requests.post(f"{app_config.app_url}/api/events/", json=event_data, headers=headers)
    assert resp.status_code in [200, 201], f"Event creation failed: {resp.text}"

    # 2. Create team
    team_id = f"workflow_team_{int(now.timestamp())}"
    volunteer = test_users["alpha_volunteer"]
    team_data = {
        "id": team_id,
        "org_id": "org_alpha",
        "name": "Workflow Team",
        "member_ids": [get_person_id(app_config, volunteer['email'], volunteer['password'])]
    }
    resp = requests.post(f"{app_config.app_url}/api/teams/", json=team_data, headers=headers)
    assert resp.status_code in [200, 201], f"Team creation failed: {resp.text}"

    # 3. Update event
    resp = requests.put(
        f"{app_config.app_url}/api/events/{event_id}",
        json={"type": "Updated Workflow Event"},
        headers=headers
    )
    assert resp.status_code == 200, f"Event update failed: {resp.text}"

    # 4. Delete event
    resp = requests.delete(f"{app_config.app_url}/api/events/{event_id}", headers=headers)
    assert resp.status_code == 204, f"Event deletion failed: {resp.text}"

    print("✓ Complete admin workflow successful")


def test_complete_volunteer_workflow(test_users, app_config: AppConfig):
    """Test complete volunteer workflow: view schedule, edit profile, view team."""
    volunteer = test_users["alpha_volunteer"]
    token, _ = get_auth_token(app_config, volunteer["email"], volunteer["password"])
    headers = get_headers(token)

    # 1. View own profile
    resp = requests.get(f"{app_config.app_url}/api/people/me", headers=headers)
    assert resp.status_code == 200, f"View profile failed: {resp.text}"

    # 2. Edit own profile
    resp = requests.put(
        f"{app_config.app_url}/api/people/me",
        json={"name": "Alice V (Updated)", "timezone": "UTC"},
        headers=headers
    )
    assert resp.status_code == 200, f"Edit profile failed: {resp.text}"

    # 3. View people in organization
    resp = requests.get(f"{app_config.app_url}/api/people/?org_id=org_alpha", headers=headers)
    assert resp.status_code == 200, f"View people failed: {resp.text}"

    # 4. View teams in organization
    resp = requests.get(f"{app_config.app_url}/api/teams/?org_id=org_alpha", headers=headers)
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
    resp = requests.post(f"{app_config.app_url}/api/events/", json=event_data, headers=headers)
    assert resp.status_code == 403, f"Volunteer should not create event: {resp.text}"

    print("✓ Complete volunteer workflow successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
