"""Marathon P3.19 — JWT SECRET_KEY launch-readiness guard."""

from __future__ import annotations

from api.security import _DEFAULT_SECRET_KEY, secret_key_issues


def test_default_key_flagged():
    issues = secret_key_issues(_DEFAULT_SECRET_KEY)
    assert any("default" in i for i in issues)


def test_short_key_flagged():
    issues = secret_key_issues("too-short")
    assert any("too short" in i for i in issues)


def test_strong_unique_key_ok():
    assert secret_key_issues("k" * 48) == []
