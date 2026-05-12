"""Sprint 10 PR A: ACCESS_TOKEN_EXPIRE_HOURS env knob.

api/security.py used to hardcode ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24.
Now it reads from ACCESS_TOKEN_EXPIRE_HOURS env (float, hours) at import.
This test reloads the module under a couple of env values to prove the
formula and the default behaviour.
"""

import importlib

import pytest

import api.security as security


@pytest.fixture
def reload_security(monkeypatch):
    """Yield a helper that sets ACCESS_TOKEN_EXPIRE_HOURS and reloads the
    security module so the new constant value takes effect. Restores the
    module on teardown."""

    def _reload(value: str | None):
        if value is None:
            monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_HOURS", raising=False)
        else:
            monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_HOURS", value)
        importlib.reload(security)
        return security.ACCESS_TOKEN_EXPIRE_MINUTES

    yield _reload
    # Cleanup: restore to the default by reloading without the var set.
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_HOURS", raising=False)
    importlib.reload(security)


def test_default_is_24_hours_when_env_unset(reload_security):
    assert reload_security(None) == 60 * 24


def test_integer_hours_via_env(reload_security):
    assert reload_security("1") == 60
    assert reload_security("12") == 60 * 12
    assert reload_security("48") == 60 * 48


def test_fractional_hours_supported_for_smoke(reload_security):
    """Sub-hour values are needed by the mobile/SMOKE.md refresh smoke
    so the access token expires within a single smoke walk."""
    # 0.05h = 3 min
    assert reload_security("0.05") == 3
    # 0.5h = 30 min
    assert reload_security("0.5") == 30
