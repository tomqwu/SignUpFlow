"""Solutions router - view and export generated solutions."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from api.core.models import (
    Assignment as AssignmentModel,
)
from api.core.models import (
    Event as EventModel,
)
from api.core.models import (
    Person as PersonModel,
)
from api.database import get_db
from api.dependencies import get_current_admin_user, verify_org_member
from api.models import Assignment, AuditAction, AuditLog, Event, Organization, Person, Solution
from api.schemas.common import PaginationParams, get_pagination_params
from api.schemas.solver import (
    AssignmentChange,
    ExportFormat,
    SolutionDiffResponse,
    SolutionList,
    SolutionResponse,
)
from api.timeutils import utcnow
from api.utils.audit_logger import log_audit_event
from api.utils.pdf_export import generate_schedule_pdf

router = APIRouter(prefix="/solutions", tags=["solutions"])


@router.get("/", response_model=SolutionList)
def list_solutions(
    org_id: str | None = Query(None, description="Filter by organization ID"),
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    """List solutions with optional filters."""
    query = db.query(Solution)

    if org_id:
        query = query.filter(Solution.org_id == org_id)

    query = query.order_by(Solution.created_at.desc())
    solutions = query.offset(pagination.offset).limit(pagination.limit).all()
    total = query.count()

    # Add assignment counts
    solution_responses = []
    for sol in solutions:
        assignment_count = db.query(Assignment).filter(Assignment.solution_id == sol.id).count()
        response = SolutionResponse.model_validate(sol)
        response.assignment_count = assignment_count
        solution_responses.append(response)

    return {
        "items": solution_responses,
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
    }


@router.get("/{solution_id}", response_model=SolutionResponse)
def get_solution(solution_id: int, db: Session = Depends(get_db)):
    """Get solution by ID."""
    solution = db.query(Solution).filter(Solution.id == solution_id).first()
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution {solution_id} not found",
        )

    assignment_count = db.query(Assignment).filter(Assignment.solution_id == solution.id).count()
    response = SolutionResponse.model_validate(solution)
    response.assignment_count = assignment_count
    return response


@router.get("/{solution_id}/assignments")
def get_solution_assignments(solution_id: int, db: Session = Depends(get_db)):
    """Get all assignments for a solution."""
    solution = db.query(Solution).filter(Solution.id == solution_id).first()
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution {solution_id} not found",
        )

    assignments = db.query(Assignment).filter(Assignment.solution_id == solution_id).all()

    # Group by event
    result = []
    for assignment in assignments:
        event = db.query(Event).filter(Event.id == assignment.event_id).first()
        person = db.query(Person).filter(Person.id == assignment.person_id).first()

        result.append(
            {
                "assignment_id": assignment.id,
                "event_id": assignment.event_id,
                "event_type": event.type if event else None,
                "event_start": event.start_time if event else None,
                "event_end": event.end_time if event else None,
                "person_id": assignment.person_id,
                "person_name": person.name if person else None,
                "assigned_at": assignment.assigned_at,
            }
        )

    return {"assignments": result, "total": len(result)}


@router.post("/", response_model=SolutionResponse, status_code=status.HTTP_201_CREATED)
def create_manual_solution(
    solution_data: dict,
    db: Session = Depends(get_db),
):
    """
    Create a manual solution record (for testing or external import).
    Note: This does not create assignments, just the solution metadata.
    """
    # Verify organization exists
    org_id = solution_data.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="org_id is required")

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")

    new_solution = Solution(
        org_id=org_id,
        solve_ms=solution_data.get("solve_ms", 0.0),
        hard_violations=solution_data.get("hard_violations", 0),
        soft_score=solution_data.get("soft_score", 0.0),
        health_score=solution_data.get("health_score", 0.0),
        metrics=solution_data.get("metrics", {}),
        created_at=datetime.utcnow(),
    )

    db.add(new_solution)
    db.commit()
    db.refresh(new_solution)

    response = SolutionResponse.model_validate(new_solution)
    response.assignment_count = 0
    return response


@router.post("/{solution_id}/export")
def export_solution(
    solution_id: int,
    export_format: ExportFormat,
    db: Session = Depends(get_db),
):
    """Export solution in various formats (CSV, ICS, JSON)."""
    solution = db.query(Solution).filter(Solution.id == solution_id).first()
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution {solution_id} not found",
        )

    # Load assignments
    assignments_db = db.query(Assignment).filter(Assignment.solution_id == solution_id).all()
    if not assignments_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solution has no assignments",
        )

    # Group assignments by event
    event_assignments = {}
    for a in assignments_db:
        if a.event_id not in event_assignments:
            event_assignments[a.event_id] = []
        event_assignments[a.event_id].append(a.person_id)

    # Load events and people
    event_ids = list(event_assignments.keys())
    events_db = db.query(Event).filter(Event.id.in_(event_ids)).all()
    people_db = db.query(Person).filter(Person.org_id == solution.org_id).all()

    # Convert to core models
    events = [
        EventModel(
            id=e.id,
            type=e.type,
            start=e.start_time,
            end=e.end_time,
            resource_id=e.resource_id,
            team_ids=[],
            required_roles=[],
        )
        for e in events_db
    ]

    people = [
        PersonModel(id=p.id, name=p.name, roles=p.roles or [], skills=[], teams=[])
        for p in people_db
    ]

    assignments = [
        AssignmentModel(event_id=event_id, assignees=person_ids)
        for event_id, person_ids in event_assignments.items()
    ]

    # Create a minimal solution object for export
    from datetime import date

    from api.core.models import (
        FairnessMetrics,
        Metrics,
        SolutionBundle,
        SolutionMeta,
        SolverMeta,
        StabilityMetrics,
        Violations,
    )

    solution_obj = SolutionBundle(
        meta=SolutionMeta(
            generated_at=solution.created_at,
            range_start=date.today(),
            range_end=date.today(),
            mode="greedy",
            change_min=False,
            solver=SolverMeta(name="greedy-solver", version="1.0", strategy="greedy"),
        ),
        assignments=assignments,
        metrics=Metrics(
            hard_violations=solution.hard_violations,
            soft_score=solution.soft_score,
            health_score=solution.health_score,
            solve_ms=solution.solve_ms,
            fairness=FairnessMetrics(
                stdev=solution.metrics.get("fairness", {}).get("stdev", 0.0)
                if solution.metrics
                else 0.0,
                per_person_counts=solution.metrics.get("fairness", {}).get("per_person_counts", {})
                if solution.metrics
                else {},
            ),
            stability=StabilityMetrics(moves_from_published=0, affected_persons=0),
        ),
        violations=Violations(hard=[], soft=[]),
    )

    # Apply scope filtering if needed
    if export_format.scope.startswith("person:"):
        person_id = export_format.scope.split(":", 1)[1]
        assignments = [a for a in assignments if person_id in a.assignees]
    elif export_format.scope.startswith("team:"):
        # Would need team member lookup
        pass

    # Generate export
    if export_format.format == "json":
        # Return solution as JSON directly
        import json

        content = json.dumps(solution_obj.model_dump(), indent=2, default=str)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=solution_{solution_id}.json"},
        )

    elif export_format.format == "csv":
        # Generate CSV directly without using write_assignments_csv (has StringIO bug)
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(["Event ID", "Event Type", "Date", "Time", "Assignees"])

        # Data rows
        for assignment in assignments:
            event = next((e for e in events if e.id == assignment.event_id), None)
            if event:
                assignees = ", ".join([p.name for p in people if p.id in assignment.assignees])
                writer.writerow(
                    [event.id, event.type, event.start.date(), event.start.time(), assignees]
                )

        content = output.getvalue()
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=solution_{solution_id}.csv"},
        )

    elif export_format.format == "ics":
        # TODO: ICS export has StringIO bug - needs fixing
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="ICS export not yet implemented"
        )

    elif export_format.format == "pdf":
        # Get organization name
        org = db.query(Organization).filter(Organization.id == solution.org_id).first()
        org_name = org.name if org else solution.org_id

        # Prepare data for PDF generation
        pdf_events = []
        for event in events:
            pdf_events.append(
                {
                    "id": event.id,
                    "type": event.type,
                    "start_time": event.start,
                    "end_time": event.end,
                }
            )

        # Create people mapping (id -> {name, roles})
        people_map = {p.id: {"name": p.name, "roles": p.roles or []} for p in people}

        # Create assignments mapping (event_id -> [person_ids])
        assignments_map = {a.event_id: a.assignees for a in assignments}

        # Get event role requirements
        events_db_map = {e.id: e for e in events_db}

        # Get blocked dates for all people
        from api.models import Availability, VacationPeriod

        blocked_dates_map = {}  # person_id -> list of {start, end}
        for person in people:
            vacations = (
                db.query(VacationPeriod)
                .join(Availability, VacationPeriod.availability_id == Availability.id)
                .filter(Availability.person_id == person.id)
                .all()
            )
            blocked_dates_map[person.id] = [
                {"start": v.start_date, "end": v.end_date} for v in vacations
            ]

        # Generate PDF
        pdf_buffer = generate_schedule_pdf(
            org_name, pdf_events, people_map, assignments_map, events_db_map, blocked_dates_map
        )

        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=schedule_{solution_id}.pdf"},
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown format: {export_format.format}. Must be json, csv, ics, or pdf",
        )


@router.post("/{solution_id}/publish", response_model=SolutionResponse)
def publish_solution(
    solution_id: int,
    http_request: Request,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Publish a solution (admin only). Unpublishes any prior published in the same org."""
    solution = db.query(Solution).filter(Solution.id == solution_id).first()
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution {solution_id} not found",
        )
    verify_org_member(current_admin, solution.org_id)

    # Unpublish any prior in the same org.
    prior = (
        db.query(Solution)
        .filter(
            Solution.org_id == solution.org_id,
            Solution.is_published.is_(True),
            Solution.id != solution.id,
        )
        .all()
    )
    for s in prior:
        s.is_published = False
        s.published_at = None

    now = utcnow()
    solution.is_published = True
    solution.published_at = now
    db.commit()
    db.refresh(solution)

    log_audit_event(
        db,
        action=AuditAction.SOLUTION_PUBLISHED,
        user_id=current_admin.id,
        user_email=current_admin.email,
        organization_id=solution.org_id,
        resource_type="solution",
        resource_id=str(solution.id),
        details={"unpublished_prior_ids": [s.id for s in prior]},
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
    )

    assignment_count = db.query(Assignment).filter(Assignment.solution_id == solution.id).count()
    response = SolutionResponse.model_validate(solution)
    response.assignment_count = assignment_count
    return response


