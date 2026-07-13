"""Invariants for `tests/e2e/_helpers` date utilities.

These lock in the properties the e2e-lane relies on:
- `next_sunday_iso()` returns a Sunday at least 7 days in the future.
- `solver_window_around(seed)` returns (from, to) that comfortably
  brackets `seed` so the seed always falls inside the solver window.
"""

from __future__ import annotations

from datetime import date

from tests.e2e._helpers import next_sunday_iso, solver_window_around


def test_next_sunday_iso_is_a_future_sunday():
    seed = date.fromisoformat(next_sunday_iso())
    assert seed.weekday() == 6, "helper must return a Sunday"
    assert (seed - date.today()).days >= 7, "helper must return a date at least 7 days from today"


def test_solver_window_brackets_seed():
    seed_iso = next_sunday_iso()
    seed = date.fromisoformat(seed_iso)
    from_iso, to_iso = solver_window_around(seed_iso)
    from_d = date.fromisoformat(from_iso)
    to_d = date.fromisoformat(to_iso)
    assert from_d < seed < to_d, "seed must fall strictly inside (from, to)"
    assert (seed - from_d).days >= 7, "from_date must be well before seed"
    assert (to_d - seed).days >= 7, "to_date must be well after seed"


def test_solver_window_deterministic_from_seed():
    from_a, to_a = solver_window_around("2026-08-02")
    from_b, to_b = solver_window_around("2026-08-02")
    assert (from_a, to_a) == (from_b, to_b)
    assert from_a == "2026-07-12"
    assert to_a == "2026-08-23"
