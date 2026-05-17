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


def _my_schedule_rows(db: Session, person: Person) -> list[dict]:
    """Assignment ⋈ Event for the caller, newest first. Enriched with
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
    out = []
    for a, e in rows:
        start, end = e.start_time, e.end_time
        out.append(
            {
                "id": a.id,
                "event_type": e.type,
                "date_label": start.strftime("%a %d %b %Y").upper() if start else "",
                "time_label": (
                    f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}" if start and end else ""
                ),
                "role": a.role,
                "status": (a.status or "pending").lower(),
            }
        )
    return out


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
