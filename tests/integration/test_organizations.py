#!/usr/bin/env python3
"""Integration tests: organizations router (Sprint 4 PR 4.6b).

Tests the /api/v1/organizations endpoints over real HTTP against the
session-scoped uvicorn api_server:
- POST   /organizations/                 - Create
- GET    /organizations/                 - List (search, include_cancelled)
- GET    /organizations/{org_id}         - Get one
- PUT    /organizations/{org_id}         - Update
- DELETE /organizations/{org_id}         - Hard delete
- POST   /organizations/{org_id}/cancel  - Soft-cancel (admin)
- POST   /organizations/{org_id}/restore - Restore (admin)
"""

import time

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


@pytest.fixture
def setup_admin(api_server, api_base):
    """Create an org + admin user; return a JWT-authed httpx.Client."""
    client = httpx.Client()

    org_id = _unique("org_admin_setup")
    # Bake org_id into name so we can filter by q= even when other tests
    # create many orgs concurrently.
    org_response = client.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"Admin Setup Org {org_id}", "region": "US", "config": {}},
    )
    assert org_response.status_code == 201, org_response.text

    admin_email = f"admin_{org_id}@test.com"
    signup_response = client.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Admin User",
            "email": admin_email,
            "password": "AdminPass123!",
        },
    )
    assert signup_response.status_code == 201, signup_response.text
    admin_data = signup_response.json()
    assert "admin" in admin_data["roles"]

    client.headers["Authorization"] = f"Bearer {admin_data['token']}"
    return {
        "client": client,
        "org_id": org_id,
        "admin_email": admin_email,
        "api_base": api_base,
    }


class TestCreateOrganization:
    """POST /organizations/."""

    def test_create_success(self, api_server, api_base):
        client = httpx.Client()
        org_id = _unique("create_org")

        response = client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Create Test", "region": "US", "config": {"tz": "UTC"}},
        )

        assert response.status_code == 201, response.text
        body = response.json()
        assert body["id"] == org_id
        assert body["name"] == "Create Test"
        assert body["region"] == "US"
        assert body["config"] == {"tz": "UTC"}

    def test_create_duplicate_id_rejected(self, api_server, api_base):
        client = httpx.Client()
        org_id = _unique("dup_create_org")

        first = client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Original", "region": "US", "config": {}},
        )
        assert first.status_code == 201, first.text

        second = client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Duplicate", "region": "US", "config": {}},
        )
        assert second.status_code == 409
        assert "already exists" in second.json()["detail"]


class TestGetOrganization:
    """GET /organizations/{org_id}."""

    def test_get_existing(self, api_server, api_base):
        client = httpx.Client()
        org_id = _unique("get_org")
        client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Get Me", "region": "CA", "config": {}},
        )

        response = client.get(f"{api_base}/organizations/{org_id}")

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == org_id
        assert body["name"] == "Get Me"
        assert body["region"] == "CA"

    def test_get_missing_returns_404(self, api_server, api_base):
        client = httpx.Client()

        response = client.get(f"{api_base}/organizations/does_not_exist_{int(time.time())}")

        assert response.status_code == 404


