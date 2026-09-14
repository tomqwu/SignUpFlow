from datetime import datetime

import pytest

from api.timeutils import utcnow

pytestmark = pytest.mark.unit


def test_test_clock_requires_explicit_subprocess_allowance(monkeypatch):
    monkeypatch.setenv("SIGNUPFLOW_TEST_NOW", "2030-01-09T12:00:00+00:00")
    monkeypatch.delenv("SIGNUPFLOW_ALLOW_TEST_CLOCK", raising=False)

    assert utcnow() != datetime(2030, 1, 9, 12)


def test_explicit_test_clock_is_returned_as_naive_utc(monkeypatch):
    monkeypatch.setenv("SIGNUPFLOW_ALLOW_TEST_CLOCK", "true")
    monkeypatch.setenv("SIGNUPFLOW_TEST_NOW", "2030-01-09T07:00:00-05:00")

    assert utcnow() == datetime(2030, 1, 9, 12)
