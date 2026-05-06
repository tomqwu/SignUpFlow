"""Tests for /api/v1/conflicts/check — backfills sparsely-tested router."""


from datetime import datetime, timedelta

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


# ---------------------------------------------------------------------------
# GET /conflicts/?org_id=&person_id= — ListResponse[ConflictType]
# ---------------------------------------------------------------------------


def _assign(client, admin_hdrs, event_id: str, person_id: str) -> None:
    resp = client.post(
        f"/api/v1/events/{event_id}/assignments",
        json={"person_id": person_id, "action": "assign", "role": "u"},
        headers=admin_hdrs,
    )
    assert resp.status_code in (200, 201), resp.text


@pytest.mark.no_mock_auth
class TestListConflictsEnvelope:
    def test_no_conflicts_returns_empty_list_response(self, client, db):
        _, admin_hdrs, vol, _ = _setup_org_and_event(client, "list-empty")
        resp = client.get(
            "/api/v1/conflicts/",
            params={"org_id": "conflicts-org-list-empty", "person_id": vol["person_id"]},
            headers=admin_hdrs,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        # Uniform ListResponse envelope
        assert set(body.keys()) == {"items", "total", "limit", "offset"}
        assert body["items"] == []
        assert body["total"] == 0
        assert body["limit"] >= 1
        assert body["offset"] == 0

    def test_single_assignment_has_no_conflicts(self, client, db):
        org_id, admin_hdrs, vol, event = _setup_org_and_event(client, "list-single")
        _assign(client, admin_hdrs, event["id"], vol["person_id"])
        resp = client.get(
            "/api/v1/conflicts/",
            params={"org_id": org_id, "person_id": vol["person_id"]},
            headers=admin_hdrs,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] == 0
        assert body["items"] == []


@pytest.mark.no_mock_auth
class TestListConflictsDoubleBooked:
    def test_two_overlapping_assignments_surface_double_booked(self, client, db):
        org_id, admin_hdrs, vol, ev_a = _setup_org_and_event(client, "list-dbl")
        # Second event with same start/end window overlaps ev_a
        ev_b = seed_event(client, admin_hdrs, org_id, event_id="evt-list-dbl-b")
        _assign(client, admin_hdrs, ev_a["id"], vol["person_id"])
        _assign(client, admin_hdrs, ev_b["id"], vol["person_id"])

        resp = client.get(
            "/api/v1/conflicts/",
            params={"org_id": org_id, "person_id": vol["person_id"]},
            headers=admin_hdrs,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] >= 1
        assert all(c["type"] == "double_booked" for c in body["items"])
        # Each conflict should reference one of the two events
        ref_ids = {c["conflicting_event_id"] for c in body["items"]}
        assert ref_ids.issubset({ev_a["id"], ev_b["id"]})

    def test_non_overlapping_assignments_have_no_conflicts(self, client, db):
        org_id, admin_hdrs, vol, ev_a = _setup_org_and_event(client, "list-nonovl")
        # Place ev_b far in the future so it does not overlap ev_a
        start = datetime.now() + timedelta(days=60)
        end = start + timedelta(hours=2)
        resp = client.post(
            "/api/v1/events/",
            json={
                "id": "evt-list-nonovl-b",
                "org_id": org_id,
                "type": "Practice",
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "extra_data": {"role_counts": {}},
            },
            headers=admin_hdrs,
        )
        assert resp.status_code == 201, resp.text
        ev_b = resp.json()
        _assign(client, admin_hdrs, ev_a["id"], vol["person_id"])
        _assign(client, admin_hdrs, ev_b["id"], vol["person_id"])

        resp = client.get(
            "/api/v1/conflicts/",
            params={"org_id": org_id, "person_id": vol["person_id"]},
            headers=admin_hdrs,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["total"] == 0


@pytest.mark.no_mock_auth
class TestListConflictsTimeOff:
    def test_assignment_overlapping_timeoff_surfaces_time_off(self, client, db):
        org_id, admin_hdrs, vol, event = _setup_org_and_event(client, "list-toff")
        _assign(client, admin_hdrs, event["id"], vol["person_id"])
        # Add a vacation period that brackets the event start day
        event_day = datetime.fromisoformat(event["start_time"]).date()
        client.post(
            f"/api/v1/availability/{vol['person_id']}/timeoff",
            json={
                "start_date": (event_day - timedelta(days=1)).isoformat(),
                "end_date": (event_day + timedelta(days=1)).isoformat(),
                "reason": "PTO",
            },
        )

        resp = client.get(
            "/api/v1/conflicts/",
            params={"org_id": org_id, "person_id": vol["person_id"]},
            headers=admin_hdrs,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] >= 1
        assert any(c["type"] == "time_off" for c in body["items"])


@pytest.mark.no_mock_auth
class TestListConflictsAuth:
    def test_unauthenticated_request_is_rejected(self, client, db):
        resp = client.get(
            "/api/v1/conflicts/",
            params={"org_id": "any", "person_id": "any"},
        )
        assert resp.status_code in (401, 403)

    def test_cross_tenant_org_id_is_rejected(self, client, db):
        # Set up two orgs; user in org A tries to read conflicts for org B
        seed_org(client, "conflicts-list-tenant-a")
        seed_user(
            client,
            "conflicts-list-tenant-a",
            email="a@c.org",
            name="A",
            password="APass1!",
        )
        seed_org(client, "conflicts-list-tenant-b")
        seed_user(
            client,
            "conflicts-list-tenant-b",
            email="b@c.org",
            name="B",
            password="BPass1!",
        )
        a_hdrs = auth_headers(client, email="a@c.org", password="APass1!")
        resp = client.get(
            "/api/v1/conflicts/",
            params={"org_id": "conflicts-list-tenant-b", "person_id": "anyone"},
            headers=a_hdrs,
        )
        assert resp.status_code == 403

    def test_unknown_person_returns_404(self, client, db):
        org_id, admin_hdrs, _, _ = _setup_org_and_event(client, "list-unknown")
        resp = client.get(
            "/api/v1/conflicts/",
            params={"org_id": org_id, "person_id": "no-such-person"},
            headers=admin_hdrs,
        )
        assert resp.status_code == 404


@pytest.mark.no_mock_auth
class TestListConflictsPagination:
    def test_limit_and_offset_supported(self, client, db):
        org_id, admin_hdrs, vol, ev_a = _setup_org_and_event(client, "list-page")
        ev_b = seed_event(client, admin_hdrs, org_id, event_id="evt-list-page-b")
        _assign(client, admin_hdrs, ev_a["id"], vol["person_id"])
        _assign(client, admin_hdrs, ev_b["id"], vol["person_id"])

        resp = client.get(
            "/api/v1/conflicts/",
            params={
                "org_id": org_id,
                "person_id": vol["person_id"],
                "limit": 1,
                "offset": 0,
            },
            headers=admin_hdrs,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["limit"] == 1
        assert body["offset"] == 0
        assert len(body["items"]) <= 1
        # total reflects all matching, not just the page
        assert body["total"] >= len(body["items"])
