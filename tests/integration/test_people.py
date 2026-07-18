#!/usr/bin/env python3
"""Integration tests: people router (Sprint 4 PR 4.6b).

Tests the /api/v1/people endpoints over real HTTP against the
session-scoped uvicorn api_server:
- GET    /people/me                      - Current user profile
- PUT    /people/me                      - Update own profile
- POST   /people/                        - Create person (admin)
- POST   /people/bulk                    - Bulk import (admin, JSON-array)
- GET    /people/                        - List (envelope, q=, role filter, org)
- GET    /people/{person_id}             - Get one
- PUT    /people/{person_id}             - Update (self or admin, no role escalation)
- DELETE /people/{person_id}             - Delete (admin)
"""

import time

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


@pytest.fixture
def people_org(api_server, api_base):
    """Create an org + admin + one volunteer; return authed clients + ids."""
    marker = _unique("people_org")
    org_id = marker
    admin_email = f"admin_{marker}@test.com"
    vol_email = f"vol_{marker}@test.com"

    bootstrap = httpx.Client()

    org_resp = bootstrap.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"People Setup {marker}", "region": "US", "config": {}},
    )
    assert org_resp.status_code == 201, org_resp.text

    admin_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "People Admin",
            "email": admin_email,
            "password": "AdminPass123!",
        },
    )
    assert admin_resp.status_code == 201, admin_resp.text
    admin_data = admin_resp.json()
    assert "admin" in admin_data["roles"]

    vol_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "People Volunteer",
            "email": vol_email,
            "password": "VolPass123!",
            "roles": ["volunteer"],
        },
    )
    assert vol_resp.status_code == 201, vol_resp.text
    vol_data = vol_resp.json()
    assert "admin" not in vol_data["roles"]

    bootstrap.close()

    admin_client = httpx.Client()
    admin_client.headers["Authorization"] = f"Bearer {admin_data['token']}"

    vol_client = httpx.Client()
    vol_client.headers["Authorization"] = f"Bearer {vol_data['token']}"

    yield {
        "marker": marker,
        "org_id": org_id,
        "admin_id": admin_data["person_id"],
        "admin_email": admin_email,
        "admin_client": admin_client,
        "vol_id": vol_data["person_id"],
        "vol_email": vol_email,
        "vol_client": vol_client,
        "api_base": api_base,
    }

    admin_client.close()
    vol_client.close()


