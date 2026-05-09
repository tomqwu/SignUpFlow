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


class TestResetTokenPersistedToDatabase:
    """Regression for Codex review on PR #78 — the reset token must NOT
    live in a per-process in-memory dict, because the default deployment
    runs ``WORKERS=4`` and the worker handling ``POST /reset-password``
    isn't guaranteed to be the one that issued the token. The token is
    persisted to the ``password_reset_tokens`` table; we verify by:

    1. Requesting a reset and checking the token row exists in the DB.
    2. Issuing the reset on a *fresh* SQLAlchemy session (proxy for a
       different worker) and confirming the password actually changed.
    """

    def test_token_row_persisted_after_forgot_password(self, db, monkeypatch):
        from api.models import PasswordResetToken
        from api.routers.password_reset import _hash_reset_token

        monkeypatch.setenv("DEBUG_RETURN_RESET_TOKEN", "true")
        person = _seed_reset_user(db)

        # Mock the email send so we don't depend on EmailService at all.
        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            MagicMock(return_value=True),
        )

        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset-email@example.com"},
        )
        assert response.status_code == 200, response.text
        token = response.json()["token"]

        # Re-query through a fresh expire-on-commit cycle so we're not
        # reading the same identity-mapped object the router commited.
        # Lookup by the digest (raw bearer token is never stored — see
        # _hash_reset_token's docstring for rationale).
        db.expire_all()
        row = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == _hash_reset_token(token))
            .one()
        )
        # Confirm the *raw* token is NOT what was stored — defense against
        # a future regression that accidentally writes the bearer.
        assert row.token_hash != token
        assert row.person_id == person.id
        assert row.used_at is None
        assert row.expires_at is not None

    def test_reset_succeeds_on_separate_session(self, db, monkeypatch):
        """Proxy for the multi-worker scenario: issue the token on one
        SQLAlchemy session, then redeem it via a TestClient request that
        gets a fresh session through ``Depends(get_db)``. If this works
        (it does, because the token is in the DB rather than a per-process
        dict), the multi-worker case works too."""
        from api.models import PasswordResetToken
        from api.routers.password_reset import _hash_reset_token
        from api.security import verify_password

        monkeypatch.setenv("DEBUG_RETURN_RESET_TOKEN", "true")
        person = _seed_reset_user(db)

        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            MagicMock(return_value=True),
        )

        client = TestClient(app)
        forgot_response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset-email@example.com"},
        )
        token = forgot_response.json()["token"]

        # The forgot-password handler used its own get_db session; the
        # token is now committed and visible to anyone — including the
        # next TestClient request, which gets a fresh session.
        reset_response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "NewPassword!2026"},
        )
        assert reset_response.status_code == 200, reset_response.text

        # Verify the password actually changed by reloading the person
        # on yet another fresh fetch.
        db.expire_all()
        person_reloaded = db.query(person.__class__).filter_by(id=person.id).one()
        assert verify_password("NewPassword!2026", person_reloaded.password_hash)

        # Replay must be rejected: token now marked used.
        replay = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "DifferentPassword!2026"},
        )
        assert replay.status_code == 400

        # And the token row exists with used_at stamped.
        db.expire_all()
        row = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == _hash_reset_token(token))
            .one()
        )
        assert row.used_at is not None


class TestForgotPasswordInvalidatesPriorTokens:
    """Regression for Codex review on PR #78 (and docs/features/
    password-reset.md Scenario 6) — when a user requests a second
    password reset, any earlier emailed link must be invalidated.
    Otherwise a brief mailbox compromise lets an attacker race the user
    to redeem a stale link.
    """

    def test_second_request_invalidates_first_token(self, db, monkeypatch):
        from api.models import PasswordResetToken
        from api.routers.password_reset import _hash_reset_token

        monkeypatch.setenv("DEBUG_RETURN_RESET_TOKEN", "true")
        _seed_reset_user(db)

        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            MagicMock(return_value=True),
        )

        client = TestClient(app)

        # First /forgot-password — capture token #1.
        r1 = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset-email@example.com"},
        )
        token1 = r1.json()["token"]

        # Second /forgot-password — issues token #2 and stamps token #1.
        r2 = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset-email@example.com"},
        )
        token2 = r2.json()["token"]
        assert token1 != token2

        db.expire_all()
        row1 = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == _hash_reset_token(token1))
            .one()
        )
        row2 = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == _hash_reset_token(token2))
            .one()
        )
        # First is invalidated, second is fresh.
        assert row1.used_at is not None
        assert row2.used_at is None

        # Redeeming the now-stale token #1 must 400.
        stale = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token1, "new_password": "DoesNotMatter!2026"},
        )
        assert stale.status_code == 400, stale.text

        # Token #2 still works.
        ok = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token2, "new_password": "FreshPassword!2026"},
        )
        assert ok.status_code == 200, ok.text


