# Feature Specification: Solver Quality + Change Minimization

**Feature Branch**: `020-solver-quality-changemin`
**Created**: 2026-05-06
**Status**: Draft
**Type**: Solver Quality / Backend

---

## Overview

**Purpose**: Activate the dormant change-minimization plumbing in the greedy solver, surface real stability metrics on every solve, and add a workload-cap fairness predicate. Turns the existing zero-stub `StabilityMetrics` into an actionable signal admins and the solver itself can use.

**Business Value**: When admins re-run the solver after publishing a schedule (e.g., to absorb a new vacation request), today the solver may reshuffle every assignment because nothing biases it toward the current published baseline. This causes unnecessary churn — volunteers see their assignments swap for no observable reason. Change-minimization preserves the published baseline where feasible while still respecting hard constraints.

**Target Users**: Admins re-solving after partial schedule changes; volunteers who benefit from stable assignments week-over-week.

---

## Background

The codebase already declares the contract:

- `api/core/models.py:177` — `StabilityMetrics` Pydantic model with `moves_from_published` and `affected_persons` fields.
- `api/core/solver/heuristics.py:33-34` — `change_min_enabled` / `change_min_weight` instance state.
- `api/core/solver/heuristics.py:288` — `enable_change_minimization(enabled, weight_move_published)` setter.
- `api/schemas/solver.py:16` — `SolveRequest.change_min: bool`.
- `api/routers/solver.py:134` — reads `change_min_weight` from `org.config`.

But none of the wires are connected:

- `solver.enable_change_minimization()` is never called from the router.
- `change_min_enabled` is never read inside the candidate-scoring loop.
- `StabilityMetrics()` returns hardcoded zeros.
- `change_min_weight` from `OrgDefaults` never reaches the solver instance.

Sprint 5 PR 5.5 added the `(event_id, person_id, role)` diff infrastructure (`api/routers/solutions.py::compare_solutions`). Sprint 6 reuses that exact key shape.

---

## Definitions

### `moves_from_published`

The number of `(event_id, person_id, role)` tuples that differ between the **current solve's assignments** and the **org's currently-published solution's assignments**, counted as `|added| + |removed|` (i.e., a person changing role on the same event counts as 2 moves, matching the compare endpoint).

When no solution is currently published in the org, `moves_from_published = 0`.

### `affected_persons`

The count of unique `person_id`s appearing in the symmetric difference (added ∪ removed). When no prior published exists, `0`.

### Change-minimization scoring contract

When `SolveRequest.change_min == True`:

1. Before the greedy loop runs, the router fetches `org`'s currently-published `Solution` and its `Assignment` rows.
2. Builds the loose prior-key set `P = {(event_id, person_id) for each Assignment}`.
3. Calls `solver.enable_change_minimization(enabled=True, weight=org_defaults.change_min_weight)` and `solver.set_prior_published_keys(P)`.
4. Inside `_assign_event`'s candidate scoring, each candidate `(event_id, person_id)` whose tuple is in `P` has its penalty reduced by `change_min_weight` (default 100, configurable per-org via `OrgDefaults.change_min_weight`). Lower penalty wins.
5. The bonus is applied only as a **tiebreaker among feasible candidates** — it never overrides hard-constraint rejections (vacation, exception dates, hard person-level constraints).

When `change_min == False` (the default), no bonus is applied. Stability metrics are still computed (so admins can see what *would* have happened with change-min off).

#### Loose vs. strict role match

The 6.1 stability metric uses a **strict** key — `(event_id, person_id, role)` — because it diffs at the DB level where role is the literal stored value. Different roles on the same `(event_id, person_id)` count as separate `removed`+`added` rows.

The 6.2 scoring bonus uses a **loose** key — `(event_id, person_id)` — because the solver writes `Assignment.role = NULL` when persisting (the in-memory `api.core.models.Assignment` does not carry per-assignee roles). A role-strict scoring match would never hit a candidate, defeating the purpose. When a future PR makes the solver role-aware, both can tighten to strict.

### Workload-cap predicate

A new constraint DSL predicate `workload_cap`:

```yaml
constraints:
  - key: weekly_volunteer_cap
    predicate: workload_cap
    severity: hard
    params:
      max_per_window_days: 7
      max_count: 2
```

Evaluates per `Person` over a rolling N-day window centered on each candidate event. Rejects (or penalizes, per `severity`) candidates that would exceed `max_count`. Reuses the existing constraint DSL evaluator (`api/core/constraints/eval.py`).