class TestMeEndpoints:
    """GET + PUT /people/me — self-profile flows."""

    def test_me_returns_current_user(self, people_org):
        data = people_org
        resp = data["admin_client"].get(f"{data['api_base']}/people/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == data["admin_id"]
        assert body["email"] == data["admin_email"]

    def test_me_unauthenticated_rejected(self, api_server, api_base):
        resp = httpx.Client().get(f"{api_base}/people/me")
        assert resp.status_code == 403

    def test_update_me_changes_name_and_timezone(self, people_org):
        data = people_org
        resp = data["vol_client"].put(
            f"{data['api_base']}/people/me",
            json={"name": "Renamed Volunteer", "timezone": "America/Los_Angeles"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["name"] == "Renamed Volunteer"
        assert body["timezone"] == "America/Los_Angeles"


class TestCreatePerson:
    """POST /people/ — admin-only creation."""

    def test_create_success(self, people_org):
        data = people_org
        new_id = _unique("newp")
        resp = data["admin_client"].post(
            f"{data['api_base']}/people/",
            json={
                "id": new_id,
                "org_id": data["org_id"],
                "name": "Fresh Person",
                "email": f"{new_id}@test.com",
                "roles": ["volunteer"],
            },
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["id"] == new_id
        assert resp.json()["org_id"] == data["org_id"]

    def test_create_requires_admin(self, people_org):
        data = people_org
        new_id = _unique("forbiddenp")
        resp = data["vol_client"].post(
            f"{data['api_base']}/people/",
            json={
                "id": new_id,
                "org_id": data["org_id"],
                "name": "Not Allowed",
                "email": f"{new_id}@test.com",
            },
        )
        assert resp.status_code == 403

    def test_create_duplicate_id_conflict(self, people_org):
        data = people_org
        resp = data["admin_client"].post(
            f"{data['api_base']}/people/",
            json={
                "id": data["vol_id"],
                "org_id": data["org_id"],
                "name": "Duplicate",
                "email": f"dup_{int(time.time())}@test.com",
            },
        )
        assert resp.status_code == 409


class TestBulkImport:
    """POST /people/bulk — admin-only JSON-array bulk import."""

    def test_bulk_import_success(self, people_org):
        data = people_org
        marker = _unique("bulkp")
        items = [
            {
                "id": f"{marker}_{i}",
                "org_id": data["org_id"],
                "name": f"Bulk Person {i}",
                "email": f"{marker}_{i}@test.com",
            }
            for i in range(3)
        ]

        resp = data["admin_client"].post(
            f"{data['api_base']}/people/bulk",
            params={"org_id": data["org_id"]},
            json={"items": items},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["created"] == 3
        assert body["skipped"] == 0
        assert body["errors"] == []

    def test_bulk_import_missing_items_400(self, people_org):
        data = people_org
        resp = data["admin_client"].post(
            f"{data['api_base']}/people/bulk",
            params={"org_id": data["org_id"]},
            json={},
        )
        assert resp.status_code == 400

    def test_bulk_import_requires_admin(self, people_org):
        data = people_org
        resp = data["vol_client"].post(
            f"{data['api_base']}/people/bulk",
            params={"org_id": data["org_id"]},
            json={"items": []},
        )
        assert resp.status_code == 403


class TestListAndGetPeople:
    """GET /people/ and GET /people/{id}."""

    def test_list_envelope(self, people_org):
        data = people_org
        resp = data["admin_client"].get(f"{data['api_base']}/people/")
        assert resp.status_code == 200
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        ids = {p["id"] for p in body["items"]}
        assert data["admin_id"] in ids
        assert data["vol_id"] in ids

    def test_list_q_filter_by_email(self, people_org):
        data = people_org
        # Search for a term unique to admin_email; volunteer must not match.
        term = data["admin_email"].split("@")[0]
        resp = data["admin_client"].get(
            f"{data['api_base']}/people/",
            params={"org_id": data["org_id"], "q": term},
        )
        assert resp.status_code == 200
        returned = {p["id"] for p in resp.json()["items"]}
        assert data["admin_id"] in returned
        assert data["vol_id"] not in returned

    def test_list_role_filter(self, people_org):
        data = people_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/people/",
            params={"org_id": data["org_id"], "role": "volunteer"},
        )
        assert resp.status_code == 200
        assert all("volunteer" in (p.get("roles") or []) for p in resp.json()["items"])

    def test_get_existing(self, people_org):
        data = people_org
        resp = data["admin_client"].get(f"{data['api_base']}/people/{data['vol_id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == data["vol_id"]

    def test_get_missing_returns_404(self, people_org):
        data = people_org
        resp = data["admin_client"].get(f"{data['api_base']}/people/ghost_{int(time.time())}")
        assert resp.status_code == 404


class TestUpdatePerson:
    """PUT /people/{id} — self or admin, no volunteer role-escalation."""

    def test_admin_can_update_other_in_org(self, people_org):
        data = people_org
        resp = data["admin_client"].put(
            f"{data['api_base']}/people/{data['vol_id']}",
            json={"name": "Volunteer-Renamed-By-Admin"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["name"] == "Volunteer-Renamed-By-Admin"

    def test_volunteer_cannot_edit_others(self, people_org):
        data = people_org
        resp = data["vol_client"].put(
            f"{data['api_base']}/people/{data['admin_id']}",
            json={"name": "Hostile Takeover"},
        )
        assert resp.status_code == 403

    def test_volunteer_cannot_escalate_roles(self, people_org):
        data = people_org
        # Self-edit but attempting to grant admin
        resp = data["vol_client"].put(
            f"{data['api_base']}/people/{data['vol_id']}",
            json={"roles": ["admin", "volunteer"]},
        )
        assert resp.status_code == 403


class TestDeletePerson:
    """DELETE /people/{id} — admin only."""

    def test_delete_removes_person(self, people_org):
        data = people_org
        # Create a fresh person to delete so we don't disturb fixture state.
        pid = _unique("delp")
        create_resp = data["admin_client"].post(
            f"{data['api_base']}/people/",
            json={
                "id": pid,
                "org_id": data["org_id"],
                "name": "Delete Me",
                "email": f"{pid}@test.com",
            },
        )
        assert create_resp.status_code == 201

        resp = data["admin_client"].delete(f"{data['api_base']}/people/{pid}")
        assert resp.status_code == 204

        follow = data["admin_client"].get(f"{data['api_base']}/people/{pid}")
        assert follow.status_code == 404

    def test_delete_requires_admin(self, people_org):
        data = people_org
        resp = data["vol_client"].delete(f"{data['api_base']}/people/{data['admin_id']}")
        assert resp.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
