#!/usr/bin/env python3
"""Integration tests: organizations router (Sprint 4 PR 4.6b).

Tests the /api/v1/organizations endpoints over real HTTP against the
session-scoped uvicorn api_server:
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

from tests.integration._identity import bootstrap_admin


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


@pytest.fixture
def setup_admin(api_server, api_base):
    """Create an org + admin user; return a JWT-authed httpx.Client."""
    client = httpx.Client()

    org_id = _unique("org_admin_setup")
    # Bake org_id into name so we can filter by q= even when other tests
    # create many orgs concurrently.
    admin_email = f"admin_{org_id}@test.com"
    admin_data = bootstrap_admin(
        client,
        api_base,
        org_id=org_id,
        org_name=f"Admin Setup Org {org_id}",
        name="Admin User",
        email=admin_email,
        password="AdminPass123!",
        region="US",
    )
    assert "admin" in admin_data["roles"]

    client.headers["Authorization"] = f"Bearer {admin_data['token']}"
    return {
        "client": client,
        "org_id": org_id,
        "admin_email": admin_email,
        "api_base": api_base,
    }


class TestCreateOrganization:
    """Organization creation is part of atomic signup, never an empty public write."""

    def test_public_empty_organization_creation_is_unavailable(self, api_server, api_base):
        response = httpx.post(
            f"{api_base}/organizations/",
            json={"id": _unique("empty_org"), "name": "Empty Org"},
        )

        assert response.status_code == 405


class TestGetOrganization:
    """Authenticated organization reads."""

    def test_get_existing(self, setup_admin):
        data = setup_admin
        response = data["client"].get(f"{data['api_base']}/organizations/{data['org_id']}")
        assert response.status_code == 200
        assert response.json()["id"] == data["org_id"]

    def test_anonymous_read_denied(self, api_server, api_base):
        with httpx.Client() as client:
            response = client.get(f"{api_base}/organizations/unknown")
        assert response.status_code == 401

    def test_unknown_tenant_does_not_reveal_existence(self, setup_admin):
        data = setup_admin
        response = data["client"].get(f"{data['api_base']}/organizations/unknown")
        assert response.status_code == 403


class TestListOrganizations:
    """List/search only the caller's tenant, including cancellation filters."""

    def test_list_returns_envelope(self, setup_admin):
        data = setup_admin
        response = data["client"].get(f"{data['api_base']}/organizations/")
        assert response.status_code == 200
        body = response.json()
        assert set(body) >= {"items", "total", "limit", "offset"}
        assert body["total"] == 1
        assert [org["id"] for org in body["items"]] == [data["org_id"]]

    def test_list_search_q_filters_by_name_and_membership(self, setup_admin):
        data = setup_admin
        client, api_base = data["client"], data["api_base"]
        other = _unique("foreign")
        with httpx.Client() as bootstrap:
            bootstrap_admin(
                bootstrap,
                api_base,
                org_id=other,
                org_name=data["org_id"],
                name="Foreign Admin",
                email=f"admin_{other}@test.com",
                password="AdminPass123!",
            )
        response = client.get(f"{api_base}/organizations/", params={"q": data["org_id"]})
        assert response.status_code == 200
        assert [row["id"] for row in response.json()["items"]] == [data["org_id"]]
        response = client.get(f"{api_base}/organizations/", params={"q": "not-a-matching-name"})
        assert response.json()["total"] == 0

    def test_list_excludes_cancelled_by_default(self, setup_admin):
        data = setup_admin
        client, api_base = data["client"], data["api_base"]
        response = client.post(f"{api_base}/organizations/{data['org_id']}/cancel")
        assert response.status_code == 200
        response = client.get(f"{api_base}/organizations/")
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_list_include_cancelled_true_returns_own_tenant(self, setup_admin):
        data = setup_admin
        client, api_base = data["client"], data["api_base"]
        assert client.post(f"{api_base}/organizations/{data['org_id']}/cancel").status_code == 200
        response = client.get(f"{api_base}/organizations/", params={"include_cancelled": True})
        assert response.status_code == 200
        assert [row["id"] for row in response.json()["items"]] == [data["org_id"]]


class TestUpdateOrganization:
    """Only the owning authenticated admin may update settings."""

    def test_update_partial(self, setup_admin):
        data = setup_admin
        response = data["client"].put(
            f"{data['api_base']}/organizations/{data['org_id']}", json={"name": "After"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "After"
        assert response.json()["region"] == "US"

    def test_update_other_tenant_denied(self, setup_admin):
        data = setup_admin
        response = data["client"].put(
            f"{data['api_base']}/organizations/unknown", json={"name": "Denied"}
        )
        assert response.status_code == 403


class TestCancelRestoreOrganization:
    """POST /organizations/{org_id}/cancel and /restore (admin-gated)."""

    def test_cancel_requires_auth(self, api_server, api_base):
        client = httpx.Client()
        org_id = _unique("cancel_auth_org")
        response = client.post(f"{api_base}/organizations/{org_id}/cancel")

        assert response.status_code == 401

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
    """Hard deletion removes membership and invalidates subsequent requests."""

    def test_delete_removes_org_and_owner(self, setup_admin):
        data = setup_admin
        client, api_base, org_id = data["client"], data["api_base"], data["org_id"]
        response = client.delete(f"{api_base}/organizations/{org_id}")
        assert response.status_code == 204
        assert client.get(f"{api_base}/organizations/{org_id}").status_code == 401

    def test_delete_other_tenant_denied(self, setup_admin):
        data = setup_admin
        response = data["client"].delete(f"{data['api_base']}/organizations/unknown")
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
