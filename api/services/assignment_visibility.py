"""Shared publication boundary for member-facing schedule queries."""

from sqlalchemy import and_, or_
from sqlalchemy.sql.elements import ColumnElement

from api.models import Assignment, Solution


def member_visible_assignment(org_id: str) -> ColumnElement[bool]:
    """Manual assignments are immediate; solver assignments require publication."""
    return or_(
        Assignment.solution_id.is_(None),
        Assignment.solution.has(and_(Solution.org_id == org_id, Solution.is_published.is_(True))),
    )
