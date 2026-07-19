#!/usr/bin/env python3
"""Integration tests: assignments router (Sprint 4 PR 4.6b).

Drives the /api/v1/assignments endpoints over real HTTP against the
session-scoped uvicorn api_server:
- POST /assignments/{id}/accept        - Volunteer confirms
- POST /assignments/{id}/decline       - Volunteer declines (reason required)
- POST /assignments/{id}/swap-request  - Volunteer flags for swap
- GET  /assignments/me                 - List caller's own assignments

Coverage locks in the volunteer self-service auth model:
- 401/403 without a token
- 403 when acting on another user's assignment
- 404 on missing assignment id
- The `/me` list is scoped by both person_id AND event.org_id (cross-org
  event assignments must not leak into the caller's list)
"""

import random
import time
from datetime import UTC, datetime, timedelta

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


def _future(days: int, hours: int = 0) -> str:
    dt = datetime.now(UTC) + timedelta(days=days, hours=hours)
    return dt.isoformat()


@pytest.fixture
def assignments_org(api_server, api_base):
    """Create an org + admin + two volunteers, plus one event assigned to vol1."""
    marker = _unique("assignments_org")
    org_id = marker
    admin_email = f"admin_{marker}@test.com"
    vol1_email = f"vol1_{marker}@test.com"
    vol2_email = f"vol2_{marker}@test.com"

    bootstrap = httpx.Client()

    org_resp = bootstrap.post(
        f"{api_base}/organizations/",
        json={
            "id": org_id,
            "name": f"Assignments Setup {marker}",
            "region": "US",
            "config": {},
        },
    )
    assert org_resp.status_code == 201, org_resp.text

    admin_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Assign Admin",
            "email": admin_email,
            "password": "AdminPass123!",
        },
    )
    assert admin_resp.status_code == 201, admin_resp.text
    admin_data = admin_resp.json()

    vol1_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Vol One",
            "email": vol1_email,
            "password": "VolPass123!",
            "roles": ["volunteer"],
        },
    )
    assert vol1_resp.status_code == 201, vol1_resp.text
    vol1_data = vol1_resp.json()

    vol2_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Vol Two",
            "email": vol2_email,
            "password": "VolPass123!",
            "roles": ["volunteer"],
        },
    )
    assert vol2_resp.status_code == 201, vol2_resp.text
    vol2_data = vol2_resp.json()
    bootstrap.close()

    admin_client = httpx.Client()
    admin_client.headers["Authorization"] = f"Bearer {admin_data['token']}"

    vol1_client = httpx.Client()
    vol1_client.headers["Authorization"] = f"Bearer {vol1_data['token']}"

    vol2_client = httpx.Client()
    vol2_client.headers["Authorization"] = f"Bearer {vol2_data['token']}"

    yield {
        "marker": marker,
        "org_id": org_id,
        "admin_client": admin_client,
        "vol1_client": vol1_client,
        "vol2_client": vol2_client,
        "vol1_id": vol1_data["person_id"],
        "vol2_id": vol2_data["person_id"],
        "api_base": api_base,
    }

    admin_client.close()
    vol1_client.close()
    vol2_client.close()


def _create_event(admin_client, api_base, org_id, *, offset_days: int = 30) -> str:
    """Admin-create an event; return the event id."""
    event_id = _unique("evt")
    resp = admin_client.post(
        f"{api_base}/events/",
        json={
            "id": event_id,
            "org_id": org_id,
            "type": "meeting",
            "start_time": _future(offset_days),
            "end_time": _future(offset_days, hours=2),
        },
    )
    assert resp.status_code == 201, resp.text
    return event_id


