"""Full-page routes. 11.0 ships the shell: landing redirect + minimal
volunteer/admin dashboards proving cookie auth + nav + theming work
end-to-end. Real screens land in 11.1+ (see plan)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Assignment, Event, Person
from web.deps import get_session_admin, get_session_user

router = APIRouter(tags=["web-pages"])


def _row_dict(a: Assignment, e: Event) -> dict:
    start, end = e.start_time, e.end_time
    return {
        "id": a.id,
        "event_type": e.type,
        "date_label": start.strftime("%a %d %b %Y").upper() if start else "",
        "time_label": (
            f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}" if start and end else ""
        ),
        "role": a.role,
        "status": (a.status or "pending").lower(),
        "decline_reason": a.decline_reason,
    }


def _my_schedule_rows(db: Session, person: Person) -> list[dict]:
    """Assignment ⋈ Event for the caller, by event start. Enriched with
    event type + times — richer than the bare /api/v1/assignments/me
    shape, which omits event details the schedule list needs."""
    rows = (
        db.query(Assignment, Event)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Assignment.person_id == person.id,
            Event.org_id == person.org_id,
        )
        .order_by(Event.start_time.asc())
        .all()
    )
    return [_row_dict(a, e) for a, e in rows]


def _my_assignment(db: Session, person: Person, aid: int) -> dict | None:
    """Single Assignment ⋈ Event owned by the caller, or None (404)."""
    row = (
        db.query(Assignment, Event)
        .join(Event, Assignment.event_id == Event.id)
        .filter(
            Assignment.id == aid,
            Assignment.person_id == person.id,
            Event.org_id == person.org_id,
        )
        .first()
    )
    return _row_dict(*row) if row else None


@router.get("/")
def root(request: Request):
    # Resolve session lazily so the bare "/" works signed-in or not.
    from web.deps import _resolve_person
    from api.database import SessionLocal

    db = SessionLocal()
    try:
        person = _resolve_person(request, db)
    finally:
        db.close()
    if person is None:
        return RedirectResponse(url="/auth/login", status_code=303)
    landing = "/a/dashboard" if "admin" in (person.roles or []) else "/v/schedule"
    return RedirectResponse(url=landing, status_code=303)


@router.get("/v/schedule", response_class=HTMLResponse)
def volunteer_schedule(
    request: Request,
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "volunteer/schedule.html",
        {
            "person": person,
            "active_tab": "schedule",
            "rows": _my_schedule_rows(db, person),
        },
    )


@router.get("/v/schedule/{assignment_id}", response_class=HTMLResponse)
def volunteer_assignment_detail(
    request: Request,
    assignment_id: int,
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    from web.app import templates

    row = _my_assignment(db, person, assignment_id)
    if row is None:
        return templates.TemplateResponse(
            request,
            "volunteer/assignment_detail.html",
            {"person": person, "active_tab": "schedule", "row": None},
            status_code=404,
        )
    return templates.TemplateResponse(
        request,
        "volunteer/assignment_detail.html",
        {"person": person, "active_tab": "schedule", "row": row},
    )


def _my_timeoff(db: Session, person: Person) -> list[dict]:
    """Time-off rows for the caller via the API handler, formatted for
    display."""
    from datetime import date as _date

    from api.routers.availability import get_timeoff

    out = []
    for t in get_timeoff(person.id, db)["timeoff"]:
        s = _date.fromisoformat(t["start_date"])
        e = _date.fromisoformat(t["end_date"])
        out.append(
            {
                "id": t["id"],
                "label": (
                    s.strftime("%d %b %Y").upper()
                    if s == e
                    else f"{s.strftime('%d %b').upper()} – {e.strftime('%d %b %Y').upper()}"
                ),
                "reason": t["reason"],
            }
        )
    return out


# Preset recurring patterns. label → RRULE; the editor also accepts a
# custom expression. Mirrors the mobile kRrulePresets intent.
RRULE_PRESETS = [
    ("Every Sunday", "FREQ=WEEKLY;BYDAY=SU"),
    ("Every Saturday", "FREQ=WEEKLY;BYDAY=SA"),
    ("Weekdays", "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"),
    ("Every other week", "FREQ=WEEKLY;INTERVAL=2"),
    ("Monthly (1st)", "FREQ=MONTHLY;BYMONTHDAY=1"),
]


def _my_rrule(db: Session, person: Person) -> str | None:
    from api.routers.availability import get_rrule

    return get_rrule(person.id, db).rrule


def _my_exceptions(db: Session, person: Person) -> list[dict]:
    """Single-date blocked exceptions for the caller, formatted."""
    from api.routers.availability import list_exceptions

    return [
        {
            "id": r.id,
            "date": r.exception_date.isoformat(),
            "label": r.exception_date.strftime("%a %d %b %Y").upper(),
        }
        for r in list_exceptions(person.id, db)
    ]


@router.get("/v/availability", response_class=HTMLResponse)
def volunteer_availability(
    request: Request,
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "volunteer/availability.html",
        {
            "person": person,
            "active_tab": "availability",
            "timeoff": _my_timeoff(db, person),
            "rrule": _my_rrule(db, person),
            "rrule_presets": RRULE_PRESETS,
            "exceptions": _my_exceptions(db, person),
        },
    )


@router.get("/v/profile", response_class=HTMLResponse)
def volunteer_profile(request: Request, person: Person = Depends(get_session_user)):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "volunteer/profile.html",
        {"person": person, "active_tab": "profile"},
    )


@router.get("/a/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, person: Person = Depends(get_session_admin)):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        {"person": person, "active_tab": "dashboard"},
    )
