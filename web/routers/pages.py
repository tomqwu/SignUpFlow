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


def _my_calendar(request: Request, db: Session, person: Person) -> dict:
    """Calendar subscription URL for the caller (token generated lazily
    by the API handler)."""
    from api.routers.calendar import get_subscription_url

    resp = get_subscription_url(person.id, person, db, request)
    return {"https_url": resp.https_url, "webcal_url": resp.webcal_url}


@router.get("/v/profile", response_class=HTMLResponse)
def volunteer_profile(
    request: Request,
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "volunteer/profile.html",
        {
            "person": person,
            "active_tab": "profile",
            "calendar": _my_calendar(request, db, person),
        },
    )


def _dashboard_kpis(db: Session, org_id: str) -> dict:
    """Roll the three analytics endpoints into the dashboard tiles.
    All three return graceful zeros for an empty org."""
    from api.routers.analytics import (
        get_burnout_risk,
        get_schedule_health,
        get_volunteer_stats,
    )

    # Pass the Query-defaulted args explicitly: a direct (non-FastAPI)
    # call doesn't resolve Query(...) sentinels to their defaults.
    vs = get_volunteer_stats(org_id, db, days=30)
    sh = get_schedule_health(org_id, db)
    br = get_burnout_risk(org_id, db, threshold=4)
    latest = sh.get("latest_solution")
    return {
        "active_volunteers": vs["active_volunteers"],
        "total_volunteers": vs["total_volunteers"],
        "participation_rate": vs["participation_rate"],
        "upcoming_events": sh["upcoming_events"],
        "coverage_rate": sh["coverage_rate"],
        "health_score": (round(latest["health_score"]) if latest else None),
        "at_risk_count": br["at_risk_count"],
        "top_volunteers": vs["top_volunteers"][:5],
    }


@router.get("/a/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        {
            "person": person,
            "active_tab": "dashboard",
            "kpis": _dashboard_kpis(db, person.org_id),
        },
    )


def _people(db: Session, org_id: str, q: str | None) -> list[dict]:
    """People in the admin's org, optional case-insensitive name/email
    search. Direct query (org-scoped) — simpler than threading the
    API list_people's Query()/pagination deps through a direct call."""
    from sqlalchemy import or_

    query = db.query(Person).filter(Person.org_id == org_id)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Person.name.ilike(like), Person.email.ilike(like)))
    rows = query.order_by(Person.name.asc()).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "email": p.email,
            "roles": [r.upper() for r in (p.roles or ["volunteer"])],
            "status": (p.status or "active").lower(),
        }
        for p in rows
    ]


@router.get("/a/people", response_class=HTMLResponse)
def admin_people(
    request: Request,
    q: str | None = None,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "admin/people.html",
        {
            "person": person,
            "active_tab": "people",
            "people": _people(db, person.org_id, q),
            "q": q or "",
        },
    )


@router.get("/a/people/list", response_class=HTMLResponse)
def admin_people_list(
    request: Request,
    q: str | None = None,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    """HTMX fragment for live search."""
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "partials/people_list.html",
        {"people": _people(db, person.org_id, q), "q": q or ""},
    )


def _events(db: Session, org_id: str) -> dict:
    """Org events split into upcoming vs past, formatted. Direct query
    (org-scoped) — simpler than the API list_events Query()/pagination
    deps via a direct call."""
    from api.timeutils import utcnow

    now = utcnow()
    rows = db.query(Event).filter(Event.org_id == org_id).order_by(Event.start_time.asc()).all()
    upcoming, past = [], []
    for e in rows:
        item = {
            "id": e.id,
            "type": e.type,
            "date_label": e.start_time.strftime("%a %d %b %Y").upper() if e.start_time else "",
            "time_label": (
                f"{e.start_time.strftime('%H:%M')}–{e.end_time.strftime('%H:%M')}"
                if e.start_time and e.end_time
                else ""
            ),
        }
        (upcoming if e.start_time and e.start_time >= now else past).append(item)
    past.reverse()  # most-recent past first
    return {"upcoming": upcoming, "past": past}


@router.get("/a/events", response_class=HTMLResponse)
def admin_events(
    request: Request,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "admin/events.html",
        {
            "person": person,
            "active_tab": "events",
            "events": _events(db, person.org_id),
        },
    )


