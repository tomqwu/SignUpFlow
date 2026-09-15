"""Fail-closed production configuration and clean-process startup tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VALID_PRODUCTION_ENV = {
    "SIGNUPFLOW_LOAD_DOTENV": "false",
    "ENVIRONMENT": "production",
    "SECRET_KEY": "synthetic-test-signing-key-that-is-long-enough-1234",
    "DATABASE_URL": "postgresql://signupflow:synthetic-db-password@db/signupflow",
    "APP_URL": "https://app.example.test",
    "API_BASE_URL": "https://api.example.test",
    "FRONTEND_URL": "https://app.example.test",
    "CORS_ALLOWED_ORIGINS": "https://app.example.test",
    "ACCESS_TOKEN_EXPIRE_HOURS": "24",
    "TESTING": "false",
    "DEBUG": "false",
    "DEBUG_RETURN_RESET_TOKEN": "false",
    "DISABLE_RATE_LIMITS": "false",
    "DISABLE_USAGE_LIMITS": "false",
    "SIGNUPFLOW_ALLOW_TEST_CLOCK": "false",
    "EMAIL_ENABLED": "false",
    "SMS_ENABLED": "false",
    "BILLING_ENABLED": "false",
    "SECURITY_HSTS_ENABLED": "true",
    "SECURITY_CSP_ENABLED": "true",
}


def _subprocess_env(**overrides: str | None) -> dict[str, str]:
    environment = {
        "HOME": os.environ.get("HOME", str(REPO_ROOT)),
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": str(REPO_ROOT),
        **VALID_PRODUCTION_ENV,
    }
    for key, value in overrides.items():
        if value is None:
            environment.pop(key, None)
        else:
            environment[key] = value
    return environment


def _validate_in_subprocess(**overrides: str | None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from api.core.runtime_config import validate_production_environment; "
                "validate_production_environment(); print('VALID')"
            ),
        ],
        cwd=REPO_ROOT,
        env=_subprocess_env(**overrides),
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("SECRET_KEY", "your-secret-key-change-in-production-use-env-var"),
        ("SECRET_KEY", "change-this-to-a-random-secret-key-in-production"),
        ("SECRET_KEY", "your-secret-key-min-32-chars-CHANGE-IN-PRODUCTION"),
        ("SECRET_KEY", "whitespace-padded-secret-that-is-long-enough "),
        ("DATABASE_URL", "sqlite:///./production.db"),
        (
            "DATABASE_URL",
            "postgresql://signupflow:changeme_in_production@db/signupflow",
        ),
        ("APP_URL", "http://app.example.test"),
        ("FRONTEND_URL", "https://app.example.test/path"),
        ("CORS_ALLOWED_ORIGINS", "*"),
        ("ACCESS_TOKEN_EXPIRE_HOURS", "not-a-number"),
        ("TESTING", "true"),
        ("DEBUG", "true"),
        ("DEBUG_RETURN_RESET_TOKEN", "true"),
        ("DISABLE_RATE_LIMITS", "true"),
        ("DISABLE_USAGE_LIMITS", "true"),
        ("SIGNUPFLOW_ALLOW_TEST_CLOCK", "true"),
        ("LOCAL_EMAIL_CAPTURE_DIR", "/tmp/production-mail"),
        ("TRUSTED_PROXY_IPS", "0.0.0.0/0"),
        ("TRUSTED_PROXY_IPS", "not-a-network"),
        ("EMAIL_ENABLED", "sometimes"),
        ("SECURITY_HSTS_MAX_AGE", "not-a-number"),
        ("EMAIL_ENABLED", "true"),
        ("SMS_ENABLED", "true"),
        ("BILLING_ENABLED", "true"),
    ],
)
def test_each_unsafe_production_setting_fails_in_a_clean_process(variable, value):
    result = _validate_in_subprocess(**{variable: value})
    combined = result.stdout + result.stderr

    assert result.returncode != 0
    assert variable in combined
    assert value not in combined


def test_disabled_providers_ignore_inherited_credentials():
    result = _validate_in_subprocess(
        SENDGRID_API_KEY="poisoned-sendgrid-value",
        TWILIO_ACCOUNT_SID="poisoned-twilio-value",
        TWILIO_AUTH_TOKEN="poisoned-twilio-value",
        TWILIO_PHONE_NUMBER="+15005550006",
        STRIPE_SECRET_KEY="poisoned-stripe-value",
        STRIPE_WEBHOOK_SECRET="poisoned-stripe-value",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "VALID"


def test_invalid_production_config_stops_before_database_initialization():
    script = """
import json
import api.main as main
from fastapi.testclient import TestClient

database_calls = []
main.init_db = lambda: database_calls.append("called")
try:
    with TestClient(main.app):
        pass
