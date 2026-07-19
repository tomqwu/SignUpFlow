#!/usr/bin/env python3
"""Integration tests: conflicts router (Sprint 4 PR 4.6b).

Tests the /api/v1/conflicts endpoints over real HTTP against the
session-scoped uvicorn api_server:
- POST /conflicts/check  - Pre-assignment conflict check
- GET  /conflicts/       - Admin-only org-wide conflict listing (ListResponse envelope)
"""

import random
import time
from datetime import UTC, date, datetime, timedelta

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


def _future_window(days: int = 14, hours: int = 2) -> tuple[str, str]:
    start = (datetime.now(UTC) + timedelta(days=days)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )
    end = start + timedelta(hours=hours)
    return start.isoformat(), end.isoformat()


@pytest.fixture
def conflicts_org(api_server, api_base):
    """Create an org + admin + one volunteer; return clients + ids."""
    marker = _unique("conflicts_org")
    org_id = marker
    admin_email = f"admin_{marker}@test.com"
    vol_email = f"vol_{marker}@test.com"

    bootstrap = httpx.Client()

    org_resp = bootstrap.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"Conflicts Setup {marker}", "region": "US", "config": {}},
    )
    assert org_resp.status_code == 201, org_resp.text

    admin_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Conflict Admin",
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
            "name": "Conflict Volunteer",
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
        "admin_client": admin_client,
        "vol_id": vol_data["person_id"],
        "vol_client": vol_client,
        "api_base": api_base,
    }

    admin_client.close()
    vol_client.close()


