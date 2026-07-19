#!/usr/bin/env python3
"""Integration tests: calendar router (Sprint 4 PR 4.6b).

Tests /api/v1/calendar endpoints over real HTTP against the
session-scoped uvicorn api_server:
- GET  /calendar/subscribe                 - Get subscription URL (self or admin)
- POST /calendar/reset-token               - Rotate subscription token
- POST /calendar/{person_id}/admin-reset   - Admin-only rotate
- GET  /calendar/feed/{token}              - Public ICS feed by token
- GET  /calendar/org/export                - Admin org-wide ICS
- GET  /calendar/export                    - Personal ICS (assignments only)
"""

import random
import time
from datetime import UTC, datetime, timedelta

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


@pytest.fixture
def calendar_org(api_server, api_base):
    marker = _unique("cal_org")
    org_id = marker
    admin_email = f"admin_{marker}@test.com"
    vol_email = f"vol_{marker}@test.com"
    other_org_id = f"{marker}_other"

    bootstrap = httpx.Client()
    for oid, name in ((org_id, f"Cal Setup {marker}"), (other_org_id, f"Other {marker}")):
        org_resp = bootstrap.post(
            f"{api_base}/organizations/",
            json={"id": oid, "name": name, "region": "US", "config": {}},
        )
        assert org_resp.status_code == 201, org_resp.text

    admin_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Cal Admin",
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
            "name": "Cal Volunteer",
            "email": vol_email,
            "password": "VolPass123!",
            "roles": ["volunteer"],
        },
    )
    assert vol_resp.status_code == 201, vol_resp.text
    vol_data = vol_resp.json()

    # Another org's admin (used for cross-org access checks)
    other_admin = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": other_org_id,
            "name": "Other Admin",
            "email": f"other_admin_{marker}@test.com",
            "password": "OtherPass123!",
        },
    )
    assert other_admin.status_code == 201, other_admin.text
    other_admin_data = other_admin.json()
    bootstrap.close()

    admin_client = httpx.Client()
    admin_client.headers["Authorization"] = f"Bearer {admin_data['token']}"

    vol_client = httpx.Client()
    vol_client.headers["Authorization"] = f"Bearer {vol_data['token']}"

    other_admin_client = httpx.Client()
    other_admin_client.headers["Authorization"] = f"Bearer {other_admin_data['token']}"

    yield {
        "marker": marker,
        "org_id": org_id,
        "other_org_id": other_org_id,
        "admin_id": admin_data["person_id"],
        "admin_client": admin_client,
        "vol_id": vol_data["person_id"],
        "vol_client": vol_client,
        "other_admin_client": other_admin_client,
        "api_base": api_base,
    }

    admin_client.close()
    vol_client.close()
    other_admin_client.close()


def _create_event_and_assign(setup: dict, person_id: str) -> dict:
    """Admin creates an event and assigns the person; returns the event body."""
    start = (datetime.now(UTC) + timedelta(days=21)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )
    end = start + timedelta(hours=2)
    event_id = _unique("evt")
    ev = setup["admin_client"].post(
        f"{setup['api_base']}/events/",
        json={
            "id": event_id,
            "org_id": setup["org_id"],
            "type": "worship",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "extra_data": {},
        },
    )
    assert ev.status_code == 201, ev.text
    ev_body = ev.json()

    assign = setup["admin_client"].post(
        f"{setup['api_base']}/events/{event_id}/assignments",
        json={"person_id": person_id, "action": "assign", "role": "usher"},
    )
    assert assign.status_code == 200, assign.text
    return ev_body


