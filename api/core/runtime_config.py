"""Small fail-closed boundary for effective production environment settings."""

from __future__ import annotations

import math
import os
import re
from collections.abc import Mapping
from ipaddress import ip_network
from urllib.parse import urlsplit

DEFAULT_SECRET_KEY = "your-secret-key-change-in-production-use-env-var"
KNOWN_SAMPLE_SECRET_KEYS = frozenset(
    {
        DEFAULT_SECRET_KEY,
        "change-this-to-a-random-secret-key-in-production",
        "your-secret-key-min-32-chars-CHANGE-IN-PRODUCTION",
        "dev-secret-key-change-in-production",
        "changeme_min_32_chars_for_jwt_signing",
    }
)
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "no", "off"})
_BOOLEAN_SETTINGS = (
    "TESTING",
    "DEBUG",
    "DEBUG_RETURN_RESET_TOKEN",
    "DISABLE_RATE_LIMITS",
    "DISABLE_USAGE_LIMITS",
    "SIGNUPFLOW_ALLOW_TEST_CLOCK",
    "EMAIL_ENABLED",
    "SMS_ENABLED",
    "BILLING_ENABLED",
    "SECURITY_HSTS_ENABLED",
    "SECURITY_CSP_ENABLED",
)
_FORBIDDEN_PRODUCTION_FLAGS = (
    "TESTING",
    "DEBUG",
    "DEBUG_RETURN_RESET_TOKEN",
    "DISABLE_RATE_LIMITS",
    "DISABLE_USAGE_LIMITS",
    "SIGNUPFLOW_ALLOW_TEST_CLOCK",
)
_PLACEHOLDER_MARKERS = ("changeme", "placeholder", "your-secret", "change-in-production")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


class ProductionConfigurationError(RuntimeError):
    """Raised before startup when production settings are unsafe or incoherent."""


def secret_key_issues(secret_key: str) -> list[str]:
    """Return key defects without including the key value."""
    issues: list[str] = []
    if secret_key in KNOWN_SAMPLE_SECRET_KEYS:
        issues.append("SECRET_KEY is a known default or sample value")
    if secret_key != secret_key.strip():
        issues.append("SECRET_KEY must not have leading or trailing whitespace")
    if len(secret_key.strip()) < 32:
        issues.append("SECRET_KEY is too short; use at least 32 characters")
    return issues


def access_token_expire_minutes(environ: Mapping[str, str] | None = None) -> int:
    """Read and validate the canonical access-token lifetime."""
    values = os.environ if environ is None else environ
    raw = values.get("ACCESS_TOKEN_EXPIRE_HOURS", "24")
    try:
        hours = float(raw)
    except ValueError as exc:
        raise ValueError("ACCESS_TOKEN_EXPIRE_HOURS must be a number") from exc
    if not math.isfinite(hours) or hours <= 0:
        raise ValueError("ACCESS_TOKEN_EXPIRE_HOURS must be greater than zero")
    minutes = int(hours * 60)
    if minutes < 1:
        raise ValueError("ACCESS_TOKEN_EXPIRE_HOURS must be at least one minute")
    return minutes


def read_boolean_setting(
    name: str,
    environ: Mapping[str, str] | None = None,
    *,
    default: bool = False,
) -> bool:
    """Read one environment boolean using the production validator's vocabulary."""
    values = os.environ if environ is None else environ
    raw = values.get(name)
    if raw is None or not raw.strip():
        return default
    normalized = raw.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise ValueError(f"{name} must be true or false")


def is_production_environment(environ: Mapping[str, str] | None = None) -> bool:
    """Return whether the normalized runtime environment is production."""
    values = os.environ if environ is None else environ
    return values.get("ENVIRONMENT", "development").strip().lower() == "production"


def security_hsts_max_age(environ: Mapping[str, str] | None = None) -> int:
    """Read a positive HSTS lifetime without exposing its raw value."""
    values = os.environ if environ is None else environ
    raw = values.get("SECURITY_HSTS_MAX_AGE", "31536000")
    try:
        max_age = int(raw)
    except ValueError as exc:
        raise ValueError("SECURITY_HSTS_MAX_AGE must be an integer") from exc
    if max_age <= 0:
        raise ValueError("SECURITY_HSTS_MAX_AGE must be greater than zero")
    return max_age


