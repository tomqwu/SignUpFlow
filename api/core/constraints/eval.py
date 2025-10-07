"""Constraint evaluation engine."""

from typing import Any

from api.core.constraints.dsl import ConstraintResult, EvalContext
from api.core.constraints.predicates import (
    is_day_of_week,
    is_friday_or_monday,
    is_long_weekend,
)
from api.core.models import ConstraintBinding, PredicateNode


def evaluate_predicate(node: PredicateNode, ctx: EvalContext) -> bool:
    """Recursively evaluate predicate tree."""
    if node.any_:
        return any(evaluate_predicate(child, ctx) for child in node.any_)
    if node.all_:
        return all(evaluate_predicate(child, ctx) for child in node.all_)

    # Leaf predicate
    if node.predicate == "is_long_weekend":
        return is_long_weekend(ctx)
    elif node.predicate == "is_day_of_week":
        day = node.params.get("day", "")
        return is_day_of_week(ctx, day)
    elif node.predicate == "is_friday_or_monday":
        return is_friday_or_monday(ctx)

    return False


def evaluate_constraint(binding: ConstraintBinding, ctx: EvalContext) -> ConstraintResult:
    """Evaluate a constraint binding against context."""
    # Check when clause
    if binding.when:
        if not evaluate_predicate(binding.when, ctx):
            return ConstraintResult(satisfied=True, reason="when clause not matched")

    # Evaluate action
    action = binding.then

    if action.forbid_if:
        # Check forbid conditions
        if action.forbid_if == "is_friday_or_monday":
            if is_friday_or_monday(ctx):
                return ConstraintResult(
                    satisfied=False,
                    penalty=1000.0 if binding.severity == "hard" else float(binding.weight or 10),
                    reason=f"Event on {ctx.date} forbidden: {action.forbid_if}",
                )

    if action.require_roles and ctx.event:
        # Check role coverage
        if not ctx.assignments:
            return ConstraintResult(satisfied=False, reason="No assignments available")

        event_assignees = ctx.assignments.get(ctx.event.id, [])
        if not ctx.all_people:
            return ConstraintResult(satisfied=False, reason="No people data available")

        people_map = {p.id: p for p in ctx.all_people}

        for req_role in action.require_roles:
            count = sum(
                1
                for pid in event_assignees
                if pid in people_map and req_role.role in people_map[pid].roles
            )
            if count < req_role.count:
                return ConstraintResult(
                    satisfied=False,
                    penalty=1000.0 if binding.severity == "hard" else float(binding.weight or 10),
                    reason=f"Role {req_role.role} needs {req_role.count}, has {count}",
                )

    if action.enforce_min_gap_hours is not None and ctx.person:
        from api.core.constraints.predicates import min_gap_hours_satisfied

        if not min_gap_hours_satisfied(ctx, ctx.person.id, action.enforce_min_gap_hours):
            return ConstraintResult(
                satisfied=False,
                penalty=1000.0 if binding.severity == "hard" else float(binding.weight or 10),
                reason=f"Min gap {action.enforce_min_gap_hours}h violated",
            )

    if action.enforce_cap and ctx.person:
        from datetime import timedelta

        from api.core.constraints.predicates import count_assignments_in_period

        period = action.enforce_cap.get("period", "P1M")
        max_count = action.enforce_cap.get("max_count", 999)

        # Simple monthly cap
        if period == "P1M" and ctx.date:
            month_start = ctx.date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            count = count_assignments_in_period(ctx, ctx.person.id, month_start, month_end)
            if count >= max_count:
                return ConstraintResult(
                    satisfied=False,
                    penalty=1000.0 if binding.severity == "hard" else float(binding.weight or 10),
                    reason=f"Cap {max_count} reached in period {period}",
                )

    if action.penalize_if and binding.severity == "soft":
        # Soft constraint penalties
        penalty_type = action.penalize_if.get("type")

        if penalty_type == "cooldown" and ctx.person and ctx.date:
            from api.core.constraints.predicates import last_assignment_days_ago

            cooldown_days = action.penalize_if.get("cooldown_days", 14)
            days_ago = last_assignment_days_ago(ctx, ctx.person.id, ctx.date)
            if days_ago is not None and days_ago < cooldown_days:
                penalty = float(binding.weight or 10) * (cooldown_days - days_ago) / cooldown_days
                return ConstraintResult(
                    satisfied=False,
                    penalty=penalty,
                    reason=f"Cooldown violation: {days_ago} < {cooldown_days} days",
                )

        if penalty_type == "recent_rotation" and ctx.person and ctx.date:
            from api.core.constraints.predicates import last_assignment_days_ago

            lookback = action.penalize_if.get("lookback_days", 30)
            days_ago = last_assignment_days_ago(ctx, ctx.person.id, ctx.date)
            if days_ago is not None and days_ago < lookback:
                penalty = float(binding.weight or 10) * (lookback - days_ago) / lookback
                return ConstraintResult(
                    satisfied=False,
                    penalty=penalty,
                    reason=f"Recent rotation: {days_ago} < {lookback} days",
                )

    return ConstraintResult(satisfied=True)
