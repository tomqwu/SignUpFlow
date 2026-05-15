"""Full-page routes. 11.0 ships the shell: landing redirect + minimal
volunteer/admin dashboards proving cookie auth + nav + theming work
end-to-end. Real screens land in 11.1+ (see plan)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from api.models import Person
from web.deps import get_session_admin, get_session_user

router = APIRouter(tags=["web-pages"])


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
def volunteer_schedule(request: Request, person: Person = Depends(get_session_user)):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "volunteer/schedule.html",
        {"person": person, "active_tab": "schedule"},
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
