"""Regression coverage for the local test-process safety boundary."""

import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from tests.test_environment import (
    build_test_environment,
    require_loopback_test_connection,
    sanitize_test_process_environment,
)

ROOT = Path(__file__).resolve().parents[2]

POISONED_ENVIRONMENT = {
    "PATH": "/usr/bin:/bin",
    "LANG": "en_CA.UTF-8",
    "STRIPE_SECRET_KEY": "sk_live_should_never_survive",
    "STRIPE_WEBHOOK_SECRET": "whsec_should_never_survive",
    "TWILIO_ACCOUNT_SID": "AC-live",
    "TWILIO_AUTH_TOKEN": "twilio-live-token",
    "TWILIO_PHONE_NUMBER": "+14165550123",
    "SENDGRID_API_KEY": "sendgrid-live-key",
    "SENDGRID_WEBHOOK_PUBLIC_KEY": "sendgrid-live-webhook-key",
    "MAILTRAP_API_TOKEN": "mailtrap-live-token",
    "MAILTRAP_ACCOUNT_ID": "mailtrap-live-account",
    "MAILTRAP_INBOX_ID": "mailtrap-live-inbox",
    "MAILTRAP_SMTP_USER": "mailtrap-live-user",
    "MAILTRAP_SMTP_PASSWORD": "mailtrap-live-password",
    "LOCAL_EMAIL_CAPTURE_DIR": "/tmp/inherited-unowned-capture",
    "OLLAMA_API_KEY": "ollama-voice-key",
    "RECAPTCHA_SITE_KEY": "recaptcha-live-site-key",
    "RECAPTCHA_SECRET_KEY": "recaptcha-live-secret-key",
    "SENTRY_DSN": "https://secret@example.invalid/1",
    "DATABASE_URL": "postgresql://customer.invalid/live",
    "ENVIRONMENT": "production",
    "EMAIL_ENABLED": "true",
    "SMS_ENABLED": "true",
    "BILLING_ENABLED": "true",
}


def test_test_process_environment_removes_live_integrations():
    environment = dict(POISONED_ENVIRONMENT)
    sanitize_test_process_environment(
        "sqlite:////tmp/owned-signupflow-test.db", environment=environment
    )

    assert environment["DATABASE_URL"] == "sqlite:////tmp/owned-signupflow-test.db"
    assert environment["ENVIRONMENT"] == "development"
    assert environment["TESTING"] == "true"
    for name in ("EMAIL_ENABLED", "SMS_ENABLED", "BILLING_ENABLED"):
        assert environment[name] == "false"
    for name in POISONED_ENVIRONMENT:
        if name not in {
            "PATH",
            "LANG",
            "DATABASE_URL",
            "EMAIL_ENABLED",
            "ENVIRONMENT",
            "SMS_ENABLED",
            "BILLING_ENABLED",
        }:
            assert name not in environment


def test_live_server_environment_preserves_runtime_basics_only():
    safe = build_test_environment(
        POISONED_ENVIRONMENT,
        database_url="sqlite:////tmp/owned-e2e.db",
        secret_key="owned-e2e-secret-key-minimum-32-characters",
    )

    assert safe["PATH"] == POISONED_ENVIRONMENT["PATH"]
    assert safe["LANG"] == POISONED_ENVIRONMENT["LANG"]
    assert safe["DATABASE_URL"] == "sqlite:////tmp/owned-e2e.db"
    assert safe["SECRET_KEY"] == "owned-e2e-secret-key-minimum-32-characters"
    assert safe["ENVIRONMENT"] == "development"
    for name in ("EMAIL_ENABLED", "SMS_ENABLED", "BILLING_ENABLED"):
        assert safe[name] == "false"
    for name in POISONED_ENVIRONMENT:
        if name not in {
            "PATH",
            "LANG",
            "DATABASE_URL",
            "EMAIL_ENABLED",
            "ENVIRONMENT",
            "SMS_ENABLED",
            "BILLING_ENABLED",
        }:
            assert name not in safe


def test_live_server_environment_allows_only_an_explicit_test_clock():
    safe = build_test_environment(
        {"SIGNUPFLOW_TEST_NOW": "2030-01-09T12:00:00+00:00"},
        database_url="sqlite:////tmp/owned-clock-e2e.db",
        secret_key="owned-clock-secret-key-minimum-32-characters",
    )

    assert safe["SIGNUPFLOW_ALLOW_TEST_CLOCK"] == "true"
    assert safe["SIGNUPFLOW_TEST_NOW"] == "2030-01-09T12:00:00+00:00"


def test_mail_capture_requires_explicit_owned_path():
    safe = build_test_environment(
        POISONED_ENVIRONMENT,
        database_url="sqlite:////tmp/owned-mail-e2e.db",
        secret_key="owned-mail-secret-key-minimum-32-characters",
        email_capture_dir="/tmp/owned-mail-capture",
        frontend_url="http://127.0.0.1:8123",
    )

    assert safe["LOCAL_EMAIL_CAPTURE_DIR"] == "/tmp/owned-mail-capture"
    assert safe["APP_URL"] == "http://127.0.0.1:8123"
    assert safe["FRONTEND_URL"] == "http://127.0.0.1:8123"
    assert safe["EMAIL_ENABLED"] == "false"


def test_settings_ignore_dotenv_when_test_loading_is_disabled(tmp_path):
    (tmp_path / ".env").write_text(
        "STRIPE_SECRET_KEY=sk_live_must_not_load\n"
        "TWILIO_AUTH_TOKEN=must_not_load\n"
        "BILLING_ENABLED=true\n"
    )
    environment = build_test_environment(
        {"PATH": "/usr/bin", "PYTHONPATH": str(ROOT)},
        database_url="sqlite:///owned.db",
        secret_key="owned-test-secret",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json; from api.core.config import settings; "
                "print(json.dumps({"
                "'billing': settings.BILLING_ENABLED, "
                "'stripe': settings.STRIPE_SECRET_KEY, "
                "'sms': settings.SMS_ENABLED}))"
            ),
        ],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        check=True,
    )

    assert json.loads(result.stdout) == {
        "billing": False,
        "stripe": None,
        "sms": False,
    }


def test_non_loopback_network_fails_before_transport():
    require_loopback_test_connection(("127.0.0.1", 8000))
    require_loopback_test_connection(("::1", 8000))

    with socket.socket() as connection, pytest.raises(
        RuntimeError, match="non-loopback host 'example.com'"
    ):
        connection.connect(("example.com", 443))
