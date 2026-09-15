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
    "RELEASE_SHA": "a" * 40,
    "SECRET_KEY": "synthetic-test-signing-key-that-is-long-enough-1234",
    "DATABASE_URL": "postgresql://signupflow:synthetic-db-password@db/signupflow",
    "REDIS_URL": "redis://:synthetic-redis-password@redis:6379/0",
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


@pytest.mark.parametrize("release_sha", [None, "short", "g" * 40, "a" * 41])
def test_production_requires_exact_git_release_sha(release_sha):
    result = _validate_in_subprocess(RELEASE_SHA=release_sha)

    assert result.returncode != 0
    assert "RELEASE_SHA must be a 40-character lowercase Git SHA" in (result.stdout + result.stderr)


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
        ("REDIS_URL", ""),
        ("REDIS_URL", "http://redis:6379/0"),
        ("EVENT_BUS_STORAGE", "memory"),
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
    if value:
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


def test_enabled_sms_requires_external_https_callback_urls():
    result = _validate_in_subprocess(
        SMS_ENABLED="true",
        TWILIO_ACCOUNT_SID="AC00000000000000000000000000000000",
        TWILIO_AUTH_TOKEN="synthetic-twilio-token",
        TWILIO_PHONE_NUMBER="+15005550006",
        TWILIO_INCOMING_SMS_URL="http://api.example.test/api/sms/webhook/incoming-sms",
        TWILIO_STATUS_CALLBACK_URL="https://api.example.test/api/sms/webhook/delivery-status",
    )

    assert result.returncode != 0
    assert "TWILIO_INCOMING_SMS_URL must be a valid external HTTPS callback URL" in (
        result.stdout + result.stderr
    )


def test_enabled_sms_accepts_complete_synthetic_callback_configuration():
    result = _validate_in_subprocess(
        SMS_ENABLED="true",
        TWILIO_ACCOUNT_SID="AC00000000000000000000000000000000",
        TWILIO_AUTH_TOKEN="synthetic-twilio-token",
        TWILIO_PHONE_NUMBER="+15005550006",
        TWILIO_INCOMING_SMS_URL="https://api.example.test/api/sms/webhook/incoming-sms",
        TWILIO_STATUS_CALLBACK_URL="https://api.example.test/api/sms/webhook/delivery-status",
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
    assert environment["RELEASE_SHA"] == "${RELEASE_SHA:?Set RELEASE_SHA to the deployed commit}"
    assert environment["READINESS_FAILURE_ALERT_THRESHOLD"] == (
        "${READINESS_FAILURE_ALERT_THRESHOLD:-3}"
    )
    assert environment["ACCESS_TOKEN_EXPIRE_HOURS"] == "${ACCESS_TOKEN_EXPIRE_HOURS:-24}"
    assert environment["SECURITY_HSTS_MAX_AGE"] == "${SECURITY_HSTS_MAX_AGE:-31536000}"
    assert environment["EMAIL_ENABLED"] == "${EMAIL_ENABLED:-false}"
    assert environment["SMS_ENABLED"] == "${SMS_ENABLED:-false}"
    assert environment["BILLING_ENABLED"] == "${BILLING_ENABLED:-false}"
    assert environment["RATE_LIMIT_STORAGE"] == "redis"
    assert environment["EVENT_BUS_STORAGE"] == "redis"
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
    health_command = " ".join(compose["services"]["api"]["healthcheck"]["test"])
    assert "http://localhost:8000/ready" in health_command
    dockerfile = (REPO_ROOT / "Dockerfile").read_text()
    assert "http://localhost:8000/ready" in dockerfile
    assert "http://localhost:8000/health" not in dockerfile
    assert redis["environment"]["REDIS_PASSWORD"] == "${REDIS_PASSWORD:?Set REDIS_PASSWORD}"
    assert "$${REDIS_PASSWORD}" in " ".join(redis["healthcheck"]["test"])


def test_production_compose_runs_one_worker_and_one_scheduler():
    compose = yaml.safe_load((REPO_ROOT / "docker-compose.yml").read_text())
    services = compose["services"]

    assert services["celery-worker"]["command"][:4] == [
        "celery",
        "-A",
        "api.celery_app",
        "worker",
    ]
    beat_services = [
        service for service in services.values() if "beat" in " ".join(service.get("command", []))
    ]
    assert len(beat_services) == 1
    assert "--schedule=/tmp/celerybeat-schedule" in beat_services[0]["command"]
    for service_name in ("celery-worker", "celery-beat"):
        environment = services[service_name]["environment"]
        assert environment["ENVIRONMENT"] == "production"
        assert environment["RELEASE_SHA"] == (
            "${RELEASE_SHA:?Set RELEASE_SHA to the deployed commit}"
        )
        assert environment["SECRET_KEY"] == "${SECRET_KEY:?Set SECRET_KEY}"
        assert environment["EVENT_BUS_STORAGE"] == "redis"
        assert environment["EMAIL_ENABLED"] == "${EMAIL_ENABLED:-false}"
        assert environment["SMS_ENABLED"] == "false"
        assert environment["BILLING_ENABLED"] == "false"


def test_celery_startup_runs_the_production_validator():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from api.celery_app import validate_celery_production_environment; "
                "validate_celery_production_environment()"
            ),
        ],
        cwd=REPO_ROOT,
        env=_subprocess_env(SECRET_KEY="known-bad-worker-key"),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "SECRET_KEY" in result.stdout + result.stderr
    assert "known-bad-worker-key" not in result.stdout + result.stderr


def test_production_artifact_keeps_conservative_single_api_worker_default():
    dockerfile = (REPO_ROOT / "Dockerfile").read_text()
    example = (REPO_ROOT / ".env.example").read_text()

    assert '"--workers", "1"' in dockerfile
    assert '"--workers", "4"' not in dockerfile
    assert dockerfile.count("poetry export") == 1
    assert "pip install --require-hashes" in dockerfile
    assert "COPY --from=builder /opt/venv /opt/venv" in dockerfile
    assert "WORKERS=1" in example
    assert "WORKERS=4" not in example


def test_production_reference_profile_keeps_unverified_services_disabled():
    profile = yaml.safe_load((REPO_ROOT / "config/env.prod.yaml").read_text())

    assert profile["app"]["workers"] == 1
    assert profile["redis"]["rate_limiting_enabled"] is True
    assert profile["email"]["enabled"] is False
    assert profile["sms"]["enabled"] is False
    assert profile["billing"]["enabled"] is False
    assert profile["monitoring"]["sentry"]["enabled"] is False
    assert profile["backup"]["enabled"] is False
