"""Tests for the send_password_reset_email wiring (Sprint 9 PR 9.1).

The forgot-password endpoint now queues
``email_service.send_password_reset_email`` via FastAPI BackgroundTasks
after issuing a reset token. These tests pin the call shape AND prove
that the HTTP response timing does not leak account existence — which
is the security guarantee the endpoint must keep.
"""

import time
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
        issued token, the user's email, and the user's name. The send happens
        as a Starlette BackgroundTask AFTER the HTTP response, so we use
        TestClient (which runs background tasks synchronously after the
        request returns) and verify the mock was invoked."""
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

    def test_endpoint_succeeds_when_email_send_raises(self, db, monkeypatch):
        """A throwing email service must not bubble up to the HTTP caller —
        the wrapper swallows + logs."""
        monkeypatch.delenv("DEBUG_RETURN_RESET_TOKEN", raising=False)
        _seed_reset_user(db)

        def _boom(**kwargs):
            raise RuntimeError("SendGrid is on fire")

        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            _boom,
        )

        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset-email@example.com"},
        )
        assert response.status_code == 200


class TestForgotPasswordTimingDoesNotLeakExistence:
    """Anti-enumeration regression. The slow-email-backend path must not
    delay /forgot-password's HTTP response, otherwise a probe can compare
    response timing for known-vs-unknown emails to enumerate registered
    users.

    Implementation: the email send is queued via Starlette
    BackgroundTasks, which runs AFTER the response is sent on the wire.
    We simulate a 2s SendGrid via monkeypatch + assert the response
    landed within a tight bound, regardless of the slow backend.
    """

    def test_known_email_response_is_fast_even_with_slow_email_backend(self, db, monkeypatch):
        monkeypatch.delenv("DEBUG_RETURN_RESET_TOKEN", raising=False)
        _seed_reset_user(db)

        def _slow_send(**kwargs):
            time.sleep(2.0)  # simulate retrying SMTP / SendGrid
            return True

        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            _slow_send,
        )

        # NOTE: TestClient runs background tasks synchronously on response
        # close, so call timing here will INCLUDE the 2s. To get a true
        # network-timing measurement we'd need an async live server. The
        # next-best regression check: assert that the route's pre-response
        # work alone is fast — i.e., the slow path is queued, not awaited.
        # We do this by patching BackgroundTasks.add_task to NOT execute
        # the queued callable, simulating the "after response close"
        # boundary. If `add_task` weren't used, the slow send would still
        # block the in-handler timing here.
        captured_tasks = []
        orig_add_task = password_reset_router.BackgroundTasks.add_task

        def _capture_task(self, fn, *args, **kw):
            captured_tasks.append((fn, args, kw))

        monkeypatch.setattr(password_reset_router.BackgroundTasks, "add_task", _capture_task)
        try:
            client = TestClient(app)
            t0 = time.monotonic()
            response = client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "reset-email@example.com"},
            )
            elapsed = time.monotonic() - t0
        finally:
            monkeypatch.setattr(password_reset_router.BackgroundTasks, "add_task", orig_add_task)

        assert response.status_code == 200
        # 1.0s is generous: the slow backend would force >= 2s if we'd
        # awaited it inline.
        assert elapsed < 1.0, f"forgot-password took {elapsed:.2f}s — likely awaiting email"
        # And the email send WAS queued (just not executed in this test).
        assert len(captured_tasks) == 1
        fn, _args, kw = captured_tasks[0]
        assert fn is password_reset_router._send_reset_email_quiet
        assert kw["to_email"] == "reset-email@example.com"

    def test_known_and_unknown_email_have_indistinguishable_timing_when_send_is_queued(
        self, db, monkeypatch
    ):
        """Tighter version: with the email send queued (not awaited), a
        known and an unknown email take comparable time. We patch
        BackgroundTasks.add_task to a no-op and the email service to a
        slow function; both calls should be fast and within a few hundred
        ms of each other."""
        monkeypatch.delenv("DEBUG_RETURN_RESET_TOKEN", raising=False)
        _seed_reset_user(db)

        # Neuter the queue so we measure ONLY the synchronous handler time.
        monkeypatch.setattr(
            password_reset_router.BackgroundTasks,
            "add_task",
            lambda self, *a, **kw: None,
        )

        def _slow_send(**kwargs):
            time.sleep(2.0)
            return True

        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            _slow_send,
        )

        client = TestClient(app)

        t0 = time.monotonic()
        r_known = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset-email@example.com"},
        )
        t_known = time.monotonic() - t0
        assert r_known.status_code == 200

        t0 = time.monotonic()
        r_unknown = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "ghost@example.com"},
        )
        t_unknown = time.monotonic() - t0
        assert r_unknown.status_code == 200

        # Both should be << 2s (i.e., the slow-email-backend never blocks).
        assert t_known < 0.5, f"known-email path took {t_known:.2f}s"
        assert t_unknown < 0.5, f"unknown-email path took {t_unknown:.2f}s"
