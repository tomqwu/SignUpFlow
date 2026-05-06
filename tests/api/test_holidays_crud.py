"""Tests for /api/v1/holidays/ — admin-managed dates with bulk import."""

from datetime import date, timedelta

import pytest

from api.models import AuditAction, AuditLog
from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin(client, org_id: str, suffix: str):
    seed_user(
        client,
        org_id,
        email=f"admin-{suffix}@h.org",
        name="Admin",
        password="AdminPass1!",
    )
    return auth_headers(client, email=f"admin-{suffix}@h.org", password="AdminPass1!")


@pytest.mark.no_mock_auth
class TestHolidayCrud:
    def test_admin_creates_holiday(self, client, db):
        org = "hol-create"
        seed_org(client, org)
        hdrs = _admin(client, org, "create")

        resp = client.post(
            "/api/v1/holidays/",
            json={
                "org_id": org,
                "date": "2026-12-25",
                "label": "Christmas Day",
                "is_long_weekend": False,
            },
            headers=hdrs,
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["label"] == "Christmas Day"
        assert body["org_id"] == org

    def test_volunteer_cannot_create(self, client, db):
        org = "hol-vol"
        seed_org(client, org)
        _admin(client, org, "vol-admin")
        seed_user(
            client,
            org,
            email="vol@h.org",
            name="Vol",
            password="VolPass1!",
            roles=["volunteer"],
        )
        vol_hdrs = auth_headers(client, email="vol@h.org", password="VolPass1!")

        resp = client.post(
            "/api/v1/holidays/",
            json={"org_id": org, "date": "2026-07-04", "label": "July 4"},
            headers=vol_hdrs,
        )
        assert resp.status_code == 403

    def test_admin_cross_org_blocked(self, client, db):
        seed_org(client, "hol-a")
        seed_org(client, "hol-b")
        a_hdrs = _admin(client, "hol-a", "a")

        resp = client.post(
            "/api/v1/holidays/",
            json={"org_id": "hol-b", "date": "2026-01-01", "label": "New Year"},
            headers=a_hdrs,
        )
        assert resp.status_code == 403

    def test_list_returns_envelope(self, client, db):
        org = "hol-list"
        seed_org(client, org)
        hdrs = _admin(client, org, "list")
        for d, label in [("2026-01-01", "New Year"), ("2026-07-04", "July 4")]:
            client.post(
                "/api/v1/holidays/",
                json={"org_id": org, "date": d, "label": label},
                headers=hdrs,
            )

        resp = client.get(f"/api/v1/holidays/?org_id={org}", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 2
        assert {"items", "total", "limit", "offset"} <= set(body.keys())

    def test_get_update_delete(self, client, db):
        org = "hol-cycle"
        seed_org(client, org)
        hdrs = _admin(client, org, "cycle")
        created = client.post(
            "/api/v1/holidays/",
            json={"org_id": org, "date": "2026-11-26", "label": "Thanksgiving"},
            headers=hdrs,
        ).json()
        hid = created["id"]

        # GET by id
        assert client.get(f"/api/v1/holidays/{hid}", headers=hdrs).status_code == 200

        # PUT
        upd = client.put(
            f"/api/v1/holidays/{hid}",
            json={"is_long_weekend": True},
            headers=hdrs,
        )
        assert upd.status_code == 200
        assert upd.json()["is_long_weekend"] is True

        # DELETE
        delete = client.delete(f"/api/v1/holidays/{hid}", headers=hdrs)
        assert delete.status_code in (200, 204)
        assert client.get(f"/api/v1/holidays/{hid}", headers=hdrs).status_code == 404


@pytest.mark.no_mock_auth
class TestHolidayBulkImport:
    def test_bulk_creates_multiple(self, client, db):
        org = "hol-bulk"
        seed_org(client, org)
        hdrs = _admin(client, org, "bulk")

        items = [
            {
                "date": (date(2026, 1, 1) + timedelta(days=i * 30)).isoformat(),
                "label": f"Holiday {i}",
            }
            for i in range(5)
        ]
        resp = client.post(
            f"/api/v1/holidays/bulk?org_id={org}",
            json={"items": items},
            headers=hdrs,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["created"] == 5
        assert body["skipped"] == 0
        assert body["errors"] == []

    def test_bulk_partial_failure_on_duplicate_date(self, client, db):
        org = "hol-bulk-dup"
        seed_org(client, org)
        hdrs = _admin(client, org, "bulk-dup")
        # Pre-create one
        client.post(
            "/api/v1/holidays/",
            json={"org_id": org, "date": "2026-12-25", "label": "Christmas"},
            headers=hdrs,
        )

        resp = client.post(
            f"/api/v1/holidays/bulk?org_id={org}",
            json={
                "items": [
                    {"date": "2026-12-25", "label": "Xmas dup"},  # already exists
                    {"date": "2026-12-31", "label": "NYE"},
                ]
            },
            headers=hdrs,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["created"] == 1
        assert body["skipped"] == 1
        assert any("already exists" in e["message"] for e in body["errors"])

    def test_bulk_volunteer_403(self, client, db):
        org = "hol-bulk-vol"
        seed_org(client, org)
        _admin(client, org, "bulk-vol-admin")
        seed_user(
            client,
            org,
            email="vol-bulk@h.org",
            name="Vol",
            password="VolPass1!",
            roles=["volunteer"],
        )
        vol_hdrs = auth_headers(client, email="vol-bulk@h.org", password="VolPass1!")

        resp = client.post(
            f"/api/v1/holidays/bulk?org_id={org}",
            json={"items": [{"date": "2026-01-01", "label": "X"}]},
            headers=vol_hdrs,
        )
        assert resp.status_code == 403

    def test_bulk_audit_row_written(self, client, db):
        org = "hol-bulk-audit"
        seed_org(client, org)
        hdrs = _admin(client, org, "bulk-audit")

        before = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.HOLIDAY_BULK_IMPORTED).count()
        )
        client.post(
            f"/api/v1/holidays/bulk?org_id={org}",
            json={"items": [{"date": "2026-01-01", "label": "New Year"}]},
            headers=hdrs,
        )
        after = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.HOLIDAY_BULK_IMPORTED).count()
        )
        assert after == before + 1
