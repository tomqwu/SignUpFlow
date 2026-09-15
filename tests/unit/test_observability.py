"""Local observability contracts without contacting an external sink."""

from __future__ import annotations

import logging

import pytest

from api import database
from api.observability import (
    ObservabilityConfigurationError,
    capture_unhandled_exception,
    initialize_error_reporting,
)


class FakeSDK:
    def __init__(
        self, *, init_error: Exception | None = None, capture_error: Exception | None = None
    ):
        self.init_error = init_error
        self.capture_error = capture_error
        self.init_calls = []
        self.captured = []

    def init(self, **kwargs):
        self.init_calls.append(kwargs)
        if self.init_error:
            raise self.init_error

    def capture_exception(self, error):
        self.captured.append(error)
        if self.capture_error:
            raise self.capture_error


def test_no_dsn_is_explicitly_disabled_without_initializing_sdk():
    sdk = FakeSDK()

    state = initialize_error_reporting(
        {"ENVIRONMENT": "production", "RELEASE_SHA": "abc123"}, sdk_client=sdk
    )

    assert state.enabled is False
    assert state.reason == "not_configured"
    assert sdk.init_calls == []


def test_configured_sdk_disables_pii_and_records_environment_and_release():
    sdk = FakeSDK()

    state = initialize_error_reporting(
        {
            "ENVIRONMENT": "production",
            "RELEASE_SHA": "abc123",
            "SENTRY_DSN": "https://public@example.invalid/1",
        },
        sdk_client=sdk,
        integrations=[],
    )

    assert state.enabled is True
    assert state.provider == "sentry"
    assert sdk.init_calls == [
        {
            "dsn": "https://public@example.invalid/1",
            "environment": "production",
            "release": "abc123",
            "send_default_pii": False,
            "traces_sample_rate": 0.0,
            "integrations": [],
        }
    ]


def test_invalid_reporting_configuration_fails_without_logging_dsn(caplog):
    secret = "https://private-token@example.invalid/1"
    sdk = FakeSDK(init_error=ValueError(secret))

    with caplog.at_level(logging.ERROR, logger="rostio"):
        with pytest.raises(
            ObservabilityConfigurationError,
            match="Error reporting initialization failed",
        ):
            initialize_error_reporting(
                {"ENVIRONMENT": "production", "SENTRY_DSN": secret},
                sdk_client=sdk,
                integrations=[],
            )

    assert secret not in caplog.text


def test_capture_failure_is_observable_without_propagating_sensitive_error(caplog):
    sdk = FakeSDK(capture_error=RuntimeError("token=private"))

    with caplog.at_level(logging.ERROR, logger="rostio"):
        delivered = capture_unhandled_exception(RuntimeError("request failed"), sdk_client=sdk)

    assert delivered is False
    assert len(sdk.captured) == 1
    assert "private" not in caplog.text
    assert "error_reporting.delivery_failed" in caplog.text


def test_database_access_emits_no_fatal_debug_noise(monkeypatch, caplog):
    class FakeSession:
        def close(self):
            return None

    with monkeypatch.context() as scoped_patch:
        scoped_patch.setattr(database, "SessionLocal", FakeSession)
        scoped_patch.setattr(database, "DATABASE_URL", "postgresql://db/signupflow")
        scoped_patch.setattr(database, "_verify_migration_head", lambda _engine: None)
        dependency = database.get_db()

        with caplog.at_level(logging.CRITICAL, logger="rostio"):
            assert isinstance(next(dependency), FakeSession)
            dependency.close()
            database.init_db()

    assert not [record for record in caplog.records if record.levelno >= logging.CRITICAL]
