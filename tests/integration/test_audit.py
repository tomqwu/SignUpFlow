#!/usr/bin/env python3
"""Integration tests: audit-logs router (Sprint 4 PR 4.6b).

Tests /api/v1/audit-logs over real HTTP against the session-scoped
uvicorn api_server. The router is admin-only and each read is itself
audited as `data.exported`, so we can assert both the envelope shape
and the self-recording behavior.
"""

import random
import time

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


@pytest.fixture
def audit_org(api_server, api_base):
    marker = _unique("audit_org")
    org_id = marker
    admin_email = f"admin_{marker}@test.com"
    vol_email = f"vol_{marker}@test.com"

    bootstrap = httpx.Client()
    org_resp = bootstrap.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"Audit Setup {marker}", "region": "US", "config": {}},
    )
    assert org_resp.status_code == 201, org_resp.text

    admin_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Audit Admin",
            "email": admin_email,
            "password": "AdminPass123!",
        },
    )
    assert admin_resp.status_code == 201, admin_resp.text
    admin_data = admin_resp.json()

    vol_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Audit Volunteer",
            "email": vol_email,
            "password": "VolPass123!",
            "roles": ["volunteer"],
        },
    )
    assert vol_resp.status_code == 201, vol_resp.text
    vol_data = vol_resp.json()
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
        "vol_client": vol_client,
        "api_base": api_base,
    }

    admin_client.close()
    vol_client.close()


class TestAuditListAuthGate:
    """Admin-only enforcement + envelope shape."""

    def test_admin_can_read(self, audit_org):
        data = audit_org
        resp = data["admin_client"].get(f"{data['api_base']}/audit-logs")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}

    def test_volunteer_forbidden(self, audit_org):
        data = audit_org
        resp = data["vol_client"].get(f"{data['api_base']}/audit-logs")
        assert resp.status_code == 403

    def test_unauthenticated_rejected(self, audit_org):
        data = audit_org
        anon = httpx.Client()
        try:
            resp = anon.get(f"{data['api_base']}/audit-logs")
        finally:
            anon.close()
        assert resp.status_code in (401, 403)


class TestAuditSelfRecording:
    """Reading audit-logs is itself an audited event (`data.exported`)."""

    def test_read_records_data_exported(self, audit_org):
        data = audit_org
        first = data["admin_client"].get(f"{data['api_base']}/audit-logs")
        assert first.status_code == 200
        first_total = first.json()["total"]

        # Read again — the previous read should have logged one row
        second = data["admin_client"].get(
            f"{data['api_base']}/audit-logs",
            params={"action": "data.exported"},
        )
        assert second.status_code == 200
        body = second.json()
        assert body["total"] >= 1
        assert all(row["action"] == "data.exported" for row in body["items"])
        # Total row count strictly grew (at minimum by the first read's log row)
        assert body["total"] > first_total or first_total == 0

    def test_scoped_to_current_admin_org(self, audit_org):
        data = audit_org
        resp = data["admin_client"].get(f"{data['api_base']}/audit-logs")
        assert resp.status_code == 200
        # All rows must be within the caller's org (or NULL org for a
        # cross-org row: the router filters organization_id == admin.org_id
        # so we expect no NULL rows here either).
        for row in resp.json()["items"]:
            assert row["organization_id"] == data["org_id"]


class TestAuditFilters:
    """Query parameters filter rows."""

    def test_action_filter(self, audit_org):
        data = audit_org
        # Prime the log with two known actions
        data["admin_client"].get(f"{data['api_base']}/audit-logs")
        # Also generate an unrelated audited action: password change requires
        # a signup already done. Simplest: another read with a filter present
        # still generates a `data.exported` row.

        resp = data["admin_client"].get(
            f"{data['api_base']}/audit-logs",
            params={"action": "data.exported"},
        )
        assert resp.status_code == 200
        rows = resp.json()["items"]
        assert all(r["action"] == "data.exported" for r in rows)

    def test_user_id_filter(self, audit_org):
        data = audit_org
        # Read the log once so a row exists for this admin
        data["admin_client"].get(f"{data['api_base']}/audit-logs")
        resp = data["admin_client"].get(
            f"{data['api_base']}/audit-logs",
            params={"user_id": data["admin_id"]},
        )
        assert resp.status_code == 200
        rows = resp.json()["items"]
        assert all(r["user_id"] == data["admin_id"] for r in rows)

    def test_pagination_envelope_echoes_params(self, audit_org):
        data = audit_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/audit-logs",
            params={"limit": 5, "offset": 0},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["limit"] == 5
        assert body["offset"] == 0

    def test_unknown_action_returns_empty(self, audit_org):
        data = audit_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/audit-logs",
            params={"action": "no.such.action.exists"},
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