class TestSubscribe:
    """GET /calendar/subscribe — self or same-org admin."""

    def test_self_can_get_subscription(self, calendar_org):
        data = calendar_org
        resp = data["vol_client"].get(
            f"{data['api_base']}/calendar/subscribe",
            params={"person_id": data["vol_id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["token"]
        assert body["webcal_url"].startswith("webcal://")
        assert body["https_url"].startswith("http")

    def test_admin_can_get_others_subscription_in_same_org(self, calendar_org):
        data = calendar_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/calendar/subscribe",
            params={"person_id": data["vol_id"]},
        )
        assert resp.status_code == 200

    def test_other_org_admin_forbidden(self, calendar_org):
        data = calendar_org
        resp = data["other_admin_client"].get(
            f"{data['api_base']}/calendar/subscribe",
            params={"person_id": data["vol_id"]},
        )
        assert resp.status_code == 403

    def test_missing_person_404(self, calendar_org):
        data = calendar_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/calendar/subscribe",
            params={"person_id": f"ghost_{int(time.time())}"},
        )
        assert resp.status_code == 404

    def test_unauthenticated_rejected(self, calendar_org):
        data = calendar_org
        anon = httpx.Client()
        try:
            resp = anon.get(
                f"{data['api_base']}/calendar/subscribe",
                params={"person_id": data["vol_id"]},
            )
        finally:
            anon.close()
        assert resp.status_code in (401, 403)


class TestResetToken:
    """POST /calendar/reset-token — self or same-org admin rotates token."""

    def test_self_rotates(self, calendar_org):
        data = calendar_org
        first = data["vol_client"].get(
            f"{data['api_base']}/calendar/subscribe",
            params={"person_id": data["vol_id"]},
        )
        assert first.status_code == 200
        old_token = first.json()["token"]

        rotate = data["vol_client"].post(
            f"{data['api_base']}/calendar/reset-token",
            params={"person_id": data["vol_id"]},
        )
        assert rotate.status_code == 200, rotate.text
        new_token = rotate.json()["token"]
        assert new_token
        assert new_token != old_token

    def test_other_org_admin_forbidden(self, calendar_org):
        data = calendar_org
        resp = data["other_admin_client"].post(
            f"{data['api_base']}/calendar/reset-token",
            params={"person_id": data["vol_id"]},
        )
        assert resp.status_code == 403


class TestAdminReset:
    """POST /calendar/{person_id}/admin-reset — admin-only forced rotate."""

    def test_admin_rotates_other_user_token(self, calendar_org):
        data = calendar_org
        first = data["admin_client"].get(
            f"{data['api_base']}/calendar/subscribe",
            params={"person_id": data["vol_id"]},
        )
        assert first.status_code == 200
        old_token = first.json()["token"]

        resp = data["admin_client"].post(
            f"{data['api_base']}/calendar/{data['vol_id']}/admin-reset"
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["token"] != old_token

    def test_volunteer_cannot_admin_reset(self, calendar_org):
        data = calendar_org
        resp = data["vol_client"].post(
            f"{data['api_base']}/calendar/{data['admin_id']}/admin-reset"
        )
        assert resp.status_code == 403

    def test_cross_org_admin_forbidden(self, calendar_org):
        data = calendar_org
        resp = data["other_admin_client"].post(
            f"{data['api_base']}/calendar/{data['vol_id']}/admin-reset"
        )
        assert resp.status_code == 403


class TestCalendarFeed:
    """GET /calendar/feed/{token} — public ICS by token."""

    def test_feed_returns_ics_for_valid_token(self, calendar_org):
        data = calendar_org
        _create_event_and_assign(data, data["vol_id"])
        sub = data["vol_client"].get(
            f"{data['api_base']}/calendar/subscribe",
            params={"person_id": data["vol_id"]},
        )
        assert sub.status_code == 200
        token = sub.json()["token"]

        anon = httpx.Client()
        try:
            resp = anon.get(f"{data['api_base']}/calendar/feed/{token}")
        finally:
            anon.close()
        assert resp.status_code == 200, resp.text
        assert resp.headers["content-type"].startswith("text/calendar")
        assert "BEGIN:VCALENDAR" in resp.text
        assert "END:VCALENDAR" in resp.text

    def test_feed_bogus_token_404(self, calendar_org):
        data = calendar_org
        anon = httpx.Client()
        try:
            resp = anon.get(f"{data['api_base']}/calendar/feed/nope_{int(time.time())}")
        finally:
            anon.close()
        assert resp.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
