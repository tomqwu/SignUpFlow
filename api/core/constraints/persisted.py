"""Validated mapping from database constraint rows to solver bindings."""

from __future__ import annotations

import re
from typing import Any

from api.core.models import ConstraintAction, ConstraintBinding

SUPPORTED_PERSISTED_CONSTRAINTS = {
    "max_assignments": {
        "severity": "hard",
        "params": ["period", "max_count", "applies_to"],
        "description": "Limit assignments in a calendar month or rolling day window.",
    },
    "min_gap_hours": {
        "severity": "hard",
        "params": ["min_hours", "applies_to"],
        "description": "Require rest time between a candidate event and prior assignments.",
    },
    "cooldown": {
        "severity": "soft",
        "params": ["cooldown_days", "applies_to"],
        "description": "Prefer people who have not served recently.",
    },
}

_ROLLING_PERIOD = re.compile(r"P[1-9][0-9]*D")


class PersistedConstraintError(ValueError):
    """A database constraint cannot be represented by the supported solver contract."""


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise PersistedConstraintError(f"{field} must be a positive integer")
    return int(value)


def _applies_to(params: dict[str, Any]) -> list[str]:
    value = params.get("applies_to", ["*"])
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise PersistedConstraintError("applies_to must be a non-empty list of event types")
    return list(dict.fromkeys(item.strip() for item in value))


def _validate_common(
    *, severity: str, weight: int | None, predicate: str, params: dict[str, Any]
) -> None:
    definition = SUPPORTED_PERSISTED_CONSTRAINTS.get(predicate)
    if definition is None:
        supported = ", ".join(SUPPORTED_PERSISTED_CONSTRAINTS)
        raise PersistedConstraintError(
            f"unsupported predicate {predicate!r}; supported predicates: {supported}"
        )
    if severity != definition["severity"]:
        raise PersistedConstraintError(
            f"{predicate} only supports {definition['severity']} constraints"
        )
    if weight is not None and (
        isinstance(weight, bool) or not isinstance(weight, int) or weight <= 0
    ):
        raise PersistedConstraintError("weight must be a positive integer")
    if severity == "soft" and weight is None:
        raise PersistedConstraintError("soft constraints require a positive weight")
    if not isinstance(params, dict):
        raise PersistedConstraintError("params must be an object")
    allowed = set(definition["params"])
    extra = sorted(set(params) - allowed)
    if extra:
        raise PersistedConstraintError(f"unsupported params for {predicate}: {', '.join(extra)}")


def map_persisted_constraint(
    *,
    key: str,
    severity: str,
    weight: int | None,
    predicate: str,
    params: dict[str, Any] | None,
) -> ConstraintBinding:
    """Map one validated database rule to an executable solver binding."""
    values = params or {}
    _validate_common(
        severity=severity,
        weight=weight,
        predicate=predicate,
        params=values,
    )
    applies_to = _applies_to(values)

    if predicate == "max_assignments":
        period = values.get("period")
        if period != "P1M" and (
            not isinstance(period, str) or not _ROLLING_PERIOD.fullmatch(period)
        ):
            raise PersistedConstraintError(
                "period must be P1M or a positive rolling period such as P7D"
            )
        action = ConstraintAction(
            enforce_cap={
                "period": period,
                "max_count": _positive_int(values.get("max_count"), "max_count"),
            }
        )
    elif predicate == "min_gap_hours":
        action = ConstraintAction(
            enforce_min_gap_hours=_positive_int(values.get("min_hours"), "min_hours")
        )
    else:
        action = ConstraintAction(
            penalize_if={
                "type": "cooldown",
                "cooldown_days": _positive_int(values.get("cooldown_days"), "cooldown_days"),
            }
        )

    return ConstraintBinding(
        key=key,
        scope="person",
        applies_to=applies_to,
        then=action,
        severity=severity,
        weight=weight,
    )


def map_database_constraints(rows: list[Any]) -> list[ConstraintBinding]:
    """Map ORM-like rows while retaining each rule key in validation errors."""
    bindings = []
    for row in rows:
        try:
            bindings.append(
                map_persisted_constraint(
                    key=row.key,
                    severity=row.type,
                    weight=row.weight,
                    predicate=row.predicate,
                    params=row.params,
                )
            )
        except PersistedConstraintError as exc:
            raise PersistedConstraintError(f"Constraint {row.key!r}: {exc}") from exc
    return bindings