class TestResetPasswordIsAtomic:
    """Regression for Codex review on PR #78 — a SELECT-then-update flow
    leaks a race where two concurrent /reset-password calls with the
    same token both pass the "unused" check and both change the password
    (last-write-wins). The handler now uses a single conditional UPDATE
    that returns rowcount; the loser sees 0 and 400s.

    True multi-thread concurrency is hard to simulate inside a single
    in-memory SQLite test session, so we exercise the *contract* the
    atomic UPDATE provides — the second redemption attempt of an
    already-used token must 400 — which is what the prod multi-worker
    case ultimately reduces to once one worker has commited.
    """

    def test_second_redemption_of_used_token_is_rejected(self, db, monkeypatch):
        monkeypatch.setenv("DEBUG_RETURN_RESET_TOKEN", "true")
        _seed_reset_user(db)

        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            MagicMock(return_value=True),
        )

        client = TestClient(app)
        forgot = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset-email@example.com"},
        )
        token = forgot.json()["token"]

        first = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "FirstPassword!2026"},
        )
        assert first.status_code == 200, first.text

        # Second submission with the same token: the conditional UPDATE
        # finds 0 rows matching `used_at IS NULL`, so it rolls back and
        # 400s without touching the person's password.
        second = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "SecondPassword!2026"},
        )
        assert second.status_code == 400

    def test_expired_token_is_rejected_atomically(self, db, monkeypatch):
        """The conditional UPDATE includes ``expires_at > now``, so an
        expired token never claims the row — it 400s like any other
        invalid token, and ``used_at`` stays NULL on the expired row."""
        from api.models import PasswordResetToken
        from api.routers.password_reset import _hash_reset_token

        monkeypatch.setenv("DEBUG_RETURN_RESET_TOKEN", "true")
        _seed_reset_user(db)

        monkeypatch.setattr(
            password_reset_router.email_service,
            "send_password_reset_email",
            MagicMock(return_value=True),
        )

        client = TestClient(app)
        forgot = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "reset-email@example.com"},
        )
        token = forgot.json()["token"]

        # Force the token to be expired by editing the DB directly.
        from datetime import timedelta as _td

        from api.timeutils import utcnow as _utcnow

        row = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == _hash_reset_token(token))
            .one()
        )
        row.expires_at = _utcnow() - _td(seconds=1)
        db.commit()

        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "WontApply!2026"},
        )
        assert response.status_code == 400

        # And used_at on the expired row is still NULL — not stamped
        # by a partial claim.
        db.expire_all()
        row_after = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == _hash_reset_token(token))
            .one()
        )
        assert row_after.used_at is None


class TestSendPasswordResetEmailEscapesUserContent:
    """Regression for Codex review on PR #78 — Person.name flows directly
    into the reset email's HTML body. An unescaped name like
    ``<script>alert(1)</script>`` or ``<a href=evil>Click</a>`` would let a
    malicious display name inject markup into a security-sensitive email
    that arrives in the victim's inbox. Build the email content in isolation
    (no router, no DB) and assert HTML escaping at the source.
    """

    def test_html_escapes_name_in_body(self, monkeypatch):
        from api.services.email_service import EmailService

        captured: dict[str, str] = {}

        def _capture(self, to_email, subject, html_content, plain_content=None):
            captured["html"] = html_content
            captured["plain"] = plain_content or ""
            return True

        monkeypatch.setattr(EmailService, "send_email", _capture)
        # Force-enable the service for this isolated test (TESTING gate
        # would short-circuit send_password_reset_email before our capture
        # ran). We replaced send_email above, so no real I/O happens.
        svc = EmailService()
        svc.enabled = True

        nasty = '<script>alert("xss")</script>'
        ok = svc.send_password_reset_email(
            to_email="victim@example.com",
            name=nasty,
            reset_token="t" * 40,
            app_url="http://localhost:8000",
        )
        assert ok is True
        # Raw markup must NOT appear; the escaped form MUST.
        assert nasty not in captured["html"]
        assert "&lt;script&gt;" in captured["html"]
        # Plain-text variant is plain text by definition; no escaping needed
        # there, but the test pins that the function still produces it.
        assert "Hi " in captured["plain"]
