#!/usr/bin/env python3
"""Integration tests: events router (Sprint 4 PR 4.6b).

Tests the /api/v1/events endpoints over real HTTP against the
session-scoped uvicorn api_server:
- POST   /events/                    - Create (admin)
- GET    /events/                    - List (org_id, q, status filters)
- GET    /events/{event_id}          - Get one
- PUT    /events/{event_id}          - Update (admin)
- DELETE /events/{event_id}          - Delete (admin)
- GET    /events/{event_id}/available-people - Role-matched people
- GET    /events/{event_id}/validation       - Config sanity check
"""

import random
import time
from datetime import UTC, datetime, timedelta

import httpx
import pytest


def _unique(prefix: str) -> str:
    """Stable-but-unique suffix; combine ms + randint to avoid same-ms collisions."""
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


def _future_window(days: int = 14, hours: int = 2) -> tuple[str, str]:
    start = (datetime.now(UTC) + timedelta(days=days)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )
    end = start + timedelta(hours=hours)
    return start.isoformat(), end.isoformat()


@pytest.fixture
def setup_admin(api_server, api_base):
    """Create an org + admin user; return an authed httpx.Client scoped to the org."""
    client = httpx.Client()

    org_id = _unique("evt_org")
    org_response = client.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"Events Test Org {org_id}", "region": "US", "config": {}},
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
        "admin_person_id": admin_data["person_id"],
        "api_base": api_base,
    }


