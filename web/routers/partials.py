"""HTMX fragment endpoints — return HTML partials, not full pages.

Assignment actions reuse the API handlers in api/routers/assignments.py
directly (same _load_own_assignment ownership check, same event_bus
publish). The web session user is passed as `current_user`; a throwaway
BackgroundTasks collects the publish side-effect. On success we re-render
the assignment card partial so HTMX swaps the fresh status in place.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Person
from api.routers.assignments import (
    accept_assignment,
    decline_assignment,
    request_swap,
)
from api.routers.availability import add_timeoff, delete_timeoff
from api.schemas.assignment import AssignmentDeclineRequest, AssignmentSwapRequest
from api.schemas.availability import TimeOffCreate
from web.deps import get_session_user
from web.routers.pages import _my_assignment, _my_timeoff

router = APIRouter(tags=["web-partials"])


def _gone() -> HTMLResponse:
    return HTMLResponse(
        '<div id="assignment-card" class="empty">'
        "This assignment isn't on your schedule anymore.</div>",
        status_code=404,
    )


def _card(request: Request, person: Person, db: Session, aid: int):
    from web.app import templates

    row = _my_assignment(db, person, aid)
    if row is None:
        return _gone()
    return templates.TemplateResponse(request, "partials/assignment_detail_card.html", {"row": row})


@router.post("/v/schedule/{assignment_id}/accept", response_class=HTMLResponse)
def accept(
    request: Request,
    assignment_id: int,
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        accept_assignment(assignment_id, request, BackgroundTasks(), person, db)
    except HTTPException:
        return _gone()
    return _card(request, person, db, assignment_id)


@router.post("/v/schedule/{assignment_id}/decline", response_class=HTMLResponse)
def decline(
    request: Request,
    assignment_id: int,
    decline_reason: str = Form(...),
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        decline_assignment(
            assignment_id,
            AssignmentDeclineRequest(decline_reason=decline_reason),
            request,
            BackgroundTasks(),
            person,
            db,
        )
    except HTTPException:
        return _gone()
    return _card(request, person, db, assignment_id)


@router.post("/v/schedule/{assignment_id}/swap-request", response_class=HTMLResponse)
def swap(
    request: Request,
    assignment_id: int,
    note: str | None = Form(None),
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        request_swap(
            assignment_id,
            AssignmentSwapRequest(note=note),
            request,
            BackgroundTasks(),
            person,
            db,
        )
    except HTTPException:
        return _gone()
    return _card(request, person, db, assignment_id)


# ── Availability: time-off ───────────────────────────────────────────


def _timeoff_list(request: Request, person: Person, db: Session, *, error=None):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "partials/timeoff_list.html",
        {"timeoff": _my_timeoff(db, person), "error": error},
    )


@router.post("/v/availability/timeoff", response_class=HTMLResponse)
def timeoff_add(
    request: Request,
    start_date: str = Form(...),
    end_date: str = Form(...),
    reason: str | None = Form(None),
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        payload = TimeOffCreate(start_date=start_date, end_date=end_date, reason=reason or None)
    except ValueError:
        return _timeoff_list(request, person, db, error="Enter valid dates.")
    try:
        add_timeoff(person.id, payload, db)
    except HTTPException as exc:
        return _timeoff_list(request, person, db, error=str(exc.detail))
    return _timeoff_list(request, person, db)


@router.post("/v/availability/timeoff/{timeoff_id}/delete", response_class=HTMLResponse)
def timeoff_delete(
    request: Request,
    timeoff_id: int,
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        delete_timeoff(person.id, timeoff_id, db)
    except HTTPException:
        pass  # already gone — fall through to a fresh (correct) list
    return _timeoff_list(request, person, db)