class TestListOrganizations:
    """GET /organizations/ with pagination + search + include_cancelled."""

    def test_list_returns_envelope(self, api_server, api_base):
        client = httpx.Client()
        org_id = _unique("list_env_org")
        client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "List Envelope", "region": "US", "config": {}},
        )

        response = client.get(f"{api_base}/organizations/")

        assert response.status_code == 200
        body = response.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        assert isinstance(body["items"], list)
        assert isinstance(body["total"], int)

    def test_list_search_q_filters_by_name(self, api_server, api_base):
        client = httpx.Client()
        marker = _unique("QMARK")
        org_id_a = f"listq_a_{marker}"
        org_id_b = f"listq_b_{marker}"
        client.post(
            f"{api_base}/organizations/",
            json={"id": org_id_a, "name": f"Alpha {marker}", "region": "US", "config": {}},
        )
        client.post(
            f"{api_base}/organizations/",
            json={"id": org_id_b, "name": "Beta Ignored", "region": "US", "config": {}},
        )

        response = client.get(f"{api_base}/organizations/", params={"q": marker})

        assert response.status_code == 200
        items = response.json()["items"]
        returned_ids = {o["id"] for o in items}
        assert org_id_a in returned_ids
        assert org_id_b not in returned_ids

    def test_list_excludes_cancelled_by_default(self, setup_admin):
        data = setup_admin
        client = data["client"]
        api_base = data["api_base"]

        # Cancel the setup admin's org (the admin belongs to it, satisfying verify_org_member)
        cancel = client.post(f"{api_base}/organizations/{data['org_id']}/cancel")
        assert cancel.status_code == 200, cancel.text

        # Scope the listing with q= so the assertion isn't sensitive to
        # unrelated orgs created by concurrent tests spilling past page 1.
        response = client.get(f"{api_base}/organizations/", params={"q": data["org_id"]})
        assert response.status_code == 200
        assert data["org_id"] not in {o["id"] for o in response.json()["items"]}

    def test_list_include_cancelled_true_returns_them(self, setup_admin):
        data = setup_admin
        client = data["client"]
        api_base = data["api_base"]

        client.post(f"{api_base}/organizations/{data['org_id']}/cancel")

        response = client.get(
            f"{api_base}/organizations/",
            params={"include_cancelled": True, "q": data["org_id"]},
        )
        assert response.status_code == 200
        assert data["org_id"] in {o["id"] for o in response.json()["items"]}


class TestUpdateOrganization:
    """PUT /organizations/{org_id}."""

    def test_update_partial(self, api_server, api_base):
        client = httpx.Client()
        org_id = _unique("upd_org")
        client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Before", "region": "US", "config": {}},
        )

        response = client.put(
            f"{api_base}/organizations/{org_id}",
            json={"name": "After"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "After"
        # Region left untouched
        assert response.json()["region"] == "US"

    def test_update_missing_returns_404(self, api_server, api_base):
        client = httpx.Client()

        response = client.put(
            f"{api_base}/organizations/nope_{int(time.time())}",
            json={"name": "wont matter"},
        )

        assert response.status_code == 404


class TestCancelRestoreOrganization:
    """POST /organizations/{org_id}/cancel and /restore (admin-gated)."""

    def test_cancel_requires_auth(self, api_server, api_base):
        client = httpx.Client()
        org_id = _unique("cancel_auth_org")
        client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Auth Guard", "region": "US", "config": {}},
        )

        response = client.post(f"{api_base}/organizations/{org_id}/cancel")

        # FastAPI HTTPBearer returns 403 when the Authorization header is missing.
        assert response.status_code == 403

    def test_cancel_sets_cancelled_at_and_retention(self, setup_admin):
        data = setup_admin
        client = data["client"]
        api_base = data["api_base"]

        response = client.post(f"{api_base}/organizations/{data['org_id']}/cancel")

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["cancelled_at"] is not None
        assert body["data_retention_until"] is not None

    def test_restore_clears_cancellation(self, setup_admin):
        data = setup_admin
        client = data["client"]
        api_base = data["api_base"]

        cancel = client.post(f"{api_base}/organizations/{data['org_id']}/cancel")
        assert cancel.status_code == 200

        response = client.post(f"{api_base}/organizations/{data['org_id']}/restore")

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["cancelled_at"] is None
        assert body["data_retention_until"] is None
        assert body["deletion_scheduled_at"] is None


class TestDeleteOrganization:
    """DELETE /organizations/{org_id}."""

    def test_delete_removes_org(self, api_server, api_base):
        client = httpx.Client()
        org_id = _unique("del_org")
        client.post(
            f"{api_base}/organizations/",
            json={"id": org_id, "name": "Delete Me", "region": "US", "config": {}},
        )

        response = client.delete(f"{api_base}/organizations/{org_id}")

        assert response.status_code == 204
        # And subsequent GET is 404
        follow = client.get(f"{api_base}/organizations/{org_id}")
        assert follow.status_code == 404

    def test_delete_missing_returns_404(self, api_server, api_base):
        client = httpx.Client()

        response = client.delete(f"{api_base}/organizations/nope_{int(time.time())}")

        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
