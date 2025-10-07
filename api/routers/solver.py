"""Solver router - schedule generation endpoint."""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db

logger = logging.getLogger("rostio")
from api.schemas.solver import SolveRequest, SolveResponse, ViolationInfo, FairnessMetrics, SolutionMetrics
from api.models import (
    Organization,
    Person,
    Team,
    Event,
    Constraint as DBConstraint,
    Holiday,
    Solution as DBSolution,
    Assignment as DBAssignment,
)
from api.core.models import (
    Org,
    Event as EventModel,
    Person as PersonModel,
    Team as TeamModel,
    ConstraintBinding as ConstraintModel,
    Holiday as HolidayModel,
    OrgDefaults,
)
from api.core.solver.adapter import SolveContext
from api.core.solver.heuristics import GreedyHeuristicSolver

router = APIRouter(prefix="/solver", tags=["solver"])


@router.post("/solve", response_model=SolveResponse)
def solve_schedule(solve_request: SolveRequest, db: Session = Depends(get_db)):
    """
    Generate a schedule for the organization.

    This endpoint:
    1. Loads all org data from database
    2. Runs the constraint solver
    3. Saves the solution to database
    4. Returns solution metrics and violations
    """
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == solve_request.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{solve_request.org_id}' not found",
        )

    # Load all data
    people_db = db.query(Person).filter(Person.org_id == solve_request.org_id).all()
    teams_db = db.query(Team).filter(Team.org_id == solve_request.org_id).all()
    events_db = (
        db.query(Event)
        .filter(
            Event.org_id == solve_request.org_id,
            Event.start_time >= datetime.combine(solve_request.from_date, datetime.min.time()),
            Event.start_time <= datetime.combine(solve_request.to_date, datetime.max.time()),
        )
        .all()
    )
    constraints_db = db.query(DBConstraint).filter(DBConstraint.org_id == solve_request.org_id).all()
    holidays_db = (
        db.query(Holiday)
        .filter(
            Holiday.org_id == solve_request.org_id,
            Holiday.date >= solve_request.from_date,
            Holiday.date <= solve_request.to_date,
        )
        .all()
    )

    if not events_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No events found in date range {solve_request.from_date} to {solve_request.to_date}",
        )

    # Convert database models to core models
    org_file = Org(
        org_id=org.id,
        region=org.region or "",
        defaults=OrgDefaults(
            change_min_weight=org.config.get("change_min_weight", 100) if org.config else 100,
            fairness_weight=org.config.get("fairness_weight", 50) if org.config else 50,
            cooldown_days=org.config.get("cooldown_days", 14) if org.config else 14,
        ) if org.config else OrgDefaults(),
    )

    people = [
        PersonModel(id=p.id, name=p.name, roles=p.roles or [], skills=[], teams=[])
        for p in people_db
    ]

    teams = []
    for t in teams_db:
        member_ids = [tm.person_id for tm in t.members]
        teams.append(TeamModel(id=t.id, name=t.name, members=member_ids))

    # Convert events to core model format
    events = []
    for e in events_db:
        # Extract role requirements from extra_data
        role_counts = (e.extra_data or {}).get("role_counts", {})
        required_roles = [
            {"role": role_name, "count": count}
            for role_name, count in role_counts.items()
        ]

        # Debug logging
        logger.info(f"Event {e.id}: role_counts={role_counts}, required_roles={required_roles}")

        events.append(
            EventModel(
                id=e.id,
                type=e.type,
                start=e.start_time,
                end=e.end_time,
                resource_id=e.resource_id,
                team_ids=[et.team_id for et in e.event_teams],
                required_roles=required_roles,
            )
        )

    # For now, we'll pass an empty constraints list since the API stores constraints
    # differently than the solver expects (ConstraintBinding vs simple params).
    # In production, you would convert DB constraints to proper ConstraintBinding format
    # with scope, applies_to, when, and then fields.
    constraints = []

    holidays = [
        HolidayModel(date=h.date, label=h.label, is_long_weekend=h.is_long_weekend)
        for h in holidays_db
    ]

    # Build solve context
    context = SolveContext(
        org=org_file,
        people=people,
        teams=teams,
        resources=[],  # TODO: Load resources if needed
        events=events,
        constraints=constraints,
        availability=[],  # TODO: Load availability if needed
        holidays=holidays,
        from_date=solve_request.from_date,
        to_date=solve_request.to_date,
        mode=solve_request.mode,
        change_min=solve_request.change_min,
    )

    # Solve
    solver = GreedyHeuristicSolver()
    solver.build_model(context)
    solution = solver.solve()

    # Save solution to database
    db_solution = DBSolution(
        org_id=org.id,
        solve_ms=solution.metrics.solve_ms,
        hard_violations=solution.metrics.hard_violations,
        soft_score=solution.metrics.soft_score,
        health_score=solution.metrics.health_score,
        metrics={
            "fairness": {
                "stdev": solution.metrics.fairness.stdev,
                "per_person_counts": solution.metrics.fairness.per_person_counts,
            }
        },
    )
    db.add(db_solution)
    db.flush()

    # Save assignments
    for assignment in solution.assignments:
        for person_id in assignment.assignees:
            db_assignment = DBAssignment(
                solution_id=db_solution.id,
                event_id=assignment.event_id,
                person_id=person_id,
            )
            db.add(db_assignment)

    db.commit()
    db.refresh(db_solution)

    # Build response
    violations = [
        ViolationInfo(
            constraint_key=v.constraint_key,
            message=v.message,
            entities=v.entities,
            severity="hard" if v in solution.violations.hard else "soft",
        )
        for v in (solution.violations.hard + solution.violations.soft)
    ]

    metrics = SolutionMetrics(
        hard_violations=solution.metrics.hard_violations,
        soft_score=solution.metrics.soft_score,
        health_score=solution.metrics.health_score,
        solve_ms=solution.metrics.solve_ms,
        fairness=FairnessMetrics(
            stdev=solution.metrics.fairness.stdev,
            per_person_counts=solution.metrics.fairness.per_person_counts,
        ),
    )

    return SolveResponse(
        solution_id=db_solution.id,
        metrics=metrics,
        assignment_count=len(solution.assignments),
        violations=violations[:20],  # Limit to first 20
        message=f"Solution generated with {len(solution.assignments)} assignments",
    )