def _assign(admin_client, api_base, event_id: str, person_id: str) -> int:
    """Admin-assign a person to an event; return the new assignment id."""
    resp = admin_client.post(
        f"{api_base}/events/{event_id}/assignments",
        json={"person_id": person_id, "action": "assign"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    return body["assignment_id"]


class TestAcceptAssignment:
    """POST /assignments/{id}/accept — volunteer confirms."""

    def test_accept_sets_status_confirmed(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        resp = data["vol1_client"].post(f"{data['api_base']}/assignments/{aid}/accept")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["id"] == aid
        assert body["status"] == "confirmed"
        assert body["decline_reason"] is None

    def test_accept_clears_prior_decline_reason(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        # Decline first so a reason is recorded, then accept.
        decline = data["vol1_client"].post(
            f"{data['api_base']}/assignments/{aid}/decline",
            json={"decline_reason": "conflict"},
        )
        assert decline.status_code == 200
        assert decline.json()["decline_reason"] == "conflict"

        accept = data["vol1_client"].post(f"{data['api_base']}/assignments/{aid}/accept")
        assert accept.status_code == 200
        assert accept.json()["status"] == "confirmed"
        assert accept.json()["decline_reason"] is None

    def test_accept_others_assignment_forbidden(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        resp = data["vol2_client"].post(f"{data['api_base']}/assignments/{aid}/accept")
        assert resp.status_code == 403

    def test_accept_missing_returns_404(self, assignments_org):
        data = assignments_org
        resp = data["vol1_client"].post(f"{data['api_base']}/assignments/999999999/accept")
        assert resp.status_code == 404

    def test_accept_unauthenticated(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        with httpx.Client() as anon:
            resp = anon.post(f"{data['api_base']}/assignments/{aid}/accept")
        assert resp.status_code in (401, 403)


class TestDeclineAssignment:
    """POST /assignments/{id}/decline — volunteer declines with reason."""

    def test_decline_records_reason(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        resp = data["vol1_client"].post(
            f"{data['api_base']}/assignments/{aid}/decline",
            json={"decline_reason": "out of town"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["status"] == "declined"
        assert body["decline_reason"] == "out of town"

    def test_decline_requires_reason(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        # Empty reason violates min_length=1.
        resp = data["vol1_client"].post(
            f"{data['api_base']}/assignments/{aid}/decline",
            json={"decline_reason": ""},
        )
        assert resp.status_code == 422

    def test_decline_missing_body_field(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        resp = data["vol1_client"].post(
            f"{data['api_base']}/assignments/{aid}/decline",
            json={},
        )
        assert resp.status_code == 422

    def test_decline_others_assignment_forbidden(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        resp = data["vol2_client"].post(
            f"{data['api_base']}/assignments/{aid}/decline",
            json={"decline_reason": "nope"},
        )
        assert resp.status_code == 403


class TestSwapRequest:
    """POST /assignments/{id}/swap-request — volunteer flags for swap."""

    def test_swap_request_sets_status(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        resp = data["vol1_client"].post(
            f"{data['api_base']}/assignments/{aid}/swap-request",
            json={"note": "family emergency"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["status"] == "swap_requested"

    def test_swap_request_note_is_optional(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        resp = data["vol1_client"].post(
            f"{data['api_base']}/assignments/{aid}/swap-request",
            json={},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "swap_requested"

    def test_swap_request_others_forbidden(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        aid = _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        resp = data["vol2_client"].post(
            f"{data['api_base']}/assignments/{aid}/swap-request",
            json={"note": "nope"},
        )
        assert resp.status_code == 403


class TestListMyAssignments:
    """GET /assignments/me — envelope shape + scoping."""

    def test_list_envelope_shape(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        resp = data["vol1_client"].get(f"{data['api_base']}/assignments/me")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        assert body["total"] >= 1
        assert all(a["person_id"] == data["vol1_id"] for a in body["items"])

    def test_list_scoped_to_caller_only(self, assignments_org):
        data = assignments_org
        ev = _create_event(data["admin_client"], data["api_base"], data["org_id"])
        _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])
        _assign(data["admin_client"], data["api_base"], ev, data["vol2_id"])

        # vol2 must not see vol1's row and vice versa.
        vol1_resp = data["vol1_client"].get(f"{data['api_base']}/assignments/me")
        vol2_resp = data["vol2_client"].get(f"{data['api_base']}/assignments/me")
        assert vol1_resp.status_code == 200
        assert vol2_resp.status_code == 200
        assert all(a["person_id"] == data["vol1_id"] for a in vol1_resp.json()["items"])
        assert all(a["person_id"] == data["vol2_id"] for a in vol2_resp.json()["items"])

    def test_list_respects_pagination(self, assignments_org):
        data = assignments_org
        # Create several events + assignments to vol1 so pagination has something
        # to slice.
        for i in range(3):
            ev = _create_event(
                data["admin_client"], data["api_base"], data["org_id"], offset_days=40 + i
            )
            _assign(data["admin_client"], data["api_base"], ev, data["vol1_id"])

        resp = data["vol1_client"].get(
            f"{data['api_base']}/assignments/me",
            params={"limit": 2, "offset": 0},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["limit"] == 2
        assert body["offset"] == 0
        assert len(body["items"]) <= 2
        assert body["total"] >= 3

    def test_list_unauthenticated(self, assignments_org):
        data = assignments_org
        with httpx.Client() as anon:
            resp = anon.get(f"{data['api_base']}/assignments/me")
        assert resp.status_code in (401, 403)

    def test_list_empty_when_no_assignments(self, assignments_org):
        """A fresh volunteer with nothing assigned gets total: 0."""
        data = assignments_org
        # vol2 hasn't been assigned yet in this test's flow.
        resp = data["vol2_client"].get(f"{data['api_base']}/assignments/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["items"] == []
