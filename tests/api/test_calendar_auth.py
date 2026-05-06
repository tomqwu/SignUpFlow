"""Calendar auth-gap tests (Sprint 4 PR 4.5).

Previously `/calendar/subscribe` and `/calendar/reset-token` accepted any
`person_id` query param with no auth check. After this PR they require an
authenticated user who is either the owner or an admin in the same org. A
new admin-only `/calendar/{person_id}/admin-reset` endpoint forces a token
reset on a different user. Both reset paths are audited.
"""

import pytest

from api.models import AuditAction, AuditLog
from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin_for(client, org_id: str, suffix: str):
    seed_user(client, org_id, email=f"admin-{suffix}@o.org", name="Admin", password="AdminPass1!")
    return auth_headers(client, email=f"admin-{suffix}@o.org", password="AdminPass1!")


def _person_id_for_email(client, headers, email: str) -> str:
    """Look up the auto-generated person_id for an email via /people/me."""
    resp = client.get("/api/v1/people/me", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    if body["email"] == email:
        return body["id"]
    raise AssertionError(f"expected {email}, got {body['email']}")


@pytest.mark.no_mock_auth
class TestSubscribeAuth:
    def test_no_auth_rejected(self, client, db):
        org_id = "cal-noauth"
        seed_org(client, org_id)
        admin_hdrs = _admin_for(client, org_id, "noauth")
        my_id = _person_id_for_email(client, admin_hdrs, "admin-noauth@o.org")

        resp = client.get(f"/api/v1/calendar/subscribe?person_id={my_id}")
        assert resp.status_code in (401, 403)

    def test_self_can_subscribe(self, client, db):
        org_id = "cal-self"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "self")
        my_id = _person_id_for_email(client, hdrs, "admin-self@o.org")

        resp = client.get(f"/api/v1/calendar/subscribe?person_id={my_id}", headers=hdrs)
        assert resp.status_code == 200, resp.text

    def test_admin_can_subscribe_other_in_same_org(self, client, db):
        org_id = "cal-admin-other"
        seed_org(client, org_id)
        admin_hdrs = _admin_for(client, org_id, "admin-other-a")
        seed_user(
            client,
            org_id,
            email="other@o.org",
            name="Other",
            password="OtherPass1!",
            roles=["volunteer"],
        )
        other_hdrs = auth_headers(client, email="other@o.org", password="OtherPass1!")
        other_id = _person_id_for_email(client, other_hdrs, "other@o.org")

        resp = client.get(f"/api/v1/calendar/subscribe?person_id={other_id}", headers=admin_hdrs)
        assert resp.status_code == 200, resp.text

    def test_volunteer_cannot_subscribe_other(self, client, db):
        org_id = "cal-vol-block"
        seed_org(client, org_id)
        _admin_for(client, org_id, "vol-block-admin")
        seed_user(
            client,
            org_id,
            email="vol1@o.org",
            name="Vol1",
            password="V1Pass1!",
            roles=["volunteer"],
        )
        seed_user(
            client,
            org_id,
            email="vol2@o.org",
            name="Vol2",
            password="V2Pass1!",
            roles=["volunteer"],
        )
        v1_hdrs = auth_headers(client, email="vol1@o.org", password="V1Pass1!")
        v2_hdrs = auth_headers(client, email="vol2@o.org", password="V2Pass1!")
        v2_id = _person_id_for_email(client, v2_hdrs, "vol2@o.org")

        resp = client.get(f"/api/v1/calendar/subscribe?person_id={v2_id}", headers=v1_hdrs)
        assert resp.status_code == 403

    def test_cross_org_admin_blocked(self, client, db):
        seed_org(client, "cal-org-a")
        seed_org(client, "cal-org-b")
        a_hdrs = _admin_for(client, "cal-org-a", "x-a")
        b_hdrs = _admin_for(client, "cal-org-b", "x-b")
        b_id = _person_id_for_email(client, b_hdrs, "admin-x-b@o.org")

        resp = client.get(f"/api/v1/calendar/subscribe?person_id={b_id}", headers=a_hdrs)
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestResetToken:
    def test_self_reset_emits_audit(self, client, db):
        org_id = "cal-reset-self"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "reset-self")
        my_id = _person_id_for_email(client, hdrs, "admin-reset-self@o.org")

        before = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.CALENDAR_TOKEN_RESET).count()
        )
        resp = client.post(f"/api/v1/calendar/reset-token?person_id={my_id}", headers=hdrs)
        assert resp.status_code == 200, resp.text
        after = (
            db.query(AuditLog).filter(AuditLog.action == AuditAction.CALENDAR_TOKEN_RESET).count()
        )
        assert after == before + 1

    def test_volunteer_cannot_reset_other(self, client, db):
        org_id = "cal-reset-vol"
        seed_org(client, org_id)
        _admin_for(client, org_id, "reset-vol-admin")
        seed_user(
            client,
            org_id,
            email="r1@o.org",
            name="R1",
            password="R1Pass1!",
            roles=["volunteer"],
        )
        seed_user(
            client,
            org_id,
            email="r2@o.org",
            name="R2",
            password="R2Pass1!",
            roles=["volunteer"],
        )
        r1_hdrs = auth_headers(client, email="r1@o.org", password="R1Pass1!")
        r2_hdrs = auth_headers(client, email="r2@o.org", password="R2Pass1!")
        r2_id = _person_id_for_email(client, r2_hdrs, "r2@o.org")

        resp = client.post(f"/api/v1/calendar/reset-token?person_id={r2_id}", headers=r1_hdrs)
        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestAdminReset:
    def test_admin_reset_other_emits_admin_audit(self, client, db):
        org_id = "cal-admin-reset"
        seed_org(client, org_id)
        admin_hdrs = _admin_for(client, org_id, "admin-reset-a")
        seed_user(
            client,
            org_id,
            email="targ@o.org",
            name="Target",
            password="TargPass1!",
            roles=["volunteer"],
        )
        targ_hdrs = auth_headers(client, email="targ@o.org", password="TargPass1!")
        targ_id = _person_id_for_email(client, targ_hdrs, "targ@o.org")

        before = (
            db.query(AuditLog)
            .filter(AuditLog.action == AuditAction.CALENDAR_TOKEN_ADMIN_RESET)
            .count()
        )
        resp = client.post(f"/api/v1/calendar/{targ_id}/admin-reset", headers=admin_hdrs)
        assert resp.status_code == 200, resp.text
        after = (
            db.query(AuditLog)
            .filter(AuditLog.action == AuditAction.CALENDAR_TOKEN_ADMIN_RESET)
            .count()
        )
        assert after == before + 1

    def test_volunteer_cannot_admin_reset(self, client, db):
        org_id = "cal-admin-reset-vol"
        seed_org(client, org_id)
        admin_hdrs = _admin_for(client, org_id, "vol-block-aadmin")
        seed_user(
            client,
            org_id,
            email="v3@o.org",
            name="V3",
            password="V3Pass1!",
            roles=["volunteer"],
        )
        v3_hdrs = auth_headers(client, email="v3@o.org", password="V3Pass1!")
        # Target the admin, attempt as volunteer.
        admin_id = _person_id_for_email(client, admin_hdrs, "admin-vol-block-aadmin@o.org")

        resp = client.post(f"/api/v1/calendar/{admin_id}/admin-reset", headers=v3_hdrs)
        assert resp.status_code == 403

    def test_admin_cross_org_blocked(self, client, db):
        seed_org(client, "cal-cr-a")
        seed_org(client, "cal-cr-b")
        a_hdrs = _admin_for(client, "cal-cr-a", "cr-a")
        b_hdrs = _admin_for(client, "cal-cr-b", "cr-b")
        b_id = _person_id_for_email(client, b_hdrs, "admin-cr-b@o.org")

        resp = client.post(f"/api/v1/calendar/{b_id}/admin-reset", headers=a_hdrs)
        assert resp.status_code == 403
