"""Solutions router - view and export generated solutions."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from io import StringIO, BytesIO
from datetime import datetime

from api.database import get_db
from api.schemas.solver import SolutionResponse, SolutionList, ExportFormat
from roster_cli.db.models import Solution, Assignment, Event, Person
from roster_cli.core.models import Assignment as AssignmentModel, Event as EventModel, Person as PersonModel
from roster_cli.core.csv_writer import write_assignments_csv
from roster_cli.core.ics_writer import write_calendar_ics
from roster_cli.core.json_writer import write_solution_json
import json

router = APIRouter(prefix="/solutions", tags=["solutions"])


@router.get("/", response_model=SolutionList)
def list_solutions(
    org_id: Optional[str] = Query(None, description="Filter by organization ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List solutions with optional filters."""
    query = db.query(Solution)

    if org_id:
        query = query.filter(Solution.org_id == org_id)

    query = query.order_by(Solution.created_at.desc())
    solutions = query.offset(skip).limit(limit).all()
    total = query.count()

    # Add assignment counts
    solution_responses = []
    for sol in solutions:
        assignment_count = db.query(Assignment).filter(Assignment.solution_id == sol.id).count()
        response = SolutionResponse.model_validate(sol)
        response.assignment_count = assignment_count
        solution_responses.append(response)

    return {"solutions": solution_responses, "total": total}


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

        result.append({
            "assignment_id": assignment.id,
            "event_id": assignment.event_id,
            "event_type": event.type if event else None,
            "event_start": event.start_time if event else None,
            "event_end": event.end_time if event else None,
            "person_id": assignment.person_id,
            "person_name": person.name if person else None,
            "assigned_at": assignment.assigned_at,
        })

    return {"assignments": result, "total": len(result)}


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
    from roster_cli.core.models import (
        SolutionBundle, Metrics, Violations, FairnessMetrics, StabilityMetrics,
        SolutionMeta, SolverMeta
    )
    from datetime import date

    solution_obj = SolutionBundle(
        meta=SolutionMeta(
            generated_at=solution.created_at,
            range_start=date.today(),
            range_end=date.today(),
            mode="greedy",
            change_min=False,
            solver=SolverMeta(name="greedy-solver", version="1.0", strategy="greedy")
        ),
        assignments=assignments,
        metrics=Metrics(
            hard_violations=solution.hard_violations,
            soft_score=solution.soft_score,
            health_score=solution.health_score,
            solve_ms=solution.solve_ms,
            fairness=FairnessMetrics(
                stdev=solution.metrics.get("fairness", {}).get("stdev", 0.0) if solution.metrics else 0.0,
                per_person_counts=solution.metrics.get("fairness", {}).get("per_person_counts", {}) if solution.metrics else {},
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
        writer.writerow(['Event ID', 'Event Type', 'Date', 'Time', 'Assignees'])

        # Data rows
        for assignment in assignments:
            event = next((e for e in events if e.id == assignment.event_id), None)
            if event:
                assignees = ', '.join([p.name for p in people if p.id in assignment.assignees])
                writer.writerow([
                    event.id,
                    event.type,
                    event.start.date(),
                    event.start.time(),
                    assignees
                ])

        content = output.getvalue()
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=solution_{solution_id}.csv"},
        )

    elif export_format.format == "ics":
        # TODO: ICS export has StringIO bug - needs fixing
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="ICS export not yet implemented"
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown format: {export_format.format}. Must be json, csv, or ics",
        )


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
