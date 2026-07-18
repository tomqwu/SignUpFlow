#!/usr/bin/env python3
"""Integration tests: recurring events router (Sprint 4 PR 4.6b).

Tests the /api/v1/recurring-series endpoints over real HTTP against the
session-scoped uvicorn api_server:
- POST /recurring-series             - Create + generate occurrences (admin)
- POST /recurring-series/preview     - Dry-run pattern preview
- GET  /recurring-series             - List (envelope, org-scoped, active_only)
- GET  /recurring-series/{id}        - Get one
- GET  /recurring-series/{id}/occurrences - List series occurrences
- PUT  /recurring-series/{id}        - Update template (admin)
- DELETE /recurring-series/{id}      - Cascade delete (admin)
"""

import random
import time
from datetime import date, timedelta

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


@pytest.fixture
def recurring_org(api_server, api_base):
    marker = _unique("recurring_org")
    org_id = marker
    admin_email = f"admin_{marker}@test.com"
    vol_email = f"vol_{marker}@test.com"

    bootstrap = httpx.Client()
    org_resp = bootstrap.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"Recurring Setup {marker}", "region": "US", "config": {}},
    )
    assert org_resp.status_code == 201, org_resp.text

    admin_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Recurring Admin",
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
            "name": "Recurring Volunteer",
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
        "admin_client": admin_client,
        "vol_client": vol_client,
        "api_base": api_base,
    }

    admin_client.close()
    vol_client.close()


def _series_payload(count: int = 4, days_out: int = 14) -> dict:
    """Weekly Monday series with a fixed occurrence count."""
    start = date.today() + timedelta(days=days_out)
    return {
        "title": f"Sunday Service {_unique('s')}",
        "duration": 90,
        "location": "Sanctuary",
        "role_requirements": None,
        "pattern_type": "weekly",
        "frequency_interval": 1,
        "selected_days": ["monday"],
        "start_date": start.isoformat(),
        "start_time": "10:00:00",
        "end_condition_type": "count",
        "occurrence_count": count,
    }


