"""Compute stability metrics for a fresh solve against the org's published baseline.

Sprint 6 PR 6.1 turns ``StabilityMetrics`` from a zero-stub into a real
signal. The diff is computed using the same ``(event_id, person_id, role)``
key shape as the ``GET /solutions/{a}/compare/{b}`` endpoint added in Sprint
5 PR 5.5 (see ``api/routers/solutions.py::compare_solutions``).

Note on role: the solver currently writes ``Assignment.role = NULL`` because
the in-memory ``api.core.models.Assignment`` does not carry per-assignee
roles. So a freshly-solved key always looks like ``(event_id, person_id,
None)``. If a prior published solution has rows with non-null roles, those
rows will compare as different from the new ``role=None`` rows — that is
intentional: a role change is a real assignment change.
"""

from sqlalchemy.orm import Session

from api.core.models import Assignment as CoreAssignment
from api.core.models import StabilityMetrics
from api.models import Assignment as DBAssignment
from api.models import Solution


def compute_stability_metrics(
    db: Session,
    *,
    org_id: str,
    new_assignments: list[CoreAssignment],
) -> StabilityMetrics:
    """Diff ``new_assignments`` against the org's currently-published solution.

    Returns ``StabilityMetrics(0, 0)`` when no solution is published in the org.
    """
    published = (
        db.query(Solution)
        .filter(Solution.org_id == org_id, Solution.is_published.is_(True))
        .first()
    )
    if published is None:
        return StabilityMetrics()

    prior_rows = db.query(DBAssignment).filter(DBAssignment.solution_id == published.id).all()
    prior_keys: set[tuple[str, str, str | None]] = {
        (
            str(r.event_id),
            str(r.person_id),
            str(r.role) if r.role is not None else None,
        )
        for r in prior_rows
    }

    new_keys: set[tuple[str, str, str | None]] = {
        (a.event_id, person_id, None) for a in new_assignments for person_id in a.assignees
    }

    sym_diff = prior_keys.symmetric_difference(new_keys)
    affected = {person_id for (_, person_id, _) in sym_diff}

    return StabilityMetrics(
        moves_from_published=len(sym_diff),
        affected_persons=len(affected),
    )