@router.get("/a/solver", response_class=HTMLResponse)
def admin_solver(
    request: Request,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    from datetime import timedelta

    from api.timeutils import utcnow
    from web.app import templates

    today = utcnow().date()
    return templates.TemplateResponse(
        request,
        "admin/solver.html",
        {
            "person": person,
            "active_tab": "solver",
            "default_from": today.isoformat(),
            "default_to": (today + timedelta(days=28)).isoformat(),
        },
    )


def _solution_owned(db: Session, person: Person, sid: int):
    """The Solution row iff it belongs to the caller's org, else None."""
    from api.models import Solution

    return db.query(Solution).filter(Solution.id == sid, Solution.org_id == person.org_id).first()


def _solution_events(db: Session, person: Person, sid: int) -> list[dict] | None:
    """Event-grouped assignees for an owned solution, formatted. None →
    404 (unknown or other-org). Shared by the full review page and the
    SSE-driven assignments refetch."""
    from api.routers.solutions import get_solution_assignments

    if _solution_owned(db, person, sid) is None:
        return None
    assignments = get_solution_assignments(sid, db)
    return [
        {
            "event_type": e.event_type or e.event_id,
            "date_label": e.event_start.strftime("%a %d %b %Y · %H:%M").upper()
            if e.event_start
            else "",
            "assignees": [a.person_name or a.person_id for a in e.assignees],
        }
        for e in assignments.events
    ]


def _solution_review(db: Session, person: Person, sid: int) -> dict | None:
    """Solution header + event-grouped assignments + stats for a solution
    in the admin's org. None → 404."""
    from api.routers.solutions import get_solution, get_solution_stats

    if _solution_owned(db, person, sid) is None:
        return None
    detail = get_solution(sid, db)
    stats = get_solution_stats(sid, person, db)
    events = _solution_events(db, person, sid)
    return {
        "id": detail.id,
        "health_score": round(detail.health_score),
        "hard_violations": detail.hard_violations,
        "soft_score": round(detail.soft_score, 1),
        "assignment_count": detail.assignment_count,
        "is_published": detail.is_published,
        "created_label": detail.created_at.strftime("%a %d %b %Y").upper()
        if detail.created_at
        else "",
        "events": events,
        "stats": {
            "fairness_stdev": round(stats.fairness.stdev, 2),
            "workload_max": stats.workload.max_events_per_person,
            "workload_min": stats.workload.min_events_per_person,
            "workload_median": stats.workload.median_events_per_person,
            "distinct": stats.workload.distinct_persons_assigned,
            "total": stats.workload.total_events_assigned,
        },
    }


@router.get("/a/solution/{solution_id}", response_class=HTMLResponse)
def admin_solution_review(
    request: Request,
    solution_id: int,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    from web.app import templates

    review = _solution_review(db, person, solution_id)
    if review is None:
        return templates.TemplateResponse(
            request,
            "admin/solution_review.html",
            {"person": person, "active_tab": "solver", "review": None},
            status_code=404,
        )
    return templates.TemplateResponse(
        request,
        "admin/solution_review.html",
        {"person": person, "active_tab": "solver", "review": review},
    )


@router.get("/a/solution/{solution_id}/assignments", response_class=HTMLResponse)
def admin_solution_assignments(
    request: Request,
    solution_id: int,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    """HTMX fragment: the event-grouped assignments block, refetched on
    each SSE event."""
    from web.app import templates

    events = _solution_events(db, person, solution_id)
    if events is None:
        return templates.TemplateResponse(
            request,
            "partials/solution_assignments.html",
            {"events": []},
            status_code=404,
        )
    return templates.TemplateResponse(
        request,
        "partials/solution_assignments.html",
        {"events": events},
    )


@router.get("/a/solution/{solution_id}/stream")
async def admin_solution_stream(
    solution_id: int,
    request: Request,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    """Cookie-authed SSE mirror of GET /api/v1/solutions/{id}/assignments
    /stream (which is Bearer-only). Same per-process event_bus topic
    (solution:{id}) the assignment-mutation endpoints publish to."""
    import json

    from fastapi.responses import StreamingResponse

    from api.services import event_bus

    if _solution_owned(db, person, solution_id) is None:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")

    topic = f"solution:{solution_id}"

    async def _stream():
        yield ": stream open\n\n"
        async for event in event_bus.subscribe(topic):
            if await request.is_disconnected():
                break
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )
