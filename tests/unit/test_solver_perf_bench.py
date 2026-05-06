"""Solver performance benchmark — Sprint 6 PR 6.4.

Synthetic workload: 1000 events × 500 people, ~3 roles per event, average
5 availability windows per person.

Runs the solver ``N_ITERATIONS`` times, computes p95 of ``solve_ms``, and
asserts it is under ``SLO_P95_MS``. Marked slow so ``make test-unit-fast``
skips it; CI's ``make test-unit`` runs it.

This is a regression guard, not a tuned benchmark — wall-clock numbers
will vary by machine. The threshold is sized so legitimate fluctuations
on dev hardware do not flake CI, while still catching order-of-magnitude
regressions.

The calibrated p95 from the developer laptop is recorded in
``specs/020-solver-quality-changemin/spec.md``.
"""

from __future__ import annotations

import math
import random
from datetime import date, datetime, timedelta

import pytest

from api.core.models import (
    Availability,
    Event,
    Org,
    OrgDefaults,
    Person,
    RequiredRole,
    VacationPeriod,
)
from api.core.solver.adapter import SolveContext
from api.core.solver.heuristics import GreedyHeuristicSolver

# Workload size — matches the spec's stated synthetic workload.
N_EVENTS = 1000
N_PEOPLE = 500
ROLES_PER_EVENT = 3
AVAIL_WINDOWS_PER_PERSON = 5
N_ITERATIONS = 5

# Per-spec SLO. Generous to avoid CI flakes on shared runners; the actual
# calibrated number on a local M-series laptop is recorded in spec.md.
SLO_P95_MS = 15000.0


def _build_synthetic_context(*, seed: int) -> SolveContext:
    """Construct a deterministic synthetic SolveContext from ``seed``."""
    rng = random.Random(seed)

    role_pool = [f"role{i}" for i in range(8)]
    people: list[Person] = []
    for i in range(N_PEOPLE):
        # Each person gets 1-4 roles drawn from the pool.
        n_roles = rng.randint(1, 4)
        person_roles = rng.sample(role_pool, n_roles)
        people.append(
            Person(id=f"p{i}", name=f"Person {i}", roles=person_roles, skills=[], teams=[])
        )

    start_date = date(2026, 6, 1)
    days_window = 90  # spread events across ~3 months
    events: list[Event] = []
    for i in range(N_EVENTS):
        day_offset = rng.randint(0, days_window - 1)
        event_date = start_date + timedelta(days=day_offset)
        start = datetime.combine(event_date, datetime.min.time().replace(hour=10))
        end = start + timedelta(hours=1)
        # Pick 3 distinct roles for this event from the pool.
        evt_roles = rng.sample(role_pool, ROLES_PER_EVENT)
        required = [RequiredRole(role=r, count=1) for r in evt_roles]
        events.append(
            Event(id=f"e{i}", type="service", start=start, end=end, required_roles=required)
        )

    # Build availability: each person has AVAIL_WINDOWS_PER_PERSON random
    # vacation periods of 1-3 days each within the schedule window. This is
    # the closest analogue to "availability windows" in the existing model.
    availability: list[Availability] = []
    for person in people:
        vacations: list[VacationPeriod] = []
        for _ in range(AVAIL_WINDOWS_PER_PERSON):
            day_offset = rng.randint(0, days_window - 4)
            length = rng.randint(0, 2)  # 1-3 days inclusive
            vac_start = start_date + timedelta(days=day_offset)
            vac_end = vac_start + timedelta(days=length)
            vacations.append(VacationPeriod(start=vac_start, end=vac_end))
        availability.append(Availability(person_id=person.id, vacations=vacations))

    return SolveContext(
        org=Org(org_id="bench", region="US", defaults=OrgDefaults()),
        people=people,
        teams=[],
        resources=[],
        events=events,
        constraints=[],
        availability=availability,
        holidays=[],
        from_date=start_date,
        to_date=start_date + timedelta(days=days_window),
        mode="strict",
        change_min=False,
    )


def _percentile(values: list[float], p: float) -> float:
    """Return the p-th percentile of ``values`` using nearest-rank method."""
    sorted_vals = sorted(values)
    rank = max(1, math.ceil(p / 100.0 * len(sorted_vals)))
    return sorted_vals[rank - 1]


@pytest.mark.slow
def test_solver_perf_p95_under_slo(capsys):
    """Bench ``GreedyHeuristicSolver`` on a synthetic 1000×500 workload."""
    timings_ms: list[float] = []

    for i in range(N_ITERATIONS):
        ctx = _build_synthetic_context(seed=42 + i)
        solver = GreedyHeuristicSolver()
        solver.build_model(ctx)
        result = solver.solve()
        timings_ms.append(result.metrics.solve_ms)

    p50 = _percentile(timings_ms, 50)
    p95 = _percentile(timings_ms, 95)
    p99 = _percentile(timings_ms, 99)

    # Print to stdout — visible when running with `-s` or in CI logs via capsys.
    with capsys.disabled():
        print(
            f"\n[solver-perf] iterations={N_ITERATIONS} "
            f"events={N_EVENTS} people={N_PEOPLE} "
            f"roles_per_event={ROLES_PER_EVENT} "
            f"avail_per_person={AVAIL_WINDOWS_PER_PERSON}"
        )
        print(
            f"[solver-perf] solve_ms p50={p50:.1f} p95={p95:.1f} p99={p99:.1f} "
            f"slo_p95={SLO_P95_MS:.0f}"
        )

    assert (
        p95 < SLO_P95_MS
    ), f"solver p95 {p95:.1f}ms exceeds SLO {SLO_P95_MS:.0f}ms — perf regression"
