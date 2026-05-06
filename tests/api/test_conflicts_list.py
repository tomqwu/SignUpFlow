"""Tests for GET /api/v1/conflicts/ — admin-only conflict listing."""

import pytest

from tests.api.conftest import auth_headers, seed_event, seed_org, seed_user


def _two_overlapping_events(client, suffix: str):
    """Create org+admin+volunteer; assign volunteer to two overlapping events."""
    org_id = f"conflicts-list-org-{suffix}"
    seed_org(client, org_id)
    seed_user(client, org_id, email=f"admin-{suffix}@cl.org", name="Admin", password="AdminPass1!")
    vol = seed_user(
        client,
        org_id,
        email=f"vol-{suffix}@cl.org",
        name="Vol",
        password="VolPass1!",
        roles=["volunteer"],
    )
    admin_hdrs = auth_headers(client, email=f"admin-{suffix}@cl.org", password="AdminPass1!")
    ev_a = seed_event(client, admin_hdrs, org_id, event_id=f"evt-a-{suffix}")
    ev_b = seed_event(client, admin_hdrs, org_id, event_id=f"evt-b-{suffix}")
    # Assign volunteer to both
    for ev in (ev_a, ev_b):
        client.post(
            f"/api/v1/events/{ev['id']}/assignments",
            json={"person_id": vol["person_id"], "action": "assign", "role": "u"},
            headers=admin_hdrs,
        )
    return org_id, admin_hdrs, vol


@pytest.mark.no_mock_auth
class TestListConflictsAuth:
    def test_volunteer_cannot_list_org_conflicts(self, client, db):
        org_id = "list-conflicts-vol"
        seed_org(client, org_id)
        seed_user(client, org_id, email="admin@lc.org", name="Admin", password="AdminPass1!")
        seed_user(
            client,
            org_id,
            email="vol@lc.org",
            name="Vol",
            password="VolPass1!",
            roles=["volunteer"],
        )
        vol_hdrs = auth_headers(client, email="vol@lc.org", password="VolPass1!")
        resp = client.get(f"/api/v1/conflicts/?org_id={org_id}", headers=vol_hdrs)
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestListConflictsScoping:
    def test_returns_listresponse_envelope(self, client, db):
        org_id, admin_hdrs, _ = _two_overlapping_events(client, "envelope")
        resp = client.get(f"/api/v1/conflicts/?org_id={org_id}", headers=admin_hdrs)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert "limit" in body
        assert "offset" in body

    def test_returns_double_booked_for_overlapping_assignments(self, client, db):
        org_id, admin_hdrs, vol = _two_overlapping_events(client, "double")
        resp = client.get(
            f"/api/v1/conflicts/?org_id={org_id}&person_id={vol['person_id']}",
            headers=admin_hdrs,
        )
        body = resp.json()
        assert body["total"] >= 1
        assert any(item["type"] == "double_booked" for item in body["items"])

    def test_empty_org_returns_zero_total(self, client, db):
        org_id = "empty-conflicts-org"
        seed_org(client, org_id)
        seed_user(client, org_id, email="admin@e.org", name="Admin", password="AdminPass1!")
        admin_hdrs = auth_headers(client, email="admin@e.org", password="AdminPass1!")

        resp = client.get(f"/api/v1/conflicts/?org_id={org_id}", headers=admin_hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["items"] == []

    def test_cross_org_admin_blocked(self, client, db):
        org_a, admin_hdrs_a, _ = _two_overlapping_events(client, "a")
        org_b = "conflicts-list-org-other"
        seed_org(client, org_b)

        # Admin from org_a tries to query org_b
        resp = client.get(f"/api/v1/conflicts/?org_id={org_b}", headers=admin_hdrs_a)
        assert resp.status_code in (403, 404)

    def test_person_id_narrows_results(self, client, db):
        org_id, admin_hdrs, vol = _two_overlapping_events(client, "narrow")
        # Add another volunteer with no conflicts
        seed_user(
            client,
            org_id,
            email="other-narrow@cl.org",
            name="Other",
            password="VolPass1!",
            roles=["volunteer"],
        )
        # Query for the conflicted volunteer
        resp = client.get(
            f"/api/v1/conflicts/?org_id={org_id}&person_id={vol['person_id']}",
            headers=admin_hdrs,
        )
        body = resp.json()
        assert body["total"] >= 1