class TestCreateRecurringSeries:
    """POST /recurring-series/ — admin-only creation."""

    def test_create_success(self, recurring_org):
        data = recurring_org
        payload = _series_payload(count=4)
        resp = data["admin_client"].post(
            f"{data['api_base']}/recurring-series",
            params={"org_id": data["org_id"]},
            json=payload,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["org_id"] == data["org_id"]
        assert body["title"] == payload["title"]
        assert body["occurrence_count"] == 4
        # Router computes preview count from generated Events
        assert body["occurrence_preview_count"] == 4

    def test_create_requires_admin(self, recurring_org):
        data = recurring_org
        resp = data["vol_client"].post(
            f"{data['api_base']}/recurring-series",
            params={"org_id": data["org_id"]},
            json=_series_payload(),
        )
        assert resp.status_code == 403

    def test_create_cross_org_rejected(self, recurring_org):
        data = recurring_org
        resp = data["admin_client"].post(
            f"{data['api_base']}/recurring-series",
            params={"org_id": f"other_{int(time.time())}"},
            json=_series_payload(),
        )
        assert resp.status_code == 403


class TestPreviewOccurrences:
    """POST /recurring-series/preview — dry-run pattern preview."""

    def test_preview_returns_occurrences(self, recurring_org):
        data = recurring_org
        payload = {
            "pattern_type": "weekly",
            "selected_days": ["monday"],
            "frequency_interval": 1,
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "start_time": "10:00:00",
            "duration": 90,
            "end_condition_type": "count",
            "occurrence_count": 3,
        }
        resp = data["admin_client"].post(
            f"{data['api_base']}/recurring-series/preview",
            params={"org_id": data["org_id"]},
            json=payload,
        )
        assert resp.status_code == 200, resp.text
        occurrences = resp.json()
        assert isinstance(occurrences, list)
        assert len(occurrences) == 3
        assert occurrences[0]["occurrence_sequence"] == 1

    def test_preview_volunteer_can_call(self, recurring_org):
        data = recurring_org
        payload = {
            "pattern_type": "weekly",
            "selected_days": ["monday"],
            "frequency_interval": 1,
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "start_time": "10:00:00",
            "duration": 90,
            "end_condition_type": "count",
            "occurrence_count": 2,
        }
        resp = data["vol_client"].post(
            f"{data['api_base']}/recurring-series/preview",
            params={"org_id": data["org_id"]},
            json=payload,
        )
        assert resp.status_code == 200


class TestListAndGetSeries:
    """GET /recurring-series and GET /recurring-series/{id}."""

    def test_list_envelope(self, recurring_org):
        data = recurring_org
        # Create a series so the list has content
        create_resp = data["admin_client"].post(
            f"{data['api_base']}/recurring-series",
            params={"org_id": data["org_id"]},
            json=_series_payload(count=2),
        )
        assert create_resp.status_code == 200, create_resp.text

        resp = data["admin_client"].get(
            f"{data['api_base']}/recurring-series",
            params={"org_id": data["org_id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        assert body["total"] >= 1
        assert all(s["org_id"] == data["org_id"] for s in body["items"])

    def test_list_cross_org_rejected(self, recurring_org):
        data = recurring_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/recurring-series",
            params={"org_id": f"other_{int(time.time())}"},
        )
        assert resp.status_code == 403

    def test_get_existing(self, recurring_org):
        data = recurring_org
        create_resp = data["admin_client"].post(
            f"{data['api_base']}/recurring-series",
            params={"org_id": data["org_id"]},
            json=_series_payload(count=2),
        )
        assert create_resp.status_code == 200
        series_id = create_resp.json()["id"]

        resp = data["admin_client"].get(f"{data['api_base']}/recurring-series/{series_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == series_id

    def test_get_missing_returns_404(self, recurring_org):
        data = recurring_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/recurring-series/nope_{int(time.time())}"
        )
        assert resp.status_code == 404


class TestSeriesOccurrences:
    """GET /recurring-series/{id}/occurrences — enumerate generated events."""

    def test_occurrences_listed_in_sequence(self, recurring_org):
        data = recurring_org
        create_resp = data["admin_client"].post(
            f"{data['api_base']}/recurring-series",
            params={"org_id": data["org_id"]},
            json=_series_payload(count=3),
        )
        assert create_resp.status_code == 200
        series_id = create_resp.json()["id"]

        resp = data["admin_client"].get(
            f"{data['api_base']}/recurring-series/{series_id}/occurrences"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["series_id"] == series_id
        assert body["occurrence_count"] == 3
        seq = [o["occurrence_sequence"] for o in body["occurrences"]]
        assert seq == sorted(seq)


class TestUpdateSeries:
    """PUT /recurring-series/{id} — admin-only template update."""

    def test_update_title_and_location(self, recurring_org):
        data = recurring_org
        create_resp = data["admin_client"].post(
            f"{data['api_base']}/recurring-series",
            params={"org_id": data["org_id"]},
            json=_series_payload(count=2),
        )
        assert create_resp.status_code == 200
        series_id = create_resp.json()["id"]

        resp = data["admin_client"].put(
            f"{data['api_base']}/recurring-series/{series_id}",
            params={"title": "Renamed", "location": "New Room"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "Renamed"
        assert body["location"] == "New Room"

    def test_update_requires_admin(self, recurring_org):
        data = recurring_org
        create_resp = data["admin_client"].post(
            f"{data['api_base']}/recurring-series",
            params={"org_id": data["org_id"]},
            json=_series_payload(count=2),
        )
        assert create_resp.status_code == 200
        series_id = create_resp.json()["id"]

        resp = data["vol_client"].put(
            f"{data['api_base']}/recurring-series/{series_id}",
            params={"title": "wont"},
        )
        assert resp.status_code == 403

    def test_update_missing_returns_404(self, recurring_org):
        data = recurring_org
        resp = data["admin_client"].put(
            f"{data['api_base']}/recurring-series/nope_{int(time.time())}",
            params={"title": "ghost"},
        )
        assert resp.status_code == 404


class TestDeleteSeries:
    """DELETE /recurring-series/{id} — admin cascade delete."""

    def test_delete_removes_series_and_occurrences(self, recurring_org):
        data = recurring_org
        create_resp = data["admin_client"].post(
            f"{data['api_base']}/recurring-series",
            params={"org_id": data["org_id"]},
            json=_series_payload(count=3),
        )
        assert create_resp.status_code == 200
        series_id = create_resp.json()["id"]

        resp = data["admin_client"].delete(f"{data['api_base']}/recurring-series/{series_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["series_id"] == series_id
        assert body["occurrences_deleted"] == 3

        follow = data["admin_client"].get(f"{data['api_base']}/recurring-series/{series_id}")
        assert follow.status_code == 404

    def test_delete_requires_admin(self, recurring_org):
        data = recurring_org
        create_resp = data["admin_client"].post(
            f"{data['api_base']}/recurring-series",
            params={"org_id": data["org_id"]},
            json=_series_payload(count=2),
        )
        assert create_resp.status_code == 200
        series_id = create_resp.json()["id"]

        resp = data["vol_client"].delete(f"{data['api_base']}/recurring-series/{series_id}")
        assert resp.status_code == 403

    def test_delete_missing_returns_404(self, recurring_org):
        data = recurring_org
        resp = data["admin_client"].delete(
            f"{data['api_base']}/recurring-series/nope_{int(time.time())}"
        )
        assert resp.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