@router.post("/{solution_id}/unpublish", response_model=SolutionResponse)
def unpublish_solution(
    solution_id: int,
    http_request: Request,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Unpublish a solution (admin only)."""
    solution = db.query(Solution).filter(Solution.id == solution_id).first()
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution {solution_id} not found",
        )
    verify_org_member(current_admin, solution.org_id)

    solution.is_published = False
    solution.published_at = None
    db.commit()
    db.refresh(solution)

    log_audit_event(
        db,
        action=AuditAction.SOLUTION_UNPUBLISHED,
        user_id=current_admin.id,
        user_email=current_admin.email,
        organization_id=solution.org_id,
        resource_type="solution",
        resource_id=str(solution.id),
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
    )

    assignment_count = db.query(Assignment).filter(Assignment.solution_id == solution.id).count()
    response = SolutionResponse.model_validate(solution)
    response.assignment_count = assignment_count
    return response


@router.get("/{solution_a_id}/compare/{solution_b_id}", response_model=SolutionDiffResponse)
def compare_solutions(
    solution_a_id: int,
    solution_b_id: int,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Diff two solutions (admin only). Both must belong to the same org as the caller."""
    sol_a = db.query(Solution).filter(Solution.id == solution_a_id).first()
    if not sol_a:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution {solution_a_id} not found",
        )
    sol_b = db.query(Solution).filter(Solution.id == solution_b_id).first()
    if not sol_b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution {solution_b_id} not found",
        )
    verify_org_member(current_admin, sol_a.org_id)
    verify_org_member(current_admin, sol_b.org_id)

    a_rows = db.query(Assignment).filter(Assignment.solution_id == sol_a.id).all()
    b_rows = db.query(Assignment).filter(Assignment.solution_id == sol_b.id).all()

    a_keys = {(r.event_id, r.person_id, r.role) for r in a_rows}
    b_keys = {(r.event_id, r.person_id, r.role) for r in b_rows}

    removed = a_keys - b_keys
    added = b_keys - a_keys
    unchanged_count = len(a_keys & b_keys)

    affected_persons = sorted({pid for (_, pid, _) in removed | added})

    return SolutionDiffResponse(
        solution_a_id=sol_a.id,
        solution_b_id=sol_b.id,
        added=[AssignmentChange(event_id=e, person_id=p, role=r) for (e, p, r) in added],
        removed=[AssignmentChange(event_id=e, person_id=p, role=r) for (e, p, r) in removed],
        unchanged_count=unchanged_count,
        affected_persons=affected_persons,
        moves=len(added) + len(removed),
    )


