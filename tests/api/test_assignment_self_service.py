"""Volunteer assignment self-service tests.

Volunteers (not just admins) can:
- accept their own assignment
- decline their own assignment with a reason
- request a swap on their own assignment
- list their own assignments

Cross-user actions are forbidden. Cross-org actions are blocked by the tenancy guard.
"""

import pytest

from tests.api.conftest import auth_headers, seed_event, seed_org, seed_user


def _setup_org_with_assignment(client, db, suffix: str, role: str = "usher"):
    """Create an org, an admin, a volunteer, an event, and assign the volunteer to it."""
    org_id = f"vss-org-{suffix}"
    seed_org(client, org_id)
    seed_user(
        client,
        org_id,
        email=f"admin-{suffix}@vss.org",
        name="Admin",
        password="AdminPass1!",
    )
    vol = seed_user(
        client,
        org_id,
        email=f"vol-{suffix}@vss.org",
        name="Volunteer",
        password="VolPass1!",
        roles=["volunteer"],
    )
    admin_hdrs = auth_headers(client, email=f"admin-{suffix}@vss.org", password="AdminPass1!")
    event = seed_event(
        client,
        admin_hdrs,
        org_id,
        event_id=f"evt-{suffix}",
    )
    resp = client.post(
        f"/api/v1/events/{event['id']}/assignments",
        json={"person_id": vol["person_id"], "action": "assign", "role": role},
        headers=admin_hdrs,
    )
    assert resp.status_code == 200, resp.text
    aid = resp.json()["assignment_id"]
    return {
        "org_id": org_id,
        "admin_hdrs": admin_hdrs,
        "vol": vol,
        "event": event,
        "assignment_id": aid,
    }


@pytest.mark.no_mock_auth
class TestVolunteerAccept:
    def test_volunteer_accepts_own_assignment(self, client, db):
        ctx = _setup_org_with_assignment(client, db, "accept")
        vol_hdrs = auth_headers(client, email="vol-accept@vss.org", password="VolPass1!")

        resp = client.post(f"/api/v1/assignments/{ctx['assignment_id']}/accept", headers=vol_hdrs)
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "confirmed"

    def test_volunteer_cannot_accept_someone_elses_assignment(self, client, db):
        ctx = _setup_org_with_assignment(client, db, "cross")
        # Add a second volunteer in the same org
        seed_user(
            client,
            ctx["org_id"],
            email="other@vss.org",
            name="Other",
            password="VolPass1!",
            roles=["volunteer"],
        )
        other_hdrs = auth_headers(client, email="other@vss.org", password="VolPass1!")

        resp = client.post(f"/api/v1/assignments/{ctx['assignment_id']}/accept", headers=other_hdrs)
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestVolunteerDecline:
    def test_decline_persists_reason(self, client, db):
        ctx = _setup_org_with_assignment(client, db, "decline")
        vol_hdrs = auth_headers(client, email="vol-decline@vss.org", password="VolPass1!")

        resp = client.post(
            f"/api/v1/assignments/{ctx['assignment_id']}/decline",
            json={"decline_reason": "Out of town"},
            headers=vol_hdrs,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["status"] == "declined"
        assert body["decline_reason"] == "Out of town"

    def test_decline_requires_reason(self, client, db):
        ctx = _setup_org_with_assignment(client, db, "decline-no-reason")
        vol_hdrs = auth_headers(client, email="vol-decline-no-reason@vss.org", password="VolPass1!")

        resp = client.post(
            f"/api/v1/assignments/{ctx['assignment_id']}/decline",
            json={},
            headers=vol_hdrs,
        )
        assert resp.status_code == 422


@pytest.mark.no_mock_auth
class TestVolunteerSwapRequest:
    def test_swap_request_sets_status(self, client, db):
        ctx = _setup_org_with_assignment(client, db, "swap")
        vol_hdrs = auth_headers(client, email="vol-swap@vss.org", password="VolPass1!")

        resp = client.post(
            f"/api/v1/assignments/{ctx['assignment_id']}/swap-request",
            json={"note": "Family wedding that day"},
            headers=vol_hdrs,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "swap_requested"

    def test_swap_request_works_without_note(self, client, db):
        ctx = _setup_org_with_assignment(client, db, "swap-no-note")
        vol_hdrs = auth_headers(client, email="vol-swap-no-note@vss.org", password="VolPass1!")

        resp = client.post(
            f"/api/v1/assignments/{ctx['assignment_id']}/swap-request",
            json={},
            headers=vol_hdrs,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "swap_requested"


@pytest.mark.no_mock_auth
class TestListMyAssignments:
    def test_returns_only_caller_assignments(self, client, db):
        ctx = _setup_org_with_assignment(client, db, "list")
        # Add a second volunteer in the same org and assign them to a second event
        org_id = ctx["org_id"]
        seed_user(
            client,
            org_id,
            email="other-list@vss.org",
            name="Other",
            password="VolPass1!",
            roles=["volunteer"],
        )
        admin_hdrs = ctx["admin_hdrs"]
        ev2 = seed_event(client, admin_hdrs, org_id, event_id="evt-list-2")
        resp = client.post(
            f"/api/v1/events/{ev2['id']}/assignments",
            json={"person_id": "other-list@vss.org-id-not-this", "action": "assign", "role": "u"},
            headers=admin_hdrs,
        )
        # That'll fail because the placeholder person_id doesn't match — fall back to listing only.
        # Use the real other person_id:
        other = client.post(
            "/api/v1/auth/login",
            json={"email": "other-list@vss.org", "password": "VolPass1!"},
        ).json()
        client.post(
            f"/api/v1/events/{ev2['id']}/assignments",
            json={"person_id": other["person_id"], "action": "assign", "role": "u"},
            headers=admin_hdrs,
        )

        # Caller (the original vol) should see only the original assignment
        vol_hdrs = auth_headers(client, email="vol-list@vss.org", password="VolPass1!")
        resp = client.get("/api/v1/assignments/me", headers=vol_hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert len(body["items"]) == 1
        assert body["items"][0]["event_id"] == ctx["event"]["id"]


@pytest.mark.no_mock_auth
class TestAuditTrail:
    def test_accept_emits_audit_row(self, client, db):
        from api.models import AuditAction, AuditLog

        ctx = _setup_org_with_assignment(client, db, "audit")
        before = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.ASSIGNMENT_ACCEPTED).count()
        )
        vol_hdrs = auth_headers(client, email="vol-audit@vss.org", password="VolPass1!")
        client.post(f"/api/v1/assignments/{ctx['assignment_id']}/accept", headers=vol_hdrs)
        after = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.ASSIGNMENT_ACCEPTED).count()
        )
        assert after == before + 1
