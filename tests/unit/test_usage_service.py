from unittest.mock import MagicMock

import pytest

from api.services.usage_service import UsageService


@pytest.fixture(autouse=True)
def clear_usage_env(monkeypatch):
    """Ensure usage limit env flags do not leak between tests."""
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.delenv("DISABLE_USAGE_LIMITS", raising=False)


def _build_service():
    db = MagicMock()
    db.query = MagicMock()
    return UsageService(db), db


def test_can_add_volunteer_bypasses_limits_when_testing_env(monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    service, db = _build_service()

    assert service.can_add_volunteer("org-1") is True
    db.query.assert_not_called()


def test_can_add_volunteer_bypasses_limits_when_disable_env(monkeypatch):
    monkeypatch.setenv("DISABLE_USAGE_LIMITS", "TRUE")
    service, db = _build_service()

    assert service.can_add_volunteer("org-2") is True
    db.query.assert_not_called()


def test_can_add_volunteer_returns_false_when_org_missing():
    service, db = _build_service()

    (
        db.query.return_value.options.return_value.filter.return_value.first.return_value
    ) = None

    assert service.can_add_volunteer("missing-org") is False
    db.query.assert_called_once()