def _create_event(
    setup,
    event_id: str | None = None,
    event_type: str = "worship",
    days: int = 14,
    role_counts: dict | None = None,
):
    client = setup["client"]
    api_base = setup["api_base"]
    eid = event_id or _unique("evt")
    start, end = _future_window(days=days)
    extra_data: dict = {}
    if role_counts:
        extra_data["role_counts"] = role_counts
    resp = client.post(
        f"{api_base}/events/",
        json={
            "id": eid,
            "org_id": setup["org_id"],
            "type": event_type,
            "start_time": start,
            "end_time": end,
            "extra_data": extra_data,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


class TestCreateEvent:
    """POST /events/ — admin-gated create."""

    def test_create_success(self, setup_admin):
        setup = setup_admin
        client = setup["client"]
        api_base = setup["api_base"]
        event_id = _unique("create_evt")
        start, end = _future_window()

        resp = client.post(
            f"{api_base}/events/",
            json={
                "id": event_id,
                "org_id": setup["org_id"],
                "type": "worship",
                "start_time": start,
                "end_time": end,
                "extra_data": {"role_counts": {"usher": 2}},
            },
        )

        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["id"] == event_id
        assert body["org_id"] == setup["org_id"]
        assert body["type"] == "worship"
        assert body["extra_data"]["role_counts"]["usher"] == 2

    def test_create_requires_admin(self, api_server, api_base):
        # Unauthenticated POST: FastAPI HTTPBearer returns 403 with no header.
        client = httpx.Client()
        start, end = _future_window()
        resp = client.post(
            f"{api_base}/events/",
            json={
                "id": _unique("noauth_evt"),
                "org_id": "does_not_matter",
                "type": "worship",
                "start_time": start,
                "end_time": end,
            },
        )
        assert resp.status_code == 403

    def test_create_duplicate_id_conflicts(self, setup_admin):
        setup = setup_admin
        first = _create_event(setup, event_id=_unique("dup_evt"))

        client = setup["client"]
        api_base = setup["api_base"]
        start, end = _future_window(days=20)
        resp = client.post(
            f"{api_base}/events/",
            json={
                "id": first["id"],
                "org_id": setup["org_id"],
                "type": "worship",
                "start_time": start,
                "end_time": end,
            },
        )
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]

    def test_create_missing_org_returns_404(self, setup_admin):
        # Setup gives us an admin token bound to a real org; simulate a stale
        # org_id (admin's own org used for verify_org_member gate). We need a
        # separate admin whose org will be deleted — simpler: send a random
        # org_id the current admin doesn't belong to.
        setup = setup_admin
        client = setup["client"]
        api_base = setup["api_base"]
        start, end = _future_window()
        resp = client.post(
            f"{api_base}/events/",
            json={
                "id": _unique("orphan_evt"),
                "org_id": "does_not_exist_org_xyz",
                "type": "worship",
                "start_time": start,
                "end_time": end,
            },
        )
        # verify_org_member fires first (admin isn't a member of that org) → 403.
        # If it ever gets past that guard, the org lookup returns 404. Accept both.
        assert resp.status_code in (403, 404)

    def test_create_invalid_time_range_rejected(self, setup_admin):
        setup = setup_admin
        client = setup["client"]
        api_base = setup["api_base"]
        # end_time before start_time
        start = (datetime.now(UTC) + timedelta(days=7)).isoformat()
        end = (datetime.now(UTC) + timedelta(days=6)).isoformat()

        resp = client.post(
            f"{api_base}/events/",
            json={
                "id": _unique("badtime_evt"),
                "org_id": setup["org_id"],
                "type": "worship",
                "start_time": start,
                "end_time": end,
            },
        )
        assert resp.status_code == 400


class TestGetEvent:
    """GET /events/{event_id}."""

    def test_get_existing(self, setup_admin):
        setup = setup_admin
        event = _create_event(setup)

        resp = setup["client"].get(f"{setup['api_base']}/events/{event['id']}")

        assert resp.status_code == 200
        assert resp.json()["id"] == event["id"]

    def test_get_missing_returns_404(self, setup_admin):
        setup = setup_admin
        resp = setup["client"].get(f"{setup['api_base']}/events/does_not_exist_{int(time.time())}")
        assert resp.status_code == 404


class TestListEvents:
    """GET /events/ — envelope, filters, search."""

    def test_list_returns_envelope(self, setup_admin):
        setup = setup_admin
        _create_event(setup)

        resp = setup["client"].get(
            f"{setup['api_base']}/events/", params={"org_id": setup["org_id"]}
        )

        assert resp.status_code == 200
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        assert isinstance(body["items"], list)
        assert body["total"] >= 1

    def test_list_filter_by_org_id_scopes_results(self, setup_admin):
        setup = setup_admin
        our_event = _create_event(setup)

        resp = setup["client"].get(
            f"{setup['api_base']}/events/", params={"org_id": setup["org_id"]}
        )
        assert resp.status_code == 200
        returned_org_ids = {e["org_id"] for e in resp.json()["items"]}
        # Every returned event belongs to our org
        assert returned_org_ids == {setup["org_id"]}
        assert our_event["id"] in {e["id"] for e in resp.json()["items"]}

    def test_list_search_q_filters_by_type_or_id(self, setup_admin):
        setup = setup_admin
        marker = _unique("QSEARCH").upper()
        target_id = f"qhit_{marker}"
        _create_event(setup, event_id=target_id, event_type=f"lookup_{marker}")
        # And a decoy in the same org that should not match
        _create_event(setup, event_type="other_type")

        resp = setup["client"].get(
            f"{setup['api_base']}/events/",
            params={"org_id": setup["org_id"], "q": marker},
        )

        assert resp.status_code == 200
        returned_ids = {e["id"] for e in resp.json()["items"]}
        assert target_id in returned_ids
        # Every returned item mentions the marker
        for item in resp.json()["items"]:
            haystack = f"{item['id']}|{item['type']}".upper()
            assert marker in haystack

    def test_list_status_upcoming_excludes_past(self, setup_admin):
        setup = setup_admin
        _create_event(setup, days=30)  # upcoming

        resp = setup["client"].get(
            f"{setup['api_base']}/events/",
            params={"org_id": setup["org_id"], "status": "upcoming"},
        )
        assert resp.status_code == 200
        now = datetime.now(UTC)
        for item in resp.json()["items"]:
            # start_time comes back as ISO string; parse and compare
            start = datetime.fromisoformat(item["start_time"].replace("Z", "+00:00"))
            assert start > now


class TestUpdateEvent:
    """PUT /events/{event_id} — admin-gated."""

    def test_update_partial(self, setup_admin):
        setup = setup_admin
        event = _create_event(setup, event_type="before_update")

        resp = setup["client"].put(
            f"{setup['api_base']}/events/{event['id']}",
            json={"type": "after_update"},
        )
        assert resp.status_code == 200
        assert resp.json()["type"] == "after_update"

    def test_update_missing_returns_404(self, setup_admin):
        setup = setup_admin
        resp = setup["client"].put(
            f"{setup['api_base']}/events/nope_{int(time.time())}",
            json={"type": "wontmatter"},
        )
        assert resp.status_code == 404

    def test_update_requires_auth(self, api_server, api_base, setup_admin):
        # Create with authed admin, then hit PUT with a fresh unauthed client.
        setup = setup_admin
        event = _create_event(setup)

        anon = httpx.Client()
        resp = anon.put(
            f"{api_base}/events/{event['id']}",
            json={"type": "hacked"},
        )
        assert resp.status_code == 403


class TestDeleteEvent:
    """DELETE /events/{event_id} — admin-gated."""

    def test_delete_removes_event(self, setup_admin):
        setup = setup_admin
        event = _create_event(setup)

        resp = setup["client"].delete(f"{setup['api_base']}/events/{event['id']}")

        assert resp.status_code == 204
        follow = setup["client"].get(f"{setup['api_base']}/events/{event['id']}")
        assert follow.status_code == 404

    def test_delete_missing_returns_404(self, setup_admin):
        setup = setup_admin
        resp = setup["client"].delete(f"{setup['api_base']}/events/nope_{int(time.time())}")
        assert resp.status_code == 404


class TestAvailablePeopleAndValidation:
    """GET /events/{id}/available-people and /validation."""

    def test_available_people_returns_role_matched(self, setup_admin):
        setup = setup_admin
        # Admin was created in setup with default admin/volunteer roles.
        # Create event that requires "admin" role so the admin shows up.
        event = _create_event(setup, role_counts={"admin": 1})

        resp = setup["client"].get(f"{setup['api_base']}/events/{event['id']}/available-people")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        # Our admin should be in the list
        assert any(p["id"] == setup["admin_person_id"] for p in body)

    def test_validation_flags_missing_role_config(self, setup_admin):
        setup = setup_admin
        # Event without role_counts → should be invalid with a missing_config warning.
        event = _create_event(setup, role_counts=None)

        resp = setup["client"].get(f"{setup['api_base']}/events/{event['id']}/validation")
        assert resp.status_code == 200
        body = resp.json()
        assert body["event_id"] == event["id"]
        assert body["is_valid"] is False
        assert any(w["type"] == "missing_config" for w in body["warnings"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
