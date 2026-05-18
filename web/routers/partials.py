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
from api.routers.availability import (
    add_exception,
    add_timeoff,
    clear_rrule,
    delete_exception,
    delete_timeoff,
    set_rrule,
)
from api.schemas.assignment import AssignmentDeclineRequest, AssignmentSwapRequest
from api.schemas.availability import (
    AvailabilityExceptionCreate,
    AvailabilityRruleUpdate,
    TimeOffCreate,
)
from web.deps import get_session_user
from api.routers.calendar import reset_calendar_token
from web.routers.pages import (
    RRULE_PRESETS,
    _my_assignment,
    _my_calendar,
    _my_exceptions,
    _my_rrule,
    _my_timeoff,
)

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


# ── Availability: recurring rrule ────────────────────────────────────


def _rrule_section(request: Request, person: Person, db: Session, *, error=None):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "partials/rrule_section.html",
        {
            "rrule": _my_rrule(db, person),
            "rrule_presets": RRULE_PRESETS,
            "error": error,
        },
    )


@router.post("/v/availability/rrule", response_class=HTMLResponse)
def rrule_set(
    request: Request,
    rrule: str = Form(...),
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        payload = AvailabilityRruleUpdate(rrule=rrule.strip())
    except ValueError:
        return _rrule_section(request, person, db, error="Enter a recurrence rule.")
    set_rrule(person.id, payload, db)
    return _rrule_section(request, person, db)


@router.post("/v/availability/rrule/clear", response_class=HTMLResponse)
def rrule_clear(
    request: Request,
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    clear_rrule(person.id, db)
    return _rrule_section(request, person, db)


# ── Availability: single-date exceptions ─────────────────────────────


def _exceptions_list(request: Request, person: Person, db: Session, *, error=None):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "partials/exceptions_list.html",
        {"exceptions": _my_exceptions(db, person), "error": error},
    )


@router.post("/v/availability/exception", response_class=HTMLResponse)
def exception_add(
    request: Request,
    exception_date: str = Form(...),
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        payload = AvailabilityExceptionCreate(exception_date=exception_date)
    except ValueError:
        return _exceptions_list(request, person, db, error="Pick a valid date.")
    add_exception(person.id, payload, db)
    return _exceptions_list(request, person, db)


@router.post(
    "/v/availability/exception/{exception_id}/delete",
    response_class=HTMLResponse,
)
def exception_delete(
    request: Request,
    exception_id: int,
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        delete_exception(person.id, exception_id, db)
    except HTTPException:
        pass  # already gone — return a fresh, correct list
    return _exceptions_list(request, person, db)


# ── Profile: calendar subscription ───────────────────────────────────


@router.post("/v/profile/calendar/reset", response_class=HTMLResponse)
def calendar_reset(
    request: Request,
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    """Rotate the calendar token (invalidates the old subscription URL)
    and re-render the calendar card with the fresh URL."""
    from web.app import templates

    reset_calendar_token(person.id, person, db, request)
    return templates.TemplateResponse(
        request,
        "partials/calendar_section.html",
        {"calendar": _my_calendar(request, db, person)},
    )
