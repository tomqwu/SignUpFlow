"""Persisted scheduling rules map to the solver's explicit constraint model."""

from datetime import date, datetime, timedelta

import pytest

from api.core.constraints.persisted import (
    PersistedConstraintError,
    map_persisted_constraint,
)
from api.core.models import ConstraintBinding, Event, Person, RequiredRole
from api.core.solver.heuristics import GreedyHeuristicSolver
from tests.unit.test_solver_rrule_honoring import _ctx_with, _solve

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("predicate", "severity", "weight", "params", "action_field"),
    [
        (
            "max_assignments",
            "hard",
            None,
            {"period": "P7D", "max_count": 2, "applies_to": ["service"]},
            "enforce_cap",
        ),
        (
            "min_gap_hours",
            "hard",
            None,
            {"min_hours": 12, "applies_to": ["service", "game"]},
            "enforce_min_gap_hours",
        ),
        (
            "cooldown",
            "soft",
            25,
            {"cooldown_days": 7},
            "penalize_if",
        ),
    ],
)
def test_supported_persisted_rule_mapping(
    predicate: str,
    severity: str,
    weight: int | None,
    params: dict,
    action_field: str,
):
    binding = map_persisted_constraint(
        key="saved-rule",
        severity=severity,
        weight=weight,
        predicate=predicate,
        params=params,
    )

    assert binding.key == "saved-rule"
    assert binding.scope == "person"
    assert binding.applies_to == params.get("applies_to", ["*"])
    assert getattr(binding.then, action_field) is not None


def test_rest_mapping_matches_cli_binding_shape():
    rest_binding = map_persisted_constraint(
        key="weekly-cap",
        severity="hard",
        weight=None,
        predicate="max_assignments",
        params={"period": "P7D", "max_count": 2, "applies_to": ["service"]},
    )
    cli_binding = ConstraintBinding.model_validate(
        {
            "key": "weekly-cap",
            "scope": "person",
            "applies_to": ["service"],
            "severity": "hard",
            "then": {"enforce_cap": {"period": "P7D", "max_count": 2}},
        }
    )

    assert rest_binding == cli_binding


@pytest.mark.parametrize(
    ("predicate", "severity", "weight", "params", "message"),
    [
        ("python_expression", "hard", None, {}, "unsupported predicate"),
        ("max_assignments", "hard", None, {"period": "weekly", "max_count": 2}, "period"),
        ("max_assignments", "hard", None, {"period": "P7D", "max_count": 0}, "max_count"),
        ("min_gap_hours", "soft", 5, {"min_hours": 12}, "only supports hard"),
        ("cooldown", "hard", None, {"cooldown_days": 7}, "only supports soft"),
        ("cooldown", "soft", 0, {"cooldown_days": 7}, "weight"),
        ("cooldown", "soft", 10, {"cooldown_days": 7, "extra": True}, "unsupported params"),
        ("cooldown", "soft", 10, {"cooldown_days": 7, "applies_to": []}, "applies_to"),
    ],
)
def test_invalid_persisted_rules_fail_explicitly(
    predicate: str,
    severity: str,
    weight: int | None,
    params: dict,
    message: str,
):
    with pytest.raises(PersistedConstraintError, match=message):
        map_persisted_constraint(
            key="bad-rule",
            severity=severity,
            weight=weight,
            predicate=predicate,
            params=params,
        )


def test_min_gap_compares_candidate_with_existing_assignment():
    start = datetime(2030, 1, 6, 10)
    person = Person(id="alex", name="Alex", roles=["volunteer"], skills=[], teams=[])
    events = [
        Event(
            id="early",
            type="service",
            start=start,
            end=start + timedelta(hours=1),
            required_roles=[RequiredRole(role="volunteer", count=1)],
        ),
        Event(
            id="late",
            type="service",
            start=start + timedelta(hours=3),
            end=start + timedelta(hours=4),
            required_roles=[RequiredRole(role="volunteer", count=1)],
        ),
    ]
    constraint = map_persisted_constraint(
        key="twelve-hour-rest",
        severity="hard",
        weight=None,
        predicate="min_gap_hours",
        params={"min_hours": 12},
    )
    context = _ctx_with(
        people=[person],
        events=events,
        availability=[],
        from_date=date(2030, 1, 6),
        to_date=date(2030, 1, 6),
    )
    context.constraints = [constraint]

    result = _solve(context)

    by_event = {assignment.event_id: assignment.assignees for assignment in result.assignments}
    assert by_event["early"] == ["alex"]
    assert by_event["late"] == []


def test_soft_cooldown_can_change_candidate_ranking():
    start = datetime(2030, 1, 6, 10)
    people = [
        Person(id="alex", name="Alex", roles=["lead", "volunteer"], skills=[], teams=[]),
        Person(id="blair", name="Blair", roles=["volunteer"], skills=[], teams=[]),
    ]
    events = [
        Event(
            id="lead",
            type="service",
            start=start,
            end=start + timedelta(hours=1),
            required_roles=[RequiredRole(role="lead", count=1)],
        ),
        Event(
            id="general",
            type="service",
            start=start + timedelta(days=1),
            end=start + timedelta(days=1, hours=1),
            required_roles=[RequiredRole(role="volunteer", count=1)],
        ),
    ]
    constraint = map_persisted_constraint(
        key="rotation",
        severity="soft",
        weight=150,
        predicate="cooldown",
        params={"cooldown_days": 7},
    )
    baseline_context = _ctx_with(
        people=people,
        events=events,
        availability=[],
        from_date=start.date(),
        to_date=(start + timedelta(days=1)).date(),
    )
    constrained_context = _ctx_with(
        people=people,
        events=events,
        availability=[],
        from_date=start.date(),
        to_date=(start + timedelta(days=1)).date(),
    )
    constrained_context.constraints = [constraint]

    def solve_with_published_preference(context):
        solver = GreedyHeuristicSolver()
        solver.build_model(context)
        solver.enable_change_minimization(True, 100)
        solver.set_prior_published_keys({("general", "alex")})
        return solver.solve()

    baseline = solve_with_published_preference(baseline_context)
    constrained = solve_with_published_preference(constrained_context)

    baseline_by_event = {a.event_id: a.assignees for a in baseline.assignments}
    constrained_by_event = {a.event_id: a.assignees for a in constrained.assignments}
    assert baseline_by_event["general"] == ["alex"]
    assert constrained_by_event["general"] == ["blair"]
