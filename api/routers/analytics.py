"""Analytics endpoints for volunteer participation metrics."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from api.database import get_db
from api.models import Person, Assignment, Event, Solution

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/{org_id}/volunteer-stats")
def get_volunteer_stats(
    org_id: str,
    db: Session = Depends(get_db),
    days: int = Query(30, description="Number of days to analyze"),
):
    """Get volunteer participation statistics."""

    since_date = datetime.now() - timedelta(days=days)

    # Total volunteers
    total_volunteers = db.query(Person).filter(Person.org_id == org_id).count()

    # Active volunteers (have at least one assignment)
    active_volunteers = (
        db.query(func.count(func.distinct(Assignment.person_id)))
        .join(Event)
        .filter(Event.org_id == org_id)
        .filter(Event.start_time >= since_date)
        .scalar()
    )

    # Total assignments
    total_assignments = (
        db.query(func.count(Assignment.id))
        .join(Event)
        .filter(Event.org_id == org_id)
        .filter(Event.start_time >= since_date)
        .scalar()
    )

    # Top volunteers
    top_volunteers = (
        db.query(
            Person.name,
            func.count(Assignment.id).label("assignment_count")
        )
        .join(Assignment, Person.id == Assignment.person_id)
        .join(Event)
        .filter(Event.org_id == org_id)
        .filter(Event.start_time >= since_date)
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
        "top_volunteers": [
            {"name": name, "assignments": count}
            for name, count in top_volunteers
        ],
    }


@router.get("/{org_id}/schedule-health")
def get_schedule_health(
    org_id: str,
    db: Session = Depends(get_db),
):
    """Get schedule health metrics."""

    # Upcoming events
    upcoming_events = (
        db.query(Event)
        .filter(Event.org_id == org_id)
        .filter(Event.start_time >= datetime.now())
        .count()
    )

    # Events with assignments
    events_with_assignments = (
        db.query(func.count(func.distinct(Event.id)))
        .join(Assignment)
        .filter(Event.org_id == org_id)
        .filter(Event.start_time >= datetime.now())
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
            "assignment_count": latest_solution.assignment_count,
            "created_at": latest_solution.created_at.isoformat(),
        } if latest_solution else None,
    }


@router.get("/{org_id}/burnout-risk")
def get_burnout_risk(
    org_id: str,
    db: Session = Depends(get_db),
    threshold: int = Query(4, description="Assignments per month threshold"),
):
    """Identify volunteers at risk of burnout (serving too frequently)."""

    one_month_ago = datetime.now() - timedelta(days=30)

    # Count assignments per person in last month
    at_risk = (
        db.query(
            Person.id,
            Person.name,
            Person.email,
            func.count(Assignment.id).label("assignment_count")
        )
        .join(Assignment, Person.id == Assignment.person_id)
        .join(Event)
        .filter(Event.org_id == org_id)
        .filter(Event.start_time >= one_month_ago)
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
