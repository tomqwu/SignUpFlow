"""Tests for /availability/{person_id}/exceptions CRUD (Sprint 8 PR 8.2).

Single-date availability exceptions are already consumed by the solver via
the ``AvailabilityException`` model. This PR adds a tiny CRUD surface so the
mobile Availability screen can let volunteers manage them directly.
"""

import pytest

from tests.api.conftest import seed_org, seed_user

PERSON_PW = "VolPass1!"


def _person_for(client, org_id: str, suffix: str) -> str:
    """Sign up a volunteer and return their person_id (which is also auth subject)."""
    resp = seed_user(
        client,
        org_id,
        email=f"vol-{suffix}@o.org",
        name="Vol",
        password=PERSON_PW,
    )
    return resp["person_id"]


@pytest.mark.no_mock_auth
class TestAvailabilityExceptions:
    def test_list_empty_returns_empty_list(self, client):
        org_id = "ax-empty"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "e")
        resp = client.get(f"/api/v1/availability/{person_id}/exceptions")
        assert resp.status_code == 200, resp.text
        assert resp.json() == []

    def test_post_creates_exception(self, client):
        org_id = "ax-create"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "c")

        resp = client.post(
            f"/api/v1/availability/{person_id}/exceptions",
            json={"exception_date": "2026-12-25"},
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["exception_date"] == "2026-12-25"
        assert "id" in body

        # GET reflects the new row.
        listed = client.get(f"/api/v1/availability/{person_id}/exceptions")
        assert listed.status_code == 200
        assert len(listed.json()) == 1
        assert listed.json()[0]["exception_date"] == "2026-12-25"

    def test_post_same_date_is_idempotent(self, client):
        org_id = "ax-idempo"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "i")

        first = client.post(
            f"/api/v1/availability/{person_id}/exceptions",
            json={"exception_date": "2026-07-04"},
        )
        second = client.post(
            f"/api/v1/availability/{person_id}/exceptions",
            json={"exception_date": "2026-07-04"},
        )
        assert first.status_code == 201
        # Second POST returns the same row (Pydantic doesn't change the
        # status_code we declared, so it's still 201 — but the id matches).
        assert second.json()["id"] == first.json()["id"]
        listed = client.get(f"/api/v1/availability/{person_id}/exceptions")
        assert len(listed.json()) == 1

    def test_delete_removes_exception(self, client):
        org_id = "ax-del"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "d")

        created = client.post(
            f"/api/v1/availability/{person_id}/exceptions",
            json={"exception_date": "2026-03-15"},
        )
        ex_id = created.json()["id"]

        deleted = client.delete(f"/api/v1/availability/{person_id}/exceptions/{ex_id}")
        assert deleted.status_code == 204

        listed = client.get(f"/api/v1/availability/{person_id}/exceptions")
        assert listed.json() == []

    def test_delete_unknown_returns_404(self, client):
        org_id = "ax-404"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "n")
        resp = client.delete(f"/api/v1/availability/{person_id}/exceptions/999999")
        assert resp.status_code == 404

    def test_post_for_unknown_person_returns_404(self, client):
        org_id = "ax-noperson"
        seed_org(client, org_id)
        _person_for(client, org_id, "p")  # unrelated, just to land an org
        resp = client.post(
            "/api/v1/availability/person_does_not_exist/exceptions",
            json={"exception_date": "2026-01-01"},
        )
        assert resp.status_code == 404
