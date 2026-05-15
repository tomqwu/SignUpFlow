"""Web auth: HTML login form + cookie session set/clear.

Credential validation is identical to `api/routers/auth.py:login`
(`verify_password` + `_pwd_iat_for`). The only difference: instead of
returning the JWT in a JSON body, we set it as an httpOnly cookie and
redirect the browser to the role-appropriate landing page.
"""

from __future__ import annotations

import os

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Person
from api.security import create_access_token, verify_password
from api.timeutils import utcnow
from web.deps import SESSION_COOKIE, get_optional_session_user

router = APIRouter(tags=["web-auth"])

# Secure flag off in dev/test (http://localhost) so the cookie is stored;
# on in production. ENVIRONMENT=production is set by the app at boot.
_COOKIE_SECURE = os.getenv("ENVIRONMENT", "development") == "production"
_COOKIE_MAX_AGE = 60 * 60 * 24  # 24h, matches access-token lifetime intent


def _pwd_iat_for(person: Person) -> float:
    """Mirror of api/routers/auth.py:_pwd_iat_for — the password-version
    claim used for session-invalidation-on-password-change."""
    if person.password_changed_at is not None:
        return person.password_changed_at.timestamp()
    return utcnow().timestamp()


def _landing_for(person: Person) -> str:
    return "/a/dashboard" if "admin" in (person.roles or []) else "/v/schedule"


def set_session_cookie(response, person: Person) -> None:
    token = create_access_token(data={"sub": person.id, "pwd_iat": _pwd_iat_for(person)})
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=_COOKIE_MAX_AGE,
        httponly=True,
        secure=_COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


@router.get("/auth/login", response_class=HTMLResponse)
def login_form(
    request: Request,
    person: Person | None = Depends(get_optional_session_user),
):
    # Already signed in → skip the form.
    if person is not None:
        return RedirectResponse(url=_landing_for(person), status_code=303)
    from web.app import templates

    return templates.TemplateResponse(request, "auth/login.html", {"error": None})


@router.post("/auth/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    from web.app import templates

    person = db.query(Person).filter(Person.email == email).first()
    invalid = (
        person is None
        or not person.password_hash
        or not verify_password(password, person.password_hash)
    )
    if invalid:
        # 401 + re-render the form with an inline error (HTMX swaps the
        # whole <main>; full-page nav also works since the template
        # extends base).
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": "Invalid email or password."},
            status_code=401,
        )

    response = RedirectResponse(url=_landing_for(person), status_code=303)
    set_session_cookie(response, person)
    return response


@router.post("/auth/logout")
def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response
