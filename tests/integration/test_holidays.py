#!/usr/bin/env python3
"""Integration tests: holidays router (Sprint 4 PR 4.6b).

Tests the /api/v1/holidays endpoints over real HTTP against the
session-scoped uvicorn api_server:
- POST   /holidays/              - Create (admin)
- POST   /holidays/bulk          - Bulk import (admin, audited)
- GET    /holidays/              - List (envelope, org-scoped)
- GET    /holidays/{holiday_id}  - Get one
- PUT    /holidays/{holiday_id}  - Update (admin)
- DELETE /holidays/{holiday_id}  - Delete (admin)
"""

import random
import time
from datetime import date, timedelta

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


@pytest.fixture
def holidays_org(api_server, api_base):
    """Create an org + admin + one volunteer; return authed clients + ids."""
    marker = _unique("holidays_org")
    org_id = marker
    admin_email = f"admin_{marker}@test.com"
    vol_email = f"vol_{marker}@test.com"

    bootstrap = httpx.Client()

    org_resp = bootstrap.post(
        f"{api_base}/organizations/",
        json={"id": org_id, "name": f"Holidays Setup {marker}", "region": "US", "config": {}},
    )
    assert org_resp.status_code == 201, org_resp.text

    admin_resp = bootstrap.post(
        f"{api_base}/auth/signup",
        json={
            "org_id": org_id,
            "name": "Holiday Admin",
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
            "name": "Holiday Volunteer",
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


def _future_date(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def _create_holiday(client, api_base, org_id, *, offset_days: int = 60, label: str = "Fed") -> dict:
    resp = client.post(
        f"{api_base}/holidays/",
        json={
            "org_id": org_id,
            "date": _future_date(offset_days),
            "label": f"{label} {_unique('h')}",
            "is_long_weekend": False,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


class TestCreateHoliday:
    """POST /holidays/ — admin-only creation."""

    def test_create_success(self, holidays_org):
        data = holidays_org
        h = _create_holiday(data["admin_client"], data["api_base"], data["org_id"])
        assert h["org_id"] == data["org_id"]
        assert "label" in h and h["label"].startswith("Fed ")
        assert h["is_long_weekend"] is False
        assert isinstance(h["id"], int)

    def test_create_requires_admin(self, holidays_org):
        data = holidays_org
        resp = data["vol_client"].post(
            f"{data['api_base']}/holidays/",
            json={
                "org_id": data["org_id"],
                "date": _future_date(70),
                "label": "Nope",
                "is_long_weekend": False,
            },
        )
        assert resp.status_code == 403

    def test_create_cross_org_rejected(self, holidays_org):
        data = holidays_org
        resp = data["admin_client"].post(
            f"{data['api_base']}/holidays/",
            json={
                "org_id": f"other_{int(time.time())}",
                "date": _future_date(80),
                "label": "Orphan",
                "is_long_weekend": False,
            },
        )
        # verify_org_member fires first (403); if bypassed, org lookup 404s.
        assert resp.status_code in (403, 404)


class TestBulkImport:
    """POST /holidays/bulk — admin-only batch create."""

    def test_bulk_import_success(self, holidays_org):
        data = holidays_org
        payload = {
            "items": [
                {
                    "date": _future_date(100 + i),
                    "label": f"Bulk {i} {_unique('b')}",
                    "is_long_weekend": False,
                }
                for i in range(3)
            ]
        }
        resp = data["admin_client"].post(
            f"{data['api_base']}/holidays/bulk",
            params={"org_id": data["org_id"]},
            json=payload,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["created"] == 3
        assert body["skipped"] == 0
        assert body["errors"] == []

    def test_bulk_import_dedupes_within_batch(self, holidays_org):
        data = holidays_org
        dup_date = _future_date(150)
        payload = {
            "items": [
                {"date": dup_date, "label": "First", "is_long_weekend": False},
                {"date": dup_date, "label": "Duplicate", "is_long_weekend": False},
            ]
        }
        resp = data["admin_client"].post(
            f"{data['api_base']}/holidays/bulk",
            params={"org_id": data["org_id"]},
            json=payload,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["created"] == 1
        assert body["skipped"] == 1
        assert len(body["errors"]) == 1
        assert body["errors"][0]["row"] == 1

    def test_bulk_import_requires_admin(self, holidays_org):
        data = holidays_org
        resp = data["vol_client"].post(
            f"{data['api_base']}/holidays/bulk",
            params={"org_id": data["org_id"]},
            json={"items": [{"date": _future_date(200), "label": "X"}]},
        )
        assert resp.status_code == 403


class TestListAndGet:
    """GET /holidays/ and GET /holidays/{id}."""

    def test_list_envelope_and_scoping(self, holidays_org):
        data = holidays_org
        _create_holiday(data["admin_client"], data["api_base"], data["org_id"])

        resp = data["admin_client"].get(
            f"{data['api_base']}/holidays/",
            params={"org_id": data["org_id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body.keys()) >= {"items", "total", "limit", "offset"}
        assert all(h["org_id"] == data["org_id"] for h in body["items"])

    def test_list_volunteer_can_read(self, holidays_org):
        data = holidays_org
        _create_holiday(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["vol_client"].get(
            f"{data['api_base']}/holidays/",
            params={"org_id": data["org_id"]},
        )
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_list_cross_org_rejected(self, holidays_org):
        data = holidays_org
        resp = data["admin_client"].get(
            f"{data['api_base']}/holidays/",
            params={"org_id": f"other_{int(time.time())}"},
        )
        assert resp.status_code == 403

    def test_get_existing(self, holidays_org):
        data = holidays_org
        h = _create_holiday(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["admin_client"].get(f"{data['api_base']}/holidays/{h['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == h["id"]

    def test_get_missing_returns_404(self, holidays_org):
        data = holidays_org
        resp = data["admin_client"].get(f"{data['api_base']}/holidays/999999999")
        assert resp.status_code == 404


class TestUpdateHoliday:
    """PUT /holidays/{id} — admin-only update."""

    def test_update_label(self, holidays_org):
        data = holidays_org
        h = _create_holiday(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["admin_client"].put(
            f"{data['api_base']}/holidays/{h['id']}",
            json={"label": "Renamed Holiday"},
        )
        assert resp.status_code == 200
        assert resp.json()["label"] == "Renamed Holiday"

    def test_update_requires_admin(self, holidays_org):
        data = holidays_org
        h = _create_holiday(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["vol_client"].put(
            f"{data['api_base']}/holidays/{h['id']}",
            json={"label": "wont"},
        )
        assert resp.status_code == 403

    def test_update_missing_returns_404(self, holidays_org):
        data = holidays_org
        resp = data["admin_client"].put(
            f"{data['api_base']}/holidays/999999999",
            json={"label": "ghost"},
        )
        assert resp.status_code == 404


class TestDeleteHoliday:
    """DELETE /holidays/{id}."""

    def test_delete_removes_holiday(self, holidays_org):
        data = holidays_org
        h = _create_holiday(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["admin_client"].delete(f"{data['api_base']}/holidays/{h['id']}")
        assert resp.status_code == 204
        follow = data["admin_client"].get(f"{data['api_base']}/holidays/{h['id']}")
        assert follow.status_code == 404

    def test_delete_requires_admin(self, holidays_org):
        data = holidays_org
        h = _create_holiday(data["admin_client"], data["api_base"], data["org_id"])
        resp = data["vol_client"].delete(f"{data['api_base']}/holidays/{h['id']}")
        assert resp.status_code == 403

    def test_delete_missing_returns_404(self, holidays_org):
        data = holidays_org
        resp = data["admin_client"].delete(f"{data['api_base']}/holidays/999999999")
        assert resp.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
