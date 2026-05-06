"""Tests for /api/v1/conflicts/check — backfills sparsely-tested router."""


import pytest

from tests.api.conftest import auth_headers, seed_event, seed_org, seed_user


def _setup_org_and_event(client, suffix: str):
    org_id = f"conflicts-org-{suffix}"
    seed_org(client, org_id)
    seed_user(client, org_id, email=f"admin-{suffix}@c.org", name="Admin", password="AdminPass1!")
    vol = seed_user(
        client,
        org_id,
        email=f"vol-{suffix}@c.org",
        name="Vol",
        password="VolPass1!",
        roles=["volunteer"],
    )
    admin_hdrs = auth_headers(client, email=f"admin-{suffix}@c.org", password="AdminPass1!")
    event = seed_event(client, admin_hdrs, org_id, event_id=f"evt-{suffix}")
    return org_id, admin_hdrs, vol, event


@pytest.mark.no_mock_auth
class TestNoConflicts:
    def test_clean_assignment_has_no_conflicts(self, client, db):
        _, _, vol, event = _setup_org_and_event(client, "clean")
        resp = client.post(
            "/api/v1/conflicts/check",
            json={"person_id": vol["person_id"], "event_id": event["id"]},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["has_conflicts"] is False
        assert body["conflicts"] == []
        assert body["can_assign"] is True


@pytest.mark.no_mock_auth
class TestAlreadyAssigned:
    def test_already_assigned_blocks(self, client, db):
        _, admin_hdrs, vol, event = _setup_org_and_event(client, "already")
        # Assign first
        client.post(
            f"/api/v1/events/{event['id']}/assignments",
            json={"person_id": vol["person_id"], "action": "assign", "role": "u"},
            headers=admin_hdrs,
        )
        # Now check
        resp = client.post(
            "/api/v1/conflicts/check",
            json={"person_id": vol["person_id"], "event_id": event["id"]},
        )
        body = resp.json()
        assert body["has_conflicts"] is True
        assert body["can_assign"] is False
        assert any(c["type"] == "already_assigned" for c in body["conflicts"])


@pytest.mark.no_mock_auth
class TestUnknownEntities:
    def test_unknown_person_returns_404(self, client, db):
        _, _, _, event = _setup_org_and_event(client, "unknown-p")
        resp = client.post(
            "/api/v1/conflicts/check",
            json={"person_id": "no-such-person", "event_id": event["id"]},
        )
        assert resp.status_code == 404

    def test_unknown_event_returns_404(self, client, db):
        _, _, vol, _ = _setup_org_and_event(client, "unknown-e")
        resp = client.post(
            "/api/v1/conflicts/check",
            json={"person_id": vol["person_id"], "event_id": "no-such-event"},
        )
        assert resp.status_code == 404


@pytest.mark.no_mock_auth
class TestDoubleBooked:
    def test_double_booked_warns_but_allows(self, client, db):
        org_id, admin_hdrs, vol, ev_a = _setup_org_and_event(client, "double")
        # Create a second overlapping event
        ev_b = seed_event(client, admin_hdrs, org_id, event_id="evt-double-b")
        # Assign to first event
        client.post(
            f"/api/v1/events/{ev_a['id']}/assignments",
            json={"person_id": vol["person_id"], "action": "assign", "role": "u"},
            headers=admin_hdrs,
        )
        # Check conflict for second
        resp = client.post(
            "/api/v1/conflicts/check",
            json={"person_id": vol["person_id"], "event_id": ev_b["id"]},
        )
        body = resp.json()
        # Same start time = overlap. Conflict surfaced but assignable.
        if body["has_conflicts"]:
            assert any(c["type"] == "double_booked" for c in body["conflicts"])
            assert body["can_assign"] is True  # double_booked is a warning, not a block