def _https_origin(name: str, values: Mapping[str, str]) -> str:
    raw = values.get(name, "").strip()
    try:
        parsed = urlsplit(raw)
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid HTTPS origin") from exc
    if (
        parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(f"{name} must be an HTTPS origin without path, query, or credentials")
    authority = parsed.hostname.lower()
    if port is not None and port != 443:
        authority = f"{authority}:{port}"
    return f"https://{authority}"


def _validate_database(values: Mapping[str, str]) -> None:
    raw = values.get("DATABASE_URL", "").strip()
    try:
        parsed = urlsplit(raw)
    except ValueError as exc:
        raise ValueError("DATABASE_URL must be a valid PostgreSQL URL") from exc
    if parsed.scheme not in {"postgresql", "postgresql+psycopg", "postgresql+psycopg2"}:
        raise ValueError("DATABASE_URL must use PostgreSQL in production")
    if not parsed.hostname or not parsed.path.strip("/"):
        raise ValueError("DATABASE_URL must identify a PostgreSQL host and database")
    if any(marker in raw.lower() for marker in _PLACEHOLDER_MARKERS):
        raise ValueError("DATABASE_URL contains a known sample credential")


def _validate_rate_limit_storage(values: Mapping[str, str]) -> None:
    if values.get("RATE_LIMIT_STORAGE", "redis").strip().lower() != "redis":
        raise ValueError("RATE_LIMIT_STORAGE must be redis in production")
    raw = values.get("RATE_LIMIT_REDIS_URL") or values.get("REDIS_URL", "")
    raw = raw.strip()
    try:
        parsed = urlsplit(raw)
    except ValueError as exc:
        raise ValueError("REDIS_URL must be a valid Redis URL") from exc
    if parsed.scheme not in {"redis", "rediss"} or not parsed.hostname:
        raise ValueError("REDIS_URL must use redis or rediss and identify a host")
    if not parsed.password:
        raise ValueError("REDIS_URL must authenticate in production")
    if any(marker in raw.lower() for marker in _PLACEHOLDER_MARKERS):
        raise ValueError("REDIS_URL contains a known sample credential")


def _validate_event_bus_storage(values: Mapping[str, str]) -> None:
    if values.get("EVENT_BUS_STORAGE", "redis").strip().lower() != "redis":
        raise ValueError("EVENT_BUS_STORAGE must be redis in production")


def _validate_proxy_networks(values: Mapping[str, str]) -> None:
    configured = values.get("TRUSTED_PROXY_IPS", "").strip()
    if not configured:
        return
    try:
        networks = [
            ip_network(item.strip(), strict=False) for item in configured.split(",") if item.strip()
        ]
    except ValueError as exc:
        raise ValueError("TRUSTED_PROXY_IPS must contain valid IP addresses or CIDRs") from exc
    if not networks or any(network.prefixlen == 0 for network in networks):
        raise ValueError("TRUSTED_PROXY_IPS must not trust every address")


def _validate_enabled_providers(values: Mapping[str, str], enabled: Mapping[str, bool]) -> None:
    requirements = {
        "EMAIL_ENABLED": ("SENDGRID_API_KEY",),
        "SMS_ENABLED": (
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER",
            "TWILIO_INCOMING_SMS_URL",
            "TWILIO_STATUS_CALLBACK_URL",
        ),
        "BILLING_ENABLED": ("STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"),
    }
    for flag, required_names in requirements.items():
        if enabled[flag] and any(not values.get(name, "").strip() for name in required_names):
            joined = ", ".join(required_names)
            raise ValueError(f"{flag} requires {joined}")
    if enabled["SMS_ENABLED"]:
        for name in ("TWILIO_INCOMING_SMS_URL", "TWILIO_STATUS_CALLBACK_URL"):
            parsed = urlsplit(values[name].strip())
            if (
                parsed.scheme.lower() != "https"
                or not parsed.hostname
                or parsed.username is not None
                or parsed.password is not None
                or parsed.fragment
            ):
                raise ValueError(f"{name} must be a valid external HTTPS callback URL")


def _validate_observability(values: Mapping[str, str]) -> None:
    release_sha = values.get("RELEASE_SHA", "").strip()
    if not _GIT_SHA.fullmatch(release_sha):
        raise ValueError("RELEASE_SHA must be a 40-character lowercase Git SHA")
    raw_threshold = values.get("READINESS_FAILURE_ALERT_THRESHOLD", "3")
    try:
        threshold = int(raw_threshold)
    except ValueError as exc:
        raise ValueError("READINESS_FAILURE_ALERT_THRESHOLD must be an integer") from exc
    if threshold < 1:
        raise ValueError("READINESS_FAILURE_ALERT_THRESHOLD must be at least one")


def validate_production_environment(environ: Mapping[str, str] | None = None) -> None:
    """Reject unsafe production settings before database or network startup."""
    values = os.environ if environ is None else environ
    if not is_production_environment(values):
        return

    issues: list[str] = []
    issues.extend(secret_key_issues(values.get("SECRET_KEY", DEFAULT_SECRET_KEY)))
    try:
        access_token_expire_minutes(values)
    except ValueError as exc:
        issues.append(str(exc))
    try:
        security_hsts_max_age(values)
    except ValueError as exc:
        issues.append(str(exc))
    try:
        _validate_database(values)
    except ValueError as exc:
        issues.append(str(exc))
    try:
        _validate_rate_limit_storage(values)
    except ValueError as exc:
        issues.append(str(exc))
    try:
        _validate_event_bus_storage(values)
    except ValueError as exc:
        issues.append(str(exc))
    try:
        _validate_observability(values)
    except ValueError as exc:
        issues.append(str(exc))

    origins: dict[str, str] = {}
    for name in ("APP_URL", "API_BASE_URL", "FRONTEND_URL"):
        try:
            origins[name] = _https_origin(name, values)
        except ValueError as exc:
            issues.append(str(exc))

    cors_origins: list[str] = []
    raw_cors = values.get("CORS_ALLOWED_ORIGINS", "").strip()
    if not raw_cors:
        issues.append("CORS_ALLOWED_ORIGINS must list explicit production origins")
    else:
        for index, _raw_origin in enumerate(raw_cors.split(",")):
            synthetic_name = f"CORS_ALLOWED_ORIGINS[{index}]"
            synthetic_values = {synthetic_name: _raw_origin.strip()}
            try:
                cors_origins.append(_https_origin(synthetic_name, synthetic_values))
            except ValueError as exc:
                issues.append(str(exc))
    if origins.get("FRONTEND_URL") and origins["FRONTEND_URL"] not in cors_origins:
        issues.append("CORS_ALLOWED_ORIGINS must include FRONTEND_URL")

    enabled: dict[str, bool] = {}
    for name in _BOOLEAN_SETTINGS:
        default = name in {"SECURITY_HSTS_ENABLED", "SECURITY_CSP_ENABLED"}
        try:
            enabled[name] = read_boolean_setting(name, values, default=default)
        except ValueError as exc:
            issues.append(str(exc))

    for name in _FORBIDDEN_PRODUCTION_FLAGS:
        if enabled.get(name):
            issues.append(f"{name} must be false in production")
    for name in ("SECURITY_HSTS_ENABLED", "SECURITY_CSP_ENABLED"):
        if name in enabled and not enabled[name]:
            issues.append(f"{name} must be true in production")
    if values.get("LOCAL_EMAIL_CAPTURE_DIR", "").strip():
        issues.append("LOCAL_EMAIL_CAPTURE_DIR must be unset in production")

    try:
        _validate_proxy_networks(values)
    except ValueError as exc:
        issues.append(str(exc))
    if all(name in enabled for name in ("EMAIL_ENABLED", "SMS_ENABLED", "BILLING_ENABLED")):
        try:
            _validate_enabled_providers(values, enabled)
        except ValueError as exc:
            issues.append(str(exc))

    for name in ("POSTGRES_PASSWORD", "REDIS_PASSWORD", "REDIS_URL", "CELERY_BROKER_URL"):
        raw = values.get(name, "").lower()
        if raw and any(marker in raw for marker in _PLACEHOLDER_MARKERS):
            issues.append(f"{name} contains a known sample credential")

    if issues:
        details = "\n".join(f"- {issue}" for issue in dict.fromkeys(issues))
        raise ProductionConfigurationError(f"Invalid production configuration:\n{details}")
