"""Cookie-based session for the web app.

The JSON API authenticates via `Authorization: Bearer` (HTTPBearer) for
the mobile client. Browsers get the same JWT, but delivered in an
httpOnly cookie instead of a header. `get_session_user` mirrors
`api/dependencies.py:get_current_user` exactly — same token verification,
same password-rotation revocation check — only the transport differs.
"""

from __future__ import annotations

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Person
from api.security import verify_token

SESSION_COOKIE = "signupflow_session"


class _RedirectToLogin(Exception):
    """Raised when an unauthenticated browser hits a protected page.

    Caught by the web app's exception handler and turned into a 303 to
    /auth/login. Using an exception (not returning a Response from the
    dependency) keeps the page handlers clean — they can type their
    return as the template response only.
    """


def _resolve_person(request: Request, db: Session) -> Person | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        payload = verify_token(token)
    except Exception:
        return None
    person_id = payload.get("sub")
    if not person_id:
        return None
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        return None
    # Session-invalidation-on-password-change, identical to the API dep.
    pwd_iat = payload.get("pwd_iat")
    if pwd_iat is not None and person.password_changed_at is not None:
        if float(pwd_iat) < person.password_changed_at.timestamp():
            return None
    return person


def get_session_user(
    request: Request, db: Session = Depends(get_db)
) -> Person:
    """Require an authenticated browser session. Redirects to /auth/login
    (303) when absent or invalid."""
    person = _resolve_person(request, db)
    if person is None:
        raise _RedirectToLogin()
    return person


def get_session_admin(
    person: Person = Depends(get_session_user),
) -> Person:
    """Require an authenticated admin. Non-admins are bounced to their
    volunteer landing rather than shown a raw 403."""
    roles = person.roles or []
    if "admin" not in roles:
        raise _RedirectToLogin()
    return person


def get_optional_session_user(
    request: Request, db: Session = Depends(get_db)
) -> Person | None:
    """Resolve the session user if present, else None. For pages like
    /auth/login that render differently when already signed in."""
    return _resolve_person(request, db)


def login_redirect() -> RedirectResponse:
    return RedirectResponse(url="/auth/login", status_code=303)
