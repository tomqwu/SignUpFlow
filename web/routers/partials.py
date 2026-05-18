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
from api.routers.auth import ChangePasswordRequest, change_password
from api.routers.availability import (
    add_exception,
    add_timeoff,
    clear_rrule,
    delete_exception,
    delete_timeoff,
    set_rrule,
)
from api.routers.calendar import reset_calendar_token
from api.routers.events import create_event, delete_event
from api.routers.invitations import create_invitation
from api.routers.organizations import get_organization, update_organization
from api.routers.people import update_current_person
from api.routers.solutions import compare_solutions, publish_solution
from api.routers.solver import solve_schedule
from api.routers.teams import (
    add_team_members,
    create_team,
    delete_team,
    remove_team_members,
    update_team,
)
from api.schemas.assignment import AssignmentDeclineRequest, AssignmentSwapRequest
from api.schemas.availability import (
    AvailabilityExceptionCreate,
    AvailabilityRruleUpdate,
    TimeOffCreate,
)
from api.schemas.event import EventCreate
from api.schemas.invitation import InvitationCreate
from api.schemas.organization import OrganizationUpdate
from api.schemas.person import PersonUpdate
from api.schemas.solver import SolveRequest
from api.schemas.team import TeamCreate, TeamMemberAdd, TeamMemberRemove, TeamUpdate
from web.deps import get_session_admin, get_session_user
from web.routers.pages import (
    RRULE_PRESETS,
    _events,
    _my_assignment,
    _my_calendar,
    _my_exceptions,
    _my_rrule,
    _my_timeoff,
    _solution_owned,
    _teams,
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


# NOTE: these routes declare `background_tasks: BackgroundTasks` as a
# FastAPI param (not a throwaway BackgroundTasks()) and pass it to the
# API handler. The handler queues event_bus.publish via add_task;
# FastAPI runs those AFTER the response. A discarded BackgroundTasks()
# would silently drop the publish, so the Solution-Review SSE stream
# (11.19) never fires. Caught by the 11.19 live e2e test.


@router.post("/v/schedule/{assignment_id}/accept", response_class=HTMLResponse)
def accept(
    request: Request,
    assignment_id: int,
    background_tasks: BackgroundTasks,
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        accept_assignment(assignment_id, request, background_tasks, person, db)
    except HTTPException:
        return _gone()
    return _card(request, person, db, assignment_id)


@router.post("/v/schedule/{assignment_id}/decline", response_class=HTMLResponse)
def decline(
    request: Request,
    assignment_id: int,
    background_tasks: BackgroundTasks,
    decline_reason: str = Form(...),
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        decline_assignment(
            assignment_id,
            AssignmentDeclineRequest(decline_reason=decline_reason),
            request,
            background_tasks,
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
    background_tasks: BackgroundTasks,
    note: str | None = Form(None),
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    try:
        request_swap(
            assignment_id,
            AssignmentSwapRequest(note=note),
            request,
            background_tasks,
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


# ── Admin: invite person ─────────────────────────────────────────────


@router.post("/a/people/invite", response_class=HTMLResponse)
def people_invite(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form("volunteer"),
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    """Create an invitation in the admin's org. Returns a small result
    partial (success banner or inline error) swapped into #invite-result.
    The invitee only appears on /a/people once they accept."""
    from web.app import templates

    def _result(ok: bool, msg: str, code: int = 200):
        return templates.TemplateResponse(
            request,
            "partials/invite_result.html",
            {"ok": ok, "msg": msg},
            status_code=code,
        )

    role = role if role in ("volunteer", "admin") else "volunteer"
    try:
        payload = InvitationCreate(name=name, email=email, roles=[role])
    except ValueError:
        return _result(False, "Enter a valid name and email.", 400)
    try:
        create_invitation(payload, BackgroundTasks(), org_id=person.org_id, inviter=person, db=db)
    except HTTPException as exc:
        return _result(False, str(exc.detail), exc.status_code or 400)
    return _result(True, f"Invitation sent to {email}.")


# ── Admin: organization settings ─────────────────────────────────────


@router.post("/a/settings", response_class=HTMLResponse)
def settings_save(
    request: Request,
    name: str = Form(...),
    region: str = Form(""),
    timezone: str = Form(""),
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    """Update the admin's own organization. Timezone is merged into the
    org config dict (other config keys preserved). Reuses the API's
    update_organization so the same validation applies."""
    from web.app import templates

    def _render(*, error=None, saved=False, org=None):
        if org is None:
            org = {
                "name": name,
                "region": region or None,
                "timezone": timezone or "",
            }
        return templates.TemplateResponse(
            request,
            "partials/settings_form.html",
            {"org": org, "error": error, "saved": saved},
            status_code=400 if error else 200,
        )

    if not name.strip():
        return _render(error="Organization name is required.")

    current = get_organization(person.org_id, db)
    config = dict(current.config or {})
    tz = timezone.strip()
    if tz:
        config["timezone"] = tz
    else:
        config.pop("timezone", None)

    try:
        payload = OrganizationUpdate(
            name=name.strip(),
            region=region.strip() or None,
            config=config,
        )
    except ValueError:
        return _render(error="Invalid settings.")
    try:
        update_organization(person.org_id, payload, db)
    except HTTPException as exc:
        return _render(error=str(exc.detail), org=None)

    return _render(
        saved=True,
        org={
            "name": name.strip(),
            "region": region.strip() or None,
            "timezone": tz,
        },
    )


# ── Account / security (self-service) ────────────────────────────────


def _profile_ctx(person: Person, *, saved=False, error=None, name=None) -> dict:
    return {
        "name": name if name is not None else person.name,
        "timezone": person.timezone,
        "language": person.language,
        "saved": saved,
        "error": error,
    }


@router.post("/v/profile", response_class=HTMLResponse)
async def profile_save(
    request: Request,
    name: str = Form(...),
    timezone: str = Form(""),
    language: str = Form(""),
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    """Update the signed-in user's own profile (any role). Reuses the
    API's PUT /people/me handler."""
    from web.app import templates

    def _render(ctx):
        return templates.TemplateResponse(
            request,
            "partials/profile_form.html",
            {"profile": ctx},
            status_code=400 if ctx["error"] else 200,
        )

    if not name.strip():
        return _render(_profile_ctx(person, error="Name is required.", name=""))

    payload = PersonUpdate(
        name=name.strip(),
        timezone=timezone.strip() or None,
        language=language.strip() or None,
    )
    try:
        await update_current_person(payload, person, db)
    except HTTPException as exc:
        return _render(_profile_ctx(person, error=str(exc.detail)))
    return _render(_profile_ctx(person, saved=True))


@router.post("/v/account/password", response_class=HTMLResponse)
def password_change(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    person: Person = Depends(get_session_user),
    db: Session = Depends(get_db),
):
    """Change the signed-in user's password. Reuses the API
    change_password handler, then re-mints the web session cookie so
    the password-version bump doesn't log the user out mid-session."""
    from web.app import templates
    from web.auth import set_session_cookie

    def _err(msg: str):
        return templates.TemplateResponse(
            request,
            "partials/password_form.html",
            {"pw": {"error": msg, "saved": False}},
            status_code=400,
        )

    if new_password != confirm_password:
        return _err("New password and confirmation don't match.")
    if len(new_password) < 6:
        return _err("New password must be at least 6 characters.")

    try:
        change_password(
            ChangePasswordRequest(current_password=current_password, new_password=new_password),
            person,
            db,
        )
    except HTTPException as exc:
        return _err(str(exc.detail))

    resp = templates.TemplateResponse(
        request,
        "partials/password_form.html",
        {"pw": {"error": None, "saved": True}},
    )
    set_session_cookie(resp, person)
    return resp


# ── Admin: teams ─────────────────────────────────────────────────────


def _teams_list(request: Request, person: Person, db: Session, *, error=None):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "partials/teams_list.html",
        {"teams": _teams(db, person.org_id), "error": error},
        status_code=400 if error else 200,
    )


@router.post("/a/teams/create", response_class=HTMLResponse)
def team_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    import uuid

    from web.auth import _slugify

    if not name.strip():
        return _teams_list(request, person, db, error="Team name is required.")
    payload = TeamCreate(
        id=f"{_slugify(name)}-{uuid.uuid4().hex[:8]}",
        org_id=person.org_id,
        name=name.strip(),
        description=description.strip() or None,
        member_ids=[],
    )
    try:
        create_team(payload, person, db)
    except HTTPException as exc:
        return _teams_list(request, person, db, error=str(exc.detail))
    return _teams_list(request, person, db)


@router.post("/a/teams/{team_id}/update", response_class=HTMLResponse)
def team_update(
    request: Request,
    team_id: str,
    name: str = Form(...),
    description: str = Form(""),
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    if not name.strip():
        return _teams_list(request, person, db, error="Team name is required.")
    try:
        update_team(
            team_id,
            TeamUpdate(name=name.strip(), description=description.strip() or None),
            person,
            db,
        )
    except HTTPException as exc:
        return _teams_list(request, person, db, error=str(exc.detail))
    return _teams_list(request, person, db)


@router.post("/a/teams/{team_id}/delete", response_class=HTMLResponse)
def team_delete(
    request: Request,
    team_id: str,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    try:
        delete_team(team_id, person, db)
    except HTTPException:
        pass  # already gone — return a fresh, correct list
    return _teams_list(request, person, db)


@router.post("/a/teams/{team_id}/members/add", response_class=HTMLResponse)
def team_member_add(
    request: Request,
    team_id: str,
    person_id: str = Form(...),
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    try:
        add_team_members(team_id, TeamMemberAdd(person_ids=[person_id]), person, db)
    except HTTPException as exc:
        return _teams_list(request, person, db, error=str(exc.detail))
    return _teams_list(request, person, db)


@router.post("/a/teams/{team_id}/members/remove", response_class=HTMLResponse)
def team_member_remove(
    request: Request,
    team_id: str,
    person_id: str = Form(...),
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    try:
        remove_team_members(team_id, TeamMemberRemove(person_ids=[person_id]), person, db)
    except HTTPException as exc:
        return _teams_list(request, person, db, error=str(exc.detail))
    return _teams_list(request, person, db)


# ── Admin: event create / delete ─────────────────────────────────────


def _events_list(request: Request, person: Person, db: Session, *, error=None):
    from web.app import templates

    return templates.TemplateResponse(
        request,
        "partials/events_list.html",
        {"events": _events(db, person.org_id), "error": error},
    )


@router.post("/a/events/create", response_class=HTMLResponse)
def event_create(
    request: Request,
    type: str = Form(...),
    event_date: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    role_name: list[str] = Form(default=[]),
    role_count: list[str] = Form(default=[]),
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    """Create an event in the admin's org. Combines the date + two time
    inputs into start/end datetimes; generates a unique slug id. Parallel
    role_name/role_count rows become extra_data.role_counts so the solver
    has roles to assign — without this a web-created event gets 0
    assignments (issue #141)."""
    import uuid
    from datetime import datetime

    from web.auth import _slugify

    def _err(msg: str, code: int = 400):
        return _events_list(request, person, db, error=msg)

    try:
        start_dt = datetime.fromisoformat(f"{event_date}T{start_time}")
        end_dt = datetime.fromisoformat(f"{event_date}T{end_time}")
    except ValueError:
        return _err("Enter a valid date and times.")
    if end_dt <= start_dt:
        return _err("End time must be after start time.")

    role_counts: dict[str, int] = {}
    for idx, raw_name in enumerate(role_name):
        name = raw_name.strip()
        if not name:
            continue
        raw_count = role_count[idx] if idx < len(role_count) else "1"
        try:
            count = int(raw_count)
        except (TypeError, ValueError):
            continue
        if count < 1:
            continue
        role_counts[name] = role_counts.get(name, 0) + count

    event_id = f"{_slugify(type)}-{uuid.uuid4().hex[:8]}"
    try:
        payload = EventCreate(
            id=event_id,
            org_id=person.org_id,
            type=type,
            start_time=start_dt,
            end_time=end_dt,
            extra_data={"role_counts": role_counts} if role_counts else None,
        )
    except ValueError:
        return _err("Invalid event details.")
    try:
        create_event(payload, person, db)
    except HTTPException as exc:
        return _err(str(exc.detail), exc.status_code or 400)
    return _events_list(request, person, db)


@router.post("/a/events/{event_id}/delete", response_class=HTMLResponse)
def event_delete(
    request: Request,
    event_id: str,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    try:
        delete_event(event_id, person, db)
    except HTTPException:
        pass  # already gone — return a fresh, correct list
    return _events_list(request, person, db)


# ── Admin: run solver ────────────────────────────────────────────────


@router.post("/a/solver/run", response_class=HTMLResponse)
def solver_run(
    request: Request,
    from_date: str = Form(...),
    to_date: str = Form(...),
    mode: str = Form("strict"),
    change_min: str | None = Form(None),
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    """Run the scheduler for the admin's org and render a result summary
    with a link to review the new solution (11.18)."""
    from web.app import templates

    def _err(msg: str, code: int = 400):
        return templates.TemplateResponse(
            request, "partials/solver_result.html", {"error": msg}, status_code=code
        )

    mode = mode if mode in ("strict", "relaxed") else "strict"
    try:
        req = SolveRequest(
            org_id=person.org_id,
            from_date=from_date,
            to_date=to_date,
            mode=mode,
            change_min=(change_min == "true"),
        )
    except ValueError:
        return _err("Enter a valid date range.")
    try:
        resp = solve_schedule(req, person, db)
    except HTTPException as exc:
        return _err(str(exc.detail), exc.status_code or 400)

    m = resp.metrics
    return templates.TemplateResponse(
        request,
        "partials/solver_result.html",
        {
            "r": {
                "solution_id": resp.solution_id,
                "assignment_count": resp.assignment_count,
                "health_score": round(m.health_score),
                "hard_violations": m.hard_violations,
                "solve_ms": round(m.solve_ms),
            }
        },
    )


# ── Admin: publish solution + compare ────────────────────────────────


@router.post("/a/solution/{solution_id}/publish", response_class=HTMLResponse)
def solution_publish(
    request: Request,
    solution_id: int,
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    """Publish the solution (unpublishes any prior in the org). Returns
    the refreshed publish-state fragment."""
    from web.app import templates

    if _solution_owned(db, person, solution_id) is None:
        return HTMLResponse(
            '<div id="publish-state" class="empty">Solution not found.</div>',
            status_code=404,
        )
    try:
        publish_solution(solution_id, request, person, db)
    except HTTPException as exc:
        return templates.TemplateResponse(
            request,
            "partials/publish_state.html",
            {"published": False, "error": str(exc.detail)},
            status_code=exc.status_code or 400,
        )
    return templates.TemplateResponse(
        request, "partials/publish_state.html", {"published": True, "error": None}
    )


@router.post("/a/compare", response_class=HTMLResponse)
def compare_run(
    request: Request,
    solution_a: int = Form(...),
    solution_b: int = Form(...),
    person: Person = Depends(get_session_admin),
    db: Session = Depends(get_db),
):
    from web.app import templates

    def _err(msg: str, code: int = 400):
        return templates.TemplateResponse(
            request,
            "partials/compare_result.html",
            {"diff": None, "error": msg},
            status_code=code,
        )

    if (
        _solution_owned(db, person, solution_a) is None
        or _solution_owned(db, person, solution_b) is None
    ):
        return _err("Pick two solutions from your organization.", 404)
    try:
        diff = compare_solutions(solution_a, solution_b, person, db)
    except HTTPException as exc:
        return _err(str(exc.detail), exc.status_code or 400)
    return templates.TemplateResponse(
        request,
        "partials/compare_result.html",
        {
            "diff": {
                "a": diff.solution_a_id,
                "b": diff.solution_b_id,
                "added": len(diff.added),
                "removed": len(diff.removed),
                "unchanged": diff.unchanged_count,
                "moves": diff.moves,
                "affected": diff.affected_persons,
            },
            "error": None,
        },
    )