except Exception as exc:
    print(json.dumps({"database_calls": database_calls, "error": str(exc)}))
    raise SystemExit(3)
raise SystemExit(0)
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env=_subprocess_env(SECRET_KEY="known-bad-production-key"),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 3
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["database_calls"] == []
    assert "SECRET_KEY" in payload["error"]
    assert "known-bad-production-key" not in result.stdout + result.stderr


def test_valid_production_startup_uses_secure_cookie_and_token_lifetime():
    script = """
import json
from fastapi import Response
from fastapi.testclient import TestClient
import api.main as main
from web.auth import _set_cookie

database_calls = []
main.init_db = lambda: database_calls.append("called")
with TestClient(main.app) as client:
    assert client.get("/api/v1").status_code == 200
response = Response()
_set_cookie(response, "synthetic-session-token")
print(json.dumps({
    "database_calls": database_calls,
    "cookie": response.headers["set-cookie"],
}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env=_subprocess_env(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["database_calls"] == ["called"]
    assert "HttpOnly" in payload["cookie"]
    assert "Secure" in payload["cookie"]
    assert "SameSite=lax" in payload["cookie"]
    assert "Max-Age=86400" in payload["cookie"]


def test_valid_boolean_aliases_drive_the_same_production_headers():
    script = """
import json
from fastapi.testclient import TestClient
import api.main as main

main.init_db = lambda: None
with TestClient(main.app) as client:
    response = client.get("/api/v1")
print(json.dumps({
    "hsts": response.headers.get("strict-transport-security"),
    "csp": response.headers.get("content-security-policy"),
}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env=_subprocess_env(
            ENVIRONMENT=" Production ",
            SECURITY_HSTS_ENABLED="yes",
            SECURITY_CSP_ENABLED="on",
        ),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["hsts"] == "max-age=31536000; includeSubDomains"
    assert payload["csp"]


def test_production_compose_passes_canonical_fail_closed_settings():
    compose = yaml.safe_load((REPO_ROOT / "docker-compose.yml").read_text())
    environment = compose["services"]["api"]["environment"]
    database = compose["services"]["db"]
    migration = compose["services"]["migrate"]
    redis = compose["services"]["redis"]

    assert environment["ENVIRONMENT"] == "production"
    assert environment["ACCESS_TOKEN_EXPIRE_HOURS"] == "${ACCESS_TOKEN_EXPIRE_HOURS:-24}"
    assert environment["SECURITY_HSTS_MAX_AGE"] == "${SECURITY_HSTS_MAX_AGE:-31536000}"
    assert environment["EMAIL_ENABLED"] == "${EMAIL_ENABLED:-false}"
    assert environment["SMS_ENABLED"] == "${SMS_ENABLED:-false}"
    assert environment["BILLING_ENABLED"] == "${BILLING_ENABLED:-false}"
    assert "JWT_EXPIRE_HOURS" not in environment
    assert "RATE_LIMITING_ENABLED" not in environment
    assert "changeme_in_production" not in (REPO_ROOT / "docker-compose.yml").read_text()
    assert environment["EMAIL_FROM"] == "${EMAIL_FROM:-noreply@signupflow.io}"
    assert "FROM_EMAIL" not in environment
    assert "ports" not in database
    assert "ports" not in redis
    assert migration["command"] == ["python", "-m", "alembic", "upgrade", "head"]
    assert migration["environment"]["DATABASE_URL"] == environment["DATABASE_URL"]
    assert compose["services"]["api"]["depends_on"]["migrate"]["condition"] == (
        "service_completed_successfully"
    )
    assert redis["environment"]["REDIS_PASSWORD"] == "${REDIS_PASSWORD:?Set REDIS_PASSWORD}"
    assert "$${REDIS_PASSWORD}" in " ".join(redis["healthcheck"]["test"])


def test_production_artifact_enforces_single_worker_until_shared_state_exists():
    dockerfile = (REPO_ROOT / "Dockerfile").read_text()
    example = (REPO_ROOT / ".env.example").read_text()

    assert '"--workers", "1"' in dockerfile
    assert '"--workers", "4"' not in dockerfile
    assert dockerfile.count("poetry install") == 1
    assert "--no-root" in dockerfile
    assert "WORKERS=1" in example
    assert "WORKERS=4" not in example


def test_production_reference_profile_keeps_unverified_services_disabled():
    profile = yaml.safe_load((REPO_ROOT / "config/env.prod.yaml").read_text())

    assert profile["app"]["workers"] == 1
    assert profile["redis"]["rate_limiting_enabled"] is False
    assert profile["email"]["enabled"] is False
    assert profile["sms"]["enabled"] is False
    assert profile["billing"]["enabled"] is False
    assert profile["monitoring"]["sentry"]["enabled"] is False
    assert profile["backup"]["enabled"] is False