### Performance SLO target

- **Synthetic workload**: 1000 events × 500 people, ~3 roles per event, average 5 availability windows per person.
- **Target**: solve_ms p95 < 5000ms (5s) on a developer laptop (Apple M-series or equivalent).
- **Calibrated**: actual p95 number captured during PR 6.4 and updated here on merge.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Re-solve preserves published baseline (Priority: P1)

Admin solves and publishes a schedule. A new availability exception is added that affects 1 person on 1 event. Admin re-solves with `change_min=True`. The new solution moves only the affected person on that event; everyone else stays put.

**Why this priority**: P1 — this is the core value. Without it, change-min is theoretical.

**Independent Test**: Seed 4 people (`p1..p4`), 8 events with no constraints. Solve → publish. Add an `AvailabilityException` for `p1` on `e3`. Re-solve with `change_min=True`. Assert `moves_from_published <= 2` (the displaced p1 plus 1 replacement). Assert `affected_persons <= 2`.

**Acceptance Scenarios**:

1. **Given** a published solution and no constraint changes, **When** admin re-solves with `change_min=True`, **Then** `moves_from_published == 0` and the new solution is byte-equal to the published one.
2. **Given** a published solution and one new availability exception affecting one person, **When** admin re-solves with `change_min=True`, **Then** `moves_from_published <= 2` (the displaced + the replacement).
3. **Given** a published solution and `change_min=False`, **When** admin re-solves, **Then** the solution may differ wholesale from prior published; `moves_from_published` is reported but not minimized.

### User Story 2 — Workload cap rejects over-assignment (Priority: P2)

Admin sets a weekly volunteer cap of 2 events per 7-day window. Solver respects it as a hard constraint.

**Acceptance Scenarios**:

1. **Given** 7 events in one week and only one available volunteer, **When** solver runs with a `workload_cap(2,7)` hard constraint, **Then** at most 2 of those events are filled by that volunteer; the remaining 5 are unassigned with hard violations.
2. **Given** the same setup with `severity: soft`, **When** solver runs, **Then** all 7 are filled but at least 5 of them appear in `metrics.violations.soft`.

### User Story 3 — Stats endpoint exposes the metrics (Priority: P2)

Admin can call `GET /api/v1/solutions/{id}/stats` to retrieve fairness, stability, and workload distribution histograms for any solution in their org.

**Acceptance Scenarios**:

1. **Given** any solution, **When** admin GETs `/stats`, **Then** the response includes `fairness.histogram`, `stability.moves_from_published`, `workload.max_events_per_person`.
2. **Given** a volunteer caller, **When** they GET `/stats`, **Then** 403.

---

## Out of Scope

- Replacing the greedy heuristic with an exact solver (LP/CP/MILP).
- Multi-objective Pareto search across change-min vs fairness vs soft-violations.
- Locking individual assignments to prevent solver edits (that belongs in Sprint 7's manual-editing theme, spec 017).
- Frontend visualization of stats (`/stats` is a JSON API; the dashboard is downstream).

---

## Implementation Sequence (PR breakdown)

| PR     | Branch                                  | Scope                                                            |
| ------ | --------------------------------------- | ---------------------------------------------------------------- |
| 6.0    | `sprint-6-0-solver-quality-design`      | This spec doc.                                                   |
| 6.1    | `sprint-6-1-stability-metrics`          | Compute `moves_from_published` and `affected_persons` on solve.  |
| 6.2    | `sprint-6-2-change-min-scoring`         | Wire `change_min` through; add bonus to candidate scoring.       |
| 6.3    | `sprint-6-3-workload-cap-predicate`     | New `workload_cap` DSL predicate.                                |
| 6.4    | `sprint-6-4-solver-perf-bench`          | Synthetic perf benchmark; calibrate the SLO above.               |
| 6.5    | `sprint-6-5-solution-stats`             | `GET /solutions/{id}/stats` endpoint.                            |

---

## Verification (per PR)

Same gates as Sprint 5:

1. `poetry run black --check api tests`
2. `poetry run ruff check api tests`
3. Each test tier separately: `poetry run pytest tests/unit/`, `tests/api/`, `tests/cli/`, `tests/contract/`, `tests/integration/`.
4. If a route is added, refresh `tests/contract/openapi.snapshot.json` via `make update-openapi-snapshot`.
5. PR rule (`AGENTS.md`): commit, push, wait for CI green, merge — never bypass.