@router.post("/{solution_id}/rollback", response_model=SolutionResponse)
def rollback_solution(
    solution_id: int,
    http_request: Request,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Rollback to a previously-published solution (admin only).

    Republishes the target and unpublishes whatever is currently published in
    the same org. The target must have been published at some point before
    (i.e. an audit row recording its publish/rollback exists); otherwise 400.
    """
    solution = db.query(Solution).filter(Solution.id == solution_id).first()
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution {solution_id} not found",
        )
    verify_org_member(current_admin, solution.org_id)

    # Eligibility: existing publish_solution nulls published_at on the prior
    # when it replaces, so published_at is unreliable. Use the audit trail.
    was_ever_published = (
        db.query(AuditLog)
        .filter(
            AuditLog.action.in_([AuditAction.SOLUTION_PUBLISHED, AuditAction.SOLUTION_ROLLED_BACK]),
            AuditLog.resource_id == str(solution.id),
        )
        .count()
        > 0
    )
    if not was_ever_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot roll back to a solution that has never been published",
        )

    prior = (
        db.query(Solution)
        .filter(
            Solution.org_id == solution.org_id,
            Solution.is_published.is_(True),
            Solution.id != solution.id,
        )
        .all()
    )
    for s in prior:
        s.is_published = False
        s.published_at = None

    now = utcnow()
    solution.is_published = True
    solution.published_at = now
    db.commit()
    db.refresh(solution)

    log_audit_event(
        db,
        action=AuditAction.SOLUTION_ROLLED_BACK,
        user_id=current_admin.id,
        user_email=current_admin.email,
        organization_id=solution.org_id,
        resource_type="solution",
        resource_id=str(solution.id),
        details={"unpublished_prior_ids": [s.id for s in prior]},
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
    )

    assignment_count = db.query(Assignment).filter(Assignment.solution_id == solution.id).count()
    response = SolutionResponse.model_validate(solution)
    response.assignment_count = assignment_count
    return response


@router.delete("/{solution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_solution(solution_id: int, db: Session = Depends(get_db)):
    """Delete solution and all assignments."""
    solution = db.query(Solution).filter(Solution.id == solution_id).first()
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solution {solution_id} not found",
        )

    db.delete(solution)
    db.commit()
    return None
