"""Analytics endpoints for volunteer participation metrics."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_admin_user, verify_org_member
from api.models import Assignment, Event, Person, Solution
from api.timeutils import utcnow

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _in_last_days(days: int, now: datetime):
    """Events that started in [now - days, now]; published future work is not history.

    `Event.start_time` is stored as naive UTC, so `now` must come from `utcnow()`.
    """
    return Event.start_time.between(now - timedelta(days=days), now)


@router.get("/{org_id}/volunteer-stats")
def get_volunteer_stats(
    org_id: str,
    days: int = Query(
        30,
        description="Number of past days to analyze; the window ends now and excludes upcoming events",
    ),
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get volunteer participation statistics for events in the last `days` days.

    Counts only events that started between now - `days` and now; a published
    future schedule is not participation yet.

    Admin-only within `org_id`. The caller must be an authenticated admin
    whose own org matches the requested one.
    """
    verify_org_member(current_admin, org_id)

    in_window = _in_last_days(days, utcnow())

    # Total volunteers
    total_volunteers = db.query(Person).filter(Person.org_id == org_id).count()

    # Active volunteers (have at least one assignment)
    active_volunteers = (
        db.query(func.count(func.distinct(Assignment.person_id)))
        .join(Event)
        .filter(Event.org_id == org_id)
        .filter(in_window)
        .scalar()
    )

    # Total assignments
    total_assignments = (
        db.query(func.count(Assignment.id))
        .join(Event)
        .filter(Event.org_id == org_id)
        .filter(in_window)
        .scalar()
    )

    # Top volunteers
    top_volunteers = (
        db.query(Person.name, func.count(Assignment.id).label("assignment_count"))
        .join(Assignment, Person.id == Assignment.person_id)
        .join(Event)
        .filter(Event.org_id == org_id)
        .filter(in_window)
        .group_by(Person.id, Person.name)
        .order_by(func.count(Assignment.id).desc())
        .limit(10)
        .all()
    )

    return {
        "org_id": org_id,
        "period_days": days,
        "total_volunteers": total_volunteers,
        "active_volunteers": active_volunteers or 0,
        "total_assignments": total_assignments or 0,
        "participation_rate": round((active_volunteers or 0) / max(total_volunteers, 1) * 100, 1),
        "top_volunteers": [{"name": name, "assignments": count} for name, count in top_volunteers],
    }


@router.get("/{org_id}/schedule-health")
def get_schedule_health(
    org_id: str,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get schedule health metrics for upcoming events (start time now or later).

    Admin-only within `org_id`.
    """
    verify_org_member(current_admin, org_id)

    # Upcoming events: schedule health looks ahead, unlike the "last N days" stats.
    now = utcnow()
    upcoming_events = (
        db.query(Event).filter(Event.org_id == org_id).filter(Event.start_time >= now).count()
    )

    # Events with assignments
    events_with_assignments = (
        db.query(func.count(func.distinct(Event.id)))
        .join(Assignment)
        .filter(Event.org_id == org_id)
        .filter(Event.start_time >= now)
        .scalar()
    )

    # Latest solution
    latest_solution = (
        db.query(Solution)
        .filter(Solution.org_id == org_id)
        .order_by(Solution.created_at.desc())
        .first()
    )

    return {
        "org_id": org_id,
        "upcoming_events": upcoming_events,
        "events_with_assignments": events_with_assignments or 0,
        "coverage_rate": round((events_with_assignments or 0) / max(upcoming_events, 1) * 100, 1),
        "latest_solution": {
            "id": latest_solution.id,
            "health_score": latest_solution.health_score,
            "assignment_count": (
                db.query(Assignment)
                .join(Solution, Assignment.solution_id == Solution.id)
                .filter(Solution.org_id == org_id, Solution.id == latest_solution.id)
                .count()
            ),
            "created_at": latest_solution.created_at.isoformat(),
        }
        if latest_solution
        else None,
    }


@router.get("/{org_id}/burnout-risk")
def get_burnout_risk(
    org_id: str,
    threshold: int = Query(
        4, description="Assignments in the last 30 days (upcoming excluded) that flag risk"
    ),
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Identify volunteers at risk of burnout (serving too frequently).

    Counts assignments on events that started in the last 30 days; upcoming
    assignments do not count.

    Admin-only within `org_id`. This endpoint returns other volunteers'
    names and emails, so peer volunteers can never read it.
    """
    verify_org_member(current_admin, org_id)

    # Count assignments per person in the last 30 days (not upcoming ones)
    at_risk = (
        db.query(
            Person.id,
            Person.name,
            Person.email,
            func.count(Assignment.id).label("assignment_count"),
        )
        .join(Assignment, Person.id == Assignment.person_id)
        .join(Event)
        .filter(Event.org_id == org_id)
        .filter(_in_last_days(30, utcnow()))
        .group_by(Person.id, Person.name, Person.email)
        .having(func.count(Assignment.id) >= threshold)
        .order_by(func.count(Assignment.id).desc())
        .all()
    )

    return {
        "org_id": org_id,
        "threshold": threshold,
        "at_risk_count": len(at_risk),
        "at_risk_volunteers": [
            {
                "id": person_id,
                "name": name,
                "email": email,
                "assignments_last_30_days": count,
            }
            for person_id, name, email, count in at_risk
        ],
    }
