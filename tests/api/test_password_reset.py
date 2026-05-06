"""Password-reset endpoint security tests.

Covers two regressions:
- The default response must NOT include the reset token / reset link.
- The token round-trip must still be testable, gated behind DEBUG_RETURN_RESET_TOKEN.
"""

import pytest
from fastapi.testclient import TestClient

from api.database import get_db
from api.main import app
from api.models import Organization, Person


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def reset_user(client):
    """Seed an org and one person with a known email; cleanup on teardown."""
    db_gen = get_db()
    db = next(db_gen)

    org = Organization(id="reset_test_org", name="Reset Test Org", region="Test")
    db.add(org)
    db.commit()

    person = Person(
        id="reset_test_person",
        org_id="reset_test_org",
        name="Reset Tester",
        email="reset@example.com",
        password_hash="$2b$12$dummy_hash_will_be_replaced",
        roles=["volunteer"],
    )
    db.add(person)
    db.commit()

    yield person

    db.delete(person)
    db.delete(org)
    db.commit()


class TestForgotPasswordResponseShape:
    """Default response must not leak reset token / link."""

    def test_response_omits_token_and_link_by_default(self, client, reset_user, monkeypatch):
        monkeypatch.delenv("DEBUG_RETURN_RESET_TOKEN", raising=False)
        response = client.post("/api/v1/auth/forgot-password", json={"email": "reset@example.com"})
        assert response.status_code == 200
        body = response.json()
        assert "reset_link" not in body
        assert "token" not in body
        assert "message" in body

    def test_response_omits_token_for_unknown_email(self, client):
        """Same response shape regardless of whether the email exists."""
        response = client.post(
            "/api/v1/auth/forgot-password", json={"email": "no-such-user@example.com"}
        )
        assert response.status_code == 200
        body = response.json()
        assert "reset_link" not in body
        assert "token" not in body
        assert "message" in body


class TestForgotPasswordDebugFlag:
    """Under DEBUG_RETURN_RESET_TOKEN=true the token comes back in the body for E2E."""

    def test_token_returned_when_flag_enabled(self, client, reset_user, monkeypatch):
        monkeypatch.setenv("DEBUG_RETURN_RESET_TOKEN", "true")
        response = client.post("/api/v1/auth/forgot-password", json={"email": "reset@example.com"})
        assert response.status_code == 200
        body = response.json()
        assert "token" in body
        assert isinstance(body["token"], str)
        assert len(body["token"]) >= 20

    def test_full_reset_flow_with_debug_flag(self, client, reset_user, monkeypatch):
        monkeypatch.setenv("DEBUG_RETURN_RESET_TOKEN", "true")

        forgot = client.post("/api/v1/auth/forgot-password", json={"email": "reset@example.com"})
        token = forgot.json()["token"]

        new_password = "BrandNewPassword99!"
        confirm = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": new_password},
        )
        assert confirm.status_code == 200
        assert confirm.json()["message"] == "Password reset successfully"

        login = client.post(
            "/api/v1/auth/login",
            json={"email": "reset@example.com", "password": new_password},
        )
        assert login.status_code == 200
        assert "token" in login.json()


class TestForgotPasswordAuditTrail:
    """The forgot-password endpoint should leave an audit row regardless of leak flag."""

    def test_audit_row_created_on_request(self, client, reset_user, monkeypatch):
        monkeypatch.delenv("DEBUG_RETURN_RESET_TOKEN", raising=False)

        from api.models import AuditAction, AuditLog

        db_gen = get_db()
        db = next(db_gen)
        before = (
            db.query(AuditLog)
            .filter(AuditLog.action == AuditAction.PASSWORD_RESET_REQUESTED)
            .count()
        )

        response = client.post("/api/v1/auth/forgot-password", json={"email": "reset@example.com"})
        assert response.status_code == 200

        after = (
            db.query(AuditLog)
            .filter(AuditLog.action == AuditAction.PASSWORD_RESET_REQUESTED)
            .count()
        )
        assert after == before + 1
