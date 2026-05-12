"""Sprint 10 PR A: invitation email dispatch via EmailService BackgroundTasks.

create_invitation queues send_invitation_email on creation; resend_invitation
fills the prior TODO with the same dispatch path. Tests pin the call shape
+ ensure HTTP response timing isn't blocked on email send.
"""

from datetime import timedelta
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from api.main import app
from api.models import Invitation, Organization, Person
from api.routers import invitations as invitations_router
from api.security import create_access_token
from api.timeutils import utcnow


def _seed_admin(db, *, org_id="invite_email_org", admin_name="Admin Person"):
    """Create an org + admin, return (admin, jwt) so we can authenticate."""
    org = Organization(id=org_id, name="Invite Email Org", region="Test")
    db.add(org)
    admin = Person(
        id=f"{org_id}_admin",
        org_id=org_id,
        name=admin_name,
        email=f"{org_id}_admin@example.com",
        password_hash="$2b$12$dummy_hash",
        roles=["admin"],
    )
    db.add(admin)
    db.commit()
    jwt = create_access_token({"sub": admin.id})
    return admin, jwt


class TestCreateInvitationSendsEmail:
    def test_create_queues_invitation_email(self, db, monkeypatch):
        admin, jwt = _seed_admin(db)

        mock_send = MagicMock(return_value=True)
        monkeypatch.setattr(
            invitations_router.email_service,
            "send_invitation_email",
            mock_send,
        )

        client = TestClient(app)
        resp = client.post(
            f"/api/v1/invitations?org_id={admin.org_id}",
            json={
                "email": "newvolunteer@example.com",
                "name": "New Volunteer",
                "roles": ["volunteer"],
            },
            headers={"Authorization": f"Bearer {jwt}"},
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        # Email service was called once with the user's details + the
        # newly-issued invitation token.
        assert mock_send.call_count == 1
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["to_email"] == "newvolunteer@example.com"
        assert call_kwargs["admin_name"] == admin.name
        assert call_kwargs["org_name"] == "Invite Email Org"
        # Token in response matches what we sent to the email service.
        assert call_kwargs["invitation_token"] == body["token"]

    def test_create_does_not_5xx_when_email_send_fails(self, db, monkeypatch):
        """Email service raising must not propagate — invitation row was
        already committed and the user shouldn't see a 500."""
        admin, jwt = _seed_admin(db, org_id="invite_email_fail_org")

        def _raise(**_kw):
            raise RuntimeError("simulated SendGrid 500")

        monkeypatch.setattr(invitations_router.email_service, "send_invitation_email", _raise)

        client = TestClient(app)
        resp = client.post(
            f"/api/v1/invitations?org_id={admin.org_id}",
            json={
                "email": "newvol@example.com",
                "name": "New Vol",
                "roles": ["volunteer"],
            },
            headers={"Authorization": f"Bearer {jwt}"},
        )
        assert resp.status_code == 201, resp.text


class TestResendInvitationSendsEmail:
    def test_resend_queues_invitation_email_with_rotated_token(self, db, monkeypatch):
        admin, jwt = _seed_admin(db, org_id="resend_email_org")

        invitation = Invitation(
            id="inv_resend_test",
            org_id=admin.org_id,
            email="pending@example.com",
            name="Pending Person",
            roles=["volunteer"],
            invited_by=admin.id,
            token="original_token_value",
            status="pending",
            expires_at=utcnow() + timedelta(days=7),
        )
        db.add(invitation)
        db.commit()

        mock_send = MagicMock(return_value=True)
        monkeypatch.setattr(
            invitations_router.email_service,
            "send_invitation_email",
            mock_send,
        )

        client = TestClient(app)
        resp = client.post(
            f"/api/v1/invitations/{invitation.id}/resend",
            headers={"Authorization": f"Bearer {jwt}"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()

        # Token was rotated; email got the new one, not the original.
        assert body["token"] != "original_token_value"
        assert mock_send.call_count == 1
        assert mock_send.call_args.kwargs["invitation_token"] == body["token"]
        assert mock_send.call_args.kwargs["to_email"] == "pending@example.com"
