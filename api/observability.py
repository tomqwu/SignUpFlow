"""Optional error reporting that fails closed without exposing configuration."""

from __future__ import annotations

import hashlib
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from api.logging_config import logger


class ObservabilityConfigurationError(RuntimeError):
    """Raised when an explicitly configured reporting sink cannot initialize."""


@dataclass(frozen=True)
class ErrorReportingState:
    enabled: bool
    provider: str
    reason: str


_state = ErrorReportingState(enabled=False, provider="none", reason="not_configured")
_dsn_fingerprint: str | None = None


def initialize_error_reporting(
    environ: Mapping[str, str] | None = None,
    *,
    sdk_client: Any | None = None,
    integrations: Sequence[Any] | None = None,
) -> ErrorReportingState:
    """Initialize Sentry once when configured; never log or return its DSN."""
    global _dsn_fingerprint, _state

    values = os.environ if environ is None else environ
    dsn = values.get("SENTRY_DSN", "").strip()
    if not dsn:
        state = ErrorReportingState(
            enabled=False,
            provider="none",
            reason="not_configured",
        )
        if sdk_client is None:
            _state = state
            _dsn_fingerprint = None
        return state

    client = sentry_sdk if sdk_client is None else sdk_client
    fingerprint = hashlib.sha256(dsn.encode("utf-8")).hexdigest()
    if sdk_client is None and _state.enabled and _dsn_fingerprint == fingerprint:
        return _state

    resolved_integrations = (
        list(integrations)
        if integrations is not None
        else [FastApiIntegration(), SqlalchemyIntegration()]
    )
    try:
        client.init(
            dsn=dsn,
            environment=values.get("ENVIRONMENT", "development"),
            release=values.get("RELEASE_SHA", "unknown"),
            send_default_pii=False,
            traces_sample_rate=0.0,
            integrations=resolved_integrations,
        )
    except Exception as exc:
        logger.error(
            "error_reporting.configuration_failed",
            extra={
                "event": "error_reporting.configuration_failed",
                "error_type": type(exc).__name__,
            },
        )
        raise ObservabilityConfigurationError("Error reporting initialization failed") from exc

    state = ErrorReportingState(enabled=True, provider="sentry", reason="configured")
    if sdk_client is None:
        _state = state
        _dsn_fingerprint = fingerprint
    return state


def capture_unhandled_exception(error: Exception, *, sdk_client: Any | None = None) -> bool:
    """Capture one exception when enabled and make transport failures observable."""
    if sdk_client is None and not _state.enabled:
        return False
    client = sentry_sdk if sdk_client is None else sdk_client
    try:
        client.capture_exception(error)
    except Exception as exc:
        logger.error(
            "error_reporting.delivery_failed",
            extra={
                "event": "error_reporting.delivery_failed",
                "error_type": type(exc).__name__,
            },
        )
        return False
    return True