def _create_event(client, api_base, org_id, *, days: int = 14, event_type: str = "worship") -> dict:
    """Helper: create an event via the admin client and return its body."""
    event_id = _unique("evt")
    start, end = _future_window(days=days)
    resp = client.post(
        f"{api_base}/events/",
        json={
            "id": event_id,
            "org_id": org_id,
            "type": event_type,
            "start_time": start,
            "end_time": end,
            "extra_data": {},
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _assign(client, api_base, event_id: str, person_id: str, role: str | None = None) -> dict:
    """Helper: admin assigns a person to an event via POST /events/{id}/assignments."""
    resp = client.post(
        f"{api_base}/events/{event_id}/assignments",
        json={"person_id": person_id, "action": "assign", "role": role},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _add_timeoff(api_base: str, person_id: str, start: date, end: date) -> None:
    """Helper: post a time-off period for a person (unauthenticated endpoint)."""
    anon = httpx.Client()
    try:
        resp = anon.post(
            f"{api_base}/availability/{person_id}/timeoff",
            json={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "reason": "integration test",
            },
        )
        assert resp.status_code == 201, resp.text
    finally:
        anon.close()


class TestCheckConflicts:
    """POST /conflicts/check — pre-assignment conflict detection."""

    def test_no_conflict_returns_can_assign(self, conflicts_org):
        data = conflicts_org
        event = _create_event(data["admin_client"], data["api_base"], data["org_id"])

        # Unauthenticated for this endpoint (no auth dependency in the router).
        anon = httpx.Client()
        try:
            resp = anon.post(
                f"{data['api_base']}/conflicts/check",
                json={"person_id": data["vol_id"], "event_id": event["id"]},
            )
        finally:
            anon.close()
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["has_conflicts"] is False
        assert body["can_assign"] is True
        assert body["conflicts"] == []

    def test_already_assigned_blocks(self, conflicts_org):
        data = conflicts_org
        event = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        _assign(data["admin_client"], data["api_base"], event["id"], data["vol_id"])

        resp = httpx.post(
            f"{data['api_base']}/conflicts/check",
            json={"person_id": data["vol_id"], "event_id": event["id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["has_conflicts"] is True
        assert body["can_assign"] is False
        types = [c["type"] for c in body["conflicts"]]
        assert "already_assigned" in types

    def test_time_off_blocks(self, conflicts_org):
        data = conflicts_org
        # Event 20 days out; time-off spanning that day
        event = _create_event(data["admin_client"], data["api_base"], data["org_id"], days=20)
        event_start = datetime.fromisoformat(event["start_time"]).date()
        _add_timeoff(
            data["api_base"],
            data["vol_id"],
            event_start - timedelta(days=1),
            event_start + timedelta(days=1),
        )

        resp = httpx.post(
            f"{data['api_base']}/conflicts/check",
            json={"person_id": data["vol_id"], "event_id": event["id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["has_conflicts"] is True
        assert body["can_assign"] is False
        types = [c["type"] for c in body["conflicts"]]
        assert "time_off" in types

    def test_double_booked_warns_but_allows(self, conflicts_org):
        data = conflicts_org
        event_a = _create_event(data["admin_client"], data["api_base"], data["org_id"], days=25)
        event_b = _create_event(data["admin_client"], data["api_base"], data["org_id"], days=25)
        # Both events use the identical future window: overlap guaranteed
        _assign(data["admin_client"], data["api_base"], event_a["id"], data["vol_id"])

        resp = httpx.post(
            f"{data['api_base']}/conflicts/check",
            json={"person_id": data["vol_id"], "event_id": event_b["id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        types = [c["type"] for c in body["conflicts"]]
        assert "double_booked" in types
        # Double-booked is non-blocking per the router contract
        assert body["can_assign"] is True

    def test_missing_person_returns_404(self, conflicts_org):
        data = conflicts_org
        event = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        resp = httpx.post(
            f"{data['api_base']}/conflicts/check",
            json={"person_id": f"ghost_{int(time.time())}", "event_id": event["id"]},
        )
        assert resp.status_code == 404

    def test_missing_event_returns_404(self, conflicts_org):
        data = conflicts_org
        resp = httpx.post(
            f"{data['api_base']}/conflicts/check",
            json={"person_id": data["vol_id"], "event_id": f"nope_{int(time.time())}"},
        )
        assert resp.status_code == 404


class TestListConflicts:
    """GET /conflicts/ — admin-only org-wide conflict listing."""

    def test_list_empty_when_no_conflicts(self, conflicts_org):
        data = conflicts_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/conflicts/",
            params={"org_id": data["org_id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        assert body["total"] == 0
        assert body["items"] == []

    def test_list_surfaces_time_off_conflict(self, conflicts_org):
        data = conflicts_org
        event = _create_event(data["admin_client"], data["api_base"], data["org_id"], days=30)
        _assign(data["admin_client"], data["api_base"], event["id"], data["vol_id"])
        event_start = datetime.fromisoformat(event["start_time"]).date()
        _add_timeoff(
            data["api_base"],
            data["vol_id"],
            event_start - timedelta(days=1),
            event_start + timedelta(days=1),
        )

        resp = data["admin_client"].get(
            f"{data['api_base']}/conflicts/",
            params={"org_id": data["org_id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] >= 1
        assert any(c["type"] == "time_off" for c in body["items"])

    def test_list_surfaces_double_booked(self, conflicts_org):
        data = conflicts_org
        # Two overlapping events, volunteer assigned to both
        event_a = _create_event(data["admin_client"], data["api_base"], data["org_id"], days=35)
        event_b = _create_event(data["admin_client"], data["api_base"], data["org_id"], days=35)
        _assign(data["admin_client"], data["api_base"], event_a["id"], data["vol_id"])
        _assign(data["admin_client"], data["api_base"], event_b["id"], data["vol_id"])

        resp = data["admin_client"].get(
            f"{data['api_base']}/conflicts/",
            params={"org_id": data["org_id"], "person_id": data["vol_id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] >= 1
        assert any(c["type"] == "double_booked" for c in body["items"])

    def test_list_person_filter_narrows_scope(self, conflicts_org):
        data = conflicts_org
        # Admin's own account has no conflicts; person_id filter yields empty
        resp = data["admin_client"].get(
            f"{data['api_base']}/conflicts/",
            params={"org_id": data["org_id"], "person_id": data["admin_id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] == 0

    def test_list_requires_admin(self, conflicts_org):
        data = conflicts_org
        resp = data["vol_client"].get(
            f"{data['api_base']}/conflicts/",
            params={"org_id": data["org_id"]},
        )
        assert resp.status_code == 403

    def test_list_unauthenticated_rejected(self, conflicts_org):
        data = conflicts_org
        anon = httpx.Client()
        try:
            resp = anon.get(
                f"{data['api_base']}/conflicts/",
                params={"org_id": data["org_id"]},
            )
        finally:
            anon.close()
        assert resp.status_code in (401, 403)

    def test_list_cross_org_rejected(self, conflicts_org):
        data = conflicts_org
        # Admin is not a member of some other sentinel org
        resp = data["admin_client"].get(
            f"{data['api_base']}/conflicts/",
            params={"org_id": f"other_{int(time.time())}"},
        )
        assert resp.status_code == 403

    def test_list_pagination_envelope(self, conflicts_org):
        data = conflicts_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/conflicts/",
            params={"org_id": data["org_id"], "limit": 5, "offset": 0},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["limit"] == 5
        assert body["offset"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
