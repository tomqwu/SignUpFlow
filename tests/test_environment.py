"""Build deterministic test environments without inherited provider credentials."""

from __future__ import annotations

import os
from collections.abc import Mapping, MutableMapping
from ipaddress import ip_address
from typing import Any

RUNTIME_ENVIRONMENT_KEYS = {
    "HOME",
    "LANG",
    "LC_ALL",
    "LOGNAME",
    "PATH",
    "PLAYWRIGHT_BROWSERS_PATH",
    "POETRY_ACTIVE",
    "PYTHONHOME",
    "PYTHONPATH",
    "SHELL",
    "TMPDIR",
    "USER",
    "VIRTUAL_ENV",
}

PROVIDER_ENVIRONMENT_KEYS = {
    "MAILTRAP_ACCOUNT_ID",
    "MAILTRAP_API_TOKEN",
    "MAILTRAP_INBOX_ID",
    "MAILTRAP_SMTP_HOST",
    "MAILTRAP_SMTP_PASSWORD",
    "MAILTRAP_SMTP_PORT",
    "MAILTRAP_SMTP_USER",
    "OLLAMA_API_KEY",
    "OLLAMA_BASE_URL",
    "OLLAMA_HOST",
    "RECAPTCHA_SECRET_KEY",
    "RECAPTCHA_SITE_KEY",
    "SENDGRID_API_KEY",
    "SENDGRID_WEBHOOK_PUBLIC_KEY",
    "SENTRY_DSN",
    "STRIPE_PUBLIC_KEY",
    "STRIPE_PUBLISHABLE_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_PHONE_NUMBER",
}


def require_loopback_test_connection(address: Any) -> None:
    """Reject network connections outside this machine during default tests."""
    if not isinstance(address, tuple):
        return
    host = address[0]
    if isinstance(host, bytes):
        host = host.decode(errors="replace")
    if host == "localhost":
        return
    try:
        if ip_address(host).is_loopback:
            return
    except ValueError:
        pass
    raise RuntimeError(f"Default tests cannot connect to non-loopback host {host!r}")


def sanitize_test_process_environment(
    database_url: str,
    environment: MutableMapping[str, str] | None = None,
) -> None:
    """Make the current pytest process local-only before application imports."""
    target = os.environ if environment is None else environment
    for key in PROVIDER_ENVIRONMENT_KEYS:
        target.pop(key, None)
    target.update(
        {
            "BILLING_ENABLED": "false",
            "DATABASE_URL": database_url,
            "EMAIL_ENABLED": "false",
            "ENVIRONMENT": "development",
            "SIGNUPFLOW_LOAD_DOTENV": "false",
            "SIGNUPFLOW_TEST_DATABASE_URL": database_url,
            "SMS_ENABLED": "false",
            "TESTING": "true",
        }
    )


def build_test_environment(
    source: Mapping[str, str],
    *,
    database_url: str,
    secret_key: str,
) -> dict[str, str]:
    """Return the allowlisted environment for an owned local app subprocess."""
    environment = {key: value for key, value in source.items() if key in RUNTIME_ENVIRONMENT_KEYS}
    environment.update(
        {
            "BILLING_ENABLED": "false",
            "DATABASE_URL": database_url,
            "EMAIL_ENABLED": "false",
            "ENVIRONMENT": "development",
            "SECRET_KEY": secret_key,
            "SIGNUPFLOW_DB": database_url,
            "SIGNUPFLOW_LOAD_DOTENV": "false",
            "SMS_ENABLED": "false",
        }
    )
    return environment
