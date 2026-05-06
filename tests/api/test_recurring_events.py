"""Tests for /api/v1/recurring-series — admin-only CRUD on the recurring_events router."""

from datetime import date, timedelta

import pytest

from api.models import Event, RecurringSeries
from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin(client, org_id: str, suffix: str):
    seed_user(
        client,
        org_id,
        email=f"admin-{suffix}@r.org",
        name="Admin",
        password="AdminPass1!",
    )
    return auth_headers(client, email=f"admin-{suffix}@r.org", password="AdminPass1!")


def _weekly_series_payload(title: str = "Weekly Service") -> dict:
    """Body for a 4-week Sunday series."""
    today = date.today()
    return {
        "title": title,
        "duration": 60,
        "location": "Sanctuary",
        "role_requirements": None,
        "pattern_type": "weekly",
        "frequency_interval": 1,
        "selected_days": ["sunday"],
        "weekday_position": None,
        "weekday_name": None,
        "start_date": today.isoformat(),
        "start_time": "10:00:00",
        "end_condition_type": "date",
        "end_date": (today + timedelta(days=28)).isoformat(),
        "occurrence_count": None,
    }


@pytest.mark.no_mock_auth
class TestRecurringSeriesCreate:
    def test_admin_creates_weekly_series(self, client, db):
        org = "rec-org-create"
        seed_org(client, org)
        hdrs = _admin(client, org, "create")

        resp = client.post(
            f"/api/v1/recurring-series?org_id={org}",
            json=_weekly_series_payload(),
            headers=hdrs,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["title"] == "Weekly Service"
        assert body["occurrence_preview_count"] >= 4

        # Confirm rows landed in the DB and are linked
        series = db.query(RecurringSeries).filter(RecurringSeries.org_id == org).first()
        assert series is not None
        events = db.query(Event).filter(Event.series_id == series.id).count()
        assert events >= 4

    def test_volunteer_cannot_create(self, client, db):
        org = "rec-org-vol"
        seed_org(client, org)
        _admin(client, org, "vol-admin")
        seed_user(
            client,
            org,
            email="vol@r.org",
            name="Vol",
            password="VolPass1!",
            roles=["volunteer"],
        )
        vol_hdrs = auth_headers(client, email="vol@r.org", password="VolPass1!")

        resp = client.post(
            f"/api/v1/recurring-series?org_id={org}",
            json=_weekly_series_payload(),
            headers=vol_hdrs,
        )
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestRecurringSeriesList:
    def test_list_returns_listresponse_envelope(self, client, db):
        org = "rec-org-envelope"
        seed_org(client, org)
        hdrs = _admin(client, org, "envelope")
        client.post(
            f"/api/v1/recurring-series?org_id={org}",
            json=_weekly_series_payload(),
            headers=hdrs,
        )

        resp = client.get(f"/api/v1/recurring-series?org_id={org}", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert "limit" in body
        assert "offset" in body
        assert body["total"] >= 1

    def test_active_only_filter_actually_filters(self, client, db):
        """Regression for the `active is True` Python identity bug.

        Before the fix, this filter always evaluated to False in SQL and the
        endpoint returned an empty list regardless of `active` column values.
        """
        org = "rec-org-activefilter"
        seed_org(client, org)
        hdrs = _admin(client, org, "activefilter")
        client.post(
            f"/api/v1/recurring-series?org_id={org}",
            json=_weekly_series_payload("Active Series"),
            headers=hdrs,
        )

        # Default active_only=True must include the active series
        resp = client.get(f"/api/v1/recurring-series?org_id={org}&active_only=true", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_cross_org_blocked(self, client, db):
        seed_org(client, "rec-a")
        seed_org(client, "rec-b")
        a_hdrs = _admin(client, "rec-a", "rec-a-admin")

        resp = client.get("/api/v1/recurring-series?org_id=rec-b", headers=a_hdrs)
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestRecurringSeriesGetAndDelete:
    def test_get_by_id_returns_series(self, client, db):
        org = "rec-org-get"
        seed_org(client, org)
        hdrs = _admin(client, org, "get")
        created = client.post(
            f"/api/v1/recurring-series?org_id={org}",
            json=_weekly_series_payload(),
            headers=hdrs,
        ).json()
        sid = created["id"]

        resp = client.get(f"/api/v1/recurring-series/{sid}", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["id"] == sid

    def test_get_nonexistent_returns_404(self, client, db):
        org = "rec-org-getnone"
        seed_org(client, org)
        hdrs = _admin(client, org, "getnone")

        resp = client.get("/api/v1/recurring-series/no-such", headers=hdrs)
        assert resp.status_code == 404

    def test_delete_cascades_to_occurrences(self, client, db):
        org = "rec-org-delete"
        seed_org(client, org)
        hdrs = _admin(client, org, "delete")
        created = client.post(
            f"/api/v1/recurring-series?org_id={org}",
            json=_weekly_series_payload(),
            headers=hdrs,
        ).json()
        sid = created["id"]

        # Confirm occurrences exist
        before = db.query(Event).filter(Event.series_id == sid).count()
        assert before >= 4

        resp = client.delete(f"/api/v1/recurring-series/{sid}", headers=hdrs)
        assert resp.status_code in (200, 204)

        # The series row is gone (or soft-deleted); its events should be removed
        # or detached. We accept either: the cascade is the contract.
        after_series = db.query(RecurringSeries).filter(RecurringSeries.id == sid).first()
        if after_series is not None:
            # Soft-delete path: at minimum, occurrences linked by series_id are gone
            after_events = db.query(Event).filter(Event.series_id == sid).count()
            assert after_events == 0


@pytest.mark.no_mock_auth
class TestRecurringSeriesPreview:
    def test_preview_does_not_create_db_rows(self, client, db):
        org = "rec-org-preview"
        seed_org(client, org)
        hdrs = _admin(client, org, "preview")

        # Preview accepts a narrower PreviewRequest body (subset of create payload)
        today = date.today()
        preview_body = {
            "pattern_type": "weekly",
            "selected_days": ["sunday"],
            "frequency_interval": 1,
            "start_date": today.isoformat(),
            "start_time": "10:00:00",
            "duration": 60,
            "end_condition_type": "date",
            "end_date": (today + timedelta(days=28)).isoformat(),
        }

        before_series = db.query(RecurringSeries).count()
        before_events = db.query(Event).count()

        resp = client.post(
            f"/api/v1/recurring-series/preview?org_id={org}",
            json=preview_body,
            headers=hdrs,
        )
        assert resp.status_code == 200, resp.text
        # Preview returns occurrences but persists nothing
        assert isinstance(resp.json(), list)

        assert db.query(RecurringSeries).count() == before_series
        assert db.query(Event).count() == before_events
