"""Solver router - schedule generation endpoint."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_admin_user, verify_org_member

logger = logging.getLogger("rostio")
from api.core.models import (
    Availability as AvailabilityModel,
)
from api.core.models import (
    Event as EventModel,
)
from api.core.models import (
    Holiday as HolidayModel,
)
from api.core.models import (
    Org,
    OrgDefaults,
)
from api.core.models import (
    Person as PersonModel,
)
from api.core.models import (
    Resource as ResourceModel,
)
from api.core.models import (
    Team as TeamModel,
)
from api.core.models import (
    VacationPeriod as VacationPeriodModel,
)
from api.core.solver.adapter import SolveContext
from api.core.solver.heuristics import GreedyHeuristicSolver
from api.core.timeutils import parse_rrule
from api.models import (
    Assignment as DBAssignment,
)
from api.models import (
    Availability as DBAvailability,
)
from api.models import (
    AvailabilityException as DBAvailabilityException,
)
from api.models import (
    Constraint as DBConstraint,
)
from api.models import (
    Event,
    Holiday,
    Organization,
    Person,
    Resource,
    Team,
)
from api.models import (
    Solution as DBSolution,
)
from api.models import (
    VacationPeriod as DBVacationPeriod,
)
from api.schemas.solver import (
    FairnessMetrics,
    SolutionMetrics,
    SolveRequest,
    SolveResponse,
    StabilityMetrics,
    ViolationInfo,
)
from api.utils.solver_stability import compute_stability_metrics

router = APIRouter(prefix="/solver", tags=["solver"])


@router.post("/solve", response_model=SolveResponse)
def solve_schedule(
    solve_request: SolveRequest,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Generate a schedule for the organization (admin only).

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

    # Verify admin belongs to the organization
    verify_org_member(current_admin, solve_request.org_id)

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
    (db.query(DBConstraint).filter(DBConstraint.org_id == solve_request.org_id).all())
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
        )
        if org.config
        else OrgDefaults(),
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
            {"role": role_name, "count": count} for role_name, count in role_counts.items()
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

    # Load resources for the org
    resources_db = db.query(Resource).filter(Resource.org_id == solve_request.org_id).all()
    resources = [
        ResourceModel(
            id=r.id,
            type=r.type,
            capacity=r.capacity or 1,
            location=r.location,
        )
        for r in resources_db
    ]

    # Load availability for people in this org. Each Availability row carries:
    #   - VacationPeriod children: ranges the solver blocks (Sprint 3-E)
    #   - AvailabilityException children: one-off blocked dates
    #   - rrule string: recurring blocked dates expanded over the solve window
    person_ids = [p.id for p in people_db]
    availability: list[AvailabilityModel] = []
    if person_ids:
        avail_rows = db.query(DBAvailability).filter(DBAvailability.person_id.in_(person_ids)).all()
        # Compute the solve window once for rrule expansion
        from_dt = datetime.combine(solve_request.from_date, datetime.min.time())
        to_dt = datetime.combine(solve_request.to_date, datetime.max.time())

        for a in avail_rows:
            vacations = [
                VacationPeriodModel(start=v.start_date, end=v.end_date)
                for v in db.query(DBVacationPeriod)
                .filter(DBVacationPeriod.availability_id == a.id)
                .all()
            ]
            # One-off exception dates from AvailabilityException
            exception_dates: list = [
                row.exception_date
                for row in db.query(DBAvailabilityException)
                .filter(DBAvailabilityException.availability_id == a.id)
                .all()
            ]
            # Expand rrule to concrete blocked dates within [from_date, to_date].
            # Malformed rrule strings are logged and treated as no-op so a single
            # bad rule doesn't break the entire solve.
            if a.rrule:
                try:
                    for occ in parse_rrule(a.rrule, from_dt, to_dt):
                        exception_dates.append(occ.date())
                except Exception as exc:  # noqa: BLE001 — solver must not crash on bad input
                    logger.warning(
                        "Skipping malformed rrule for person=%s availability=%s: %s",
                        a.person_id,
                        a.id,
                        exc,
                    )

            availability.append(
                AvailabilityModel(
                    person_id=a.person_id,
                    rrule=a.rrule,
                    vacations=vacations,
                    exceptions=exception_dates,
                )
            )

    # Build solve context
    context = SolveContext(
        org=org_file,
        people=people,
        teams=teams,
        resources=resources,
        events=events,
        constraints=constraints,
        availability=availability,
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

    # Compute stability vs the org's currently-published solution.
    stability = compute_stability_metrics(db, org_id=org.id, new_assignments=solution.assignments)

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
            },
            "stability": {
                "moves_from_published": stability.moves_from_published,
                "affected_persons": stability.affected_persons,
            },
        },
    )
    db.add(db_solution)
    db.flush()

    # Save assignments and collect IDs for notifications
    assignment_ids = []
    for assignment in solution.assignments:
        for person_id in assignment.assignees:
            db_assignment = DBAssignment(
                solution_id=db_solution.id,
                event_id=assignment.event_id,
                person_id=person_id,
            )
            db.add(db_assignment)
            db.flush()  # Flush to get assignment ID
            assignment_ids.append(db_assignment.id)

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
        stability=StabilityMetrics(
            moves_from_published=stability.moves_from_published,
            affected_persons=stability.affected_persons,
        ),
    )

    return SolveResponse(
        solution_id=db_solution.id,
        metrics=metrics,
        assignment_count=len(solution.assignments),
        violations=violations[:20],  # Limit to first 20
        message=f"Solution generated with {len(solution.assignments)} assignments",
    )
