"""Tests for /availability/{person_id}/rrule CRUD (Sprint 8 PR 8.3).

Single rrule per person. Mobile renders this as a friendly preset picker
("Every Monday", "Every other Friday", "Custom rrule…") that produces an
iCalendar RRULE string the solver already understands.
"""

import pytest

from tests.api.conftest import seed_org, seed_user

PERSON_PW = "VolPass1!"


def _person_for(client, org_id: str, suffix: str) -> str:
    resp = seed_user(
        client,
        org_id,
        email=f"vol-{suffix}@o.org",
        name="Vol",
        password=PERSON_PW,
    )
    return resp["person_id"]


@pytest.mark.no_mock_auth
class TestAvailabilityRrule:
    def test_get_when_no_availability_row_returns_null(self, client):
        org_id = "rr-empty"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "e")
        resp = client.get(f"/api/v1/availability/{person_id}/rrule")
        assert resp.status_code == 200, resp.text
        assert resp.json() == {"rrule": None}

    def test_put_sets_rrule_and_get_returns_it(self, client):
        org_id = "rr-set"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "s")

        put_resp = client.put(
            f"/api/v1/availability/{person_id}/rrule",
            json={"rrule": "FREQ=WEEKLY;BYDAY=MO"},
        )
        assert put_resp.status_code == 200, put_resp.text
        assert put_resp.json() == {"rrule": "FREQ=WEEKLY;BYDAY=MO"}

        get_resp = client.get(f"/api/v1/availability/{person_id}/rrule")
        assert get_resp.json() == {"rrule": "FREQ=WEEKLY;BYDAY=MO"}

    def test_put_replaces_existing_rrule(self, client):
        org_id = "rr-replace"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "r")

        client.put(
            f"/api/v1/availability/{person_id}/rrule",
            json={"rrule": "FREQ=WEEKLY;BYDAY=MO"},
        )
        client.put(
            f"/api/v1/availability/{person_id}/rrule",
            json={"rrule": "FREQ=WEEKLY;BYDAY=FR"},
        )
        resp = client.get(f"/api/v1/availability/{person_id}/rrule")
        assert resp.json() == {"rrule": "FREQ=WEEKLY;BYDAY=FR"}

    def test_delete_clears_rrule(self, client):
        org_id = "rr-clear"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "c")

        client.put(
            f"/api/v1/availability/{person_id}/rrule",
            json={"rrule": "FREQ=WEEKLY;BYDAY=MO"},
        )
        del_resp = client.delete(f"/api/v1/availability/{person_id}/rrule")
        assert del_resp.status_code == 204

        get_resp = client.get(f"/api/v1/availability/{person_id}/rrule")
        assert get_resp.json() == {"rrule": None}

    def test_delete_when_never_set_is_idempotent(self, client):
        org_id = "rr-idempo"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "i")
        resp = client.delete(f"/api/v1/availability/{person_id}/rrule")
        assert resp.status_code == 204

    def test_put_for_unknown_person_returns_404(self, client):
        org_id = "rr-noperson"
        seed_org(client, org_id)
        _person_for(client, org_id, "n")
        resp = client.put(
            "/api/v1/availability/person_does_not_exist/rrule",
            json={"rrule": "FREQ=WEEKLY"},
        )
        assert resp.status_code == 404

    def test_put_empty_string_rejected(self, client):
        org_id = "rr-validation"
        seed_org(client, org_id)
        person_id = _person_for(client, org_id, "v")
        resp = client.put(
            f"/api/v1/availability/{person_id}/rrule",
            json={"rrule": ""},
        )
        assert resp.status_code == 422
