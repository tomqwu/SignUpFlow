"""Tests for the send_password_reset_email wiring (Sprint 9 PR 9.1).

The forgot-password endpoint now invokes
``email_service.send_password_reset_email`` after issuing a reset token.
These tests pin the call shape — they don't actually send any email.
"""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from api.main import app
from api.models import Organization, Person
from api.routers import password_reset as password_reset_router


def _seed_reset_user(db):
    org = Organization(id="reset_email_org", name="Reset Email Org", region="Test")
    db.add(org)
    person = Person(
        id="reset_email_person",
        org_id="reset_email_org",
        name="Reset Email Tester",
        email="reset-email@example.com",
        password_hash="$2b$12$dummy_hash",
        roles=["volunteer"],
    )
    db.add(person)
    db.commit()
    return person


class TestForgotPasswordSendsEmail:
    def test_send_password_reset_email_called_with_user_token(self, db, monkeypatch):
        """When the user exists, the email service is called with the freshly
        issued token, the user's email, and the user's name."""
        monkeypatch.delenv("DEBUG_RETURN_RESET_TOKEN", raising=False)
        _seed_reset_user(db)

        mock_send = MagicMock(return_value=True)
        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            mock_send,
        )

        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset-email@example.com"},
        )
        assert response.status_code == 200, response.text

        # send_password_reset_email is called exactly once with kwargs.
        assert mock_send.call_count == 1
        kwargs = mock_send.call_args.kwargs
        assert kwargs["to_email"] == "reset-email@example.com"
        assert kwargs["name"] == "Reset Email Tester"
        # Token is non-empty and reasonably long (secrets.token_urlsafe(32)).
        assert isinstance(kwargs["reset_token"], str)
        assert len(kwargs["reset_token"]) >= 32
        # Includes app_url so the email can build the web fallback link.
        assert "app_url" in kwargs

    def test_send_password_reset_email_not_called_for_unknown_email(self, db, monkeypatch):
        """No user → no email send. The endpoint still returns the generic
        response so we don't leak whether the email exists."""
        mock_send = MagicMock(return_value=True)
        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            mock_send,
        )

        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "ghost@example.com"},
        )
        assert response.status_code == 200, response.text
        assert mock_send.call_count == 0


class TestSendPasswordResetEmailReturnValue:
    """The endpoint never propagates email-service failures to the caller —
    a flaky SendGrid must not block reset-token issuance."""

    def test_endpoint_succeeds_when_email_send_returns_false(self, db, monkeypatch):
        monkeypatch.delenv("DEBUG_RETURN_RESET_TOKEN", raising=False)
        _seed_reset_user(db)

        mock_send = MagicMock(return_value=False)
        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            mock_send,
        )

        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset-email@example.com"},
        )
        assert response.status_code == 200
        assert mock_send.call_count == 1
