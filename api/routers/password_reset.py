"""Password reset endpoints."""

import os
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import AuditAction, Person
from api.security import hash_password
from api.services.email_service import email_service
from api.timeutils import utcnow
from api.utils.audit_logger import log_audit_event
from api.utils.rate_limit_middleware import rate_limit


def _debug_return_reset_token() -> bool:
    """True iff DEBUG_RETURN_RESET_TOKEN is opted into via env. Default off."""
    return os.getenv("DEBUG_RETURN_RESET_TOKEN", "false").strip().lower() in ("1", "true", "yes")


router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory token store (in production, use Redis or database)
reset_tokens = {}


class PasswordResetRequest(BaseModel):
    """Request password reset."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token."""

    token: str
    new_password: str


def _send_reset_email_quiet(to_email: str, name: str, reset_token: str, app_url: str) -> None:
    """Background-task wrapper around send_password_reset_email.

    Swallows all exceptions: a flaky SendGrid (or any other email backend)
    must never affect the HTTP response timing of /forgot-password, both
    to preserve anti-enumeration guarantees and to avoid a DoS path where
    a slow upstream blocks request handlers. Any failure is logged and
    discarded — the reset token is already issued and the user can retry.

    The email service itself short-circuits when ``TESTING=true`` is set
    (see ``EmailService.__init__``), so tests that don't explicitly mock
    the service won't hang on a real SMTP retry loop.
    """
    try:
        email_service.send_password_reset_email(
            to_email=to_email,
            name=name,
            reset_token=reset_token,
            app_url=app_url,
        )
    except Exception:  # noqa: BLE001 — see docstring; we never want this to bubble
        import logging

        logging.getLogger("password_reset").exception(
            "send_password_reset_email failed for %s (token still valid)", to_email
        )


@router.post("/forgot-password", dependencies=[Depends(rate_limit("password_reset"))])
def request_password_reset(
    request: PasswordResetRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Request a password reset token.

    Always returns the same generic message regardless of whether the email
    exists. Audits every request. The reset token is held in-memory and is
    NEVER returned in the response in production. Set
    `DEBUG_RETURN_RESET_TOKEN=true` in dev/test environments to opt into
    receiving the token in the JSON body for E2E exercise.

    Email send is queued via ``BackgroundTasks`` so the HTTP response
    timing is independent of email backend latency — both for anti-
    enumeration and to prevent slow-SMTP DoS. The reset token is issued
    synchronously; email delivery is best-effort.
    """
    generic_response = {"message": "If the email exists, a password reset link will be sent"}
    person = db.query(Person).filter(Person.email == request.email).first()

    log_audit_event(
        db,
        action=AuditAction.PASSWORD_RESET_REQUESTED,
        user_id=person.id if person else None,
        user_email=request.email,
        organization_id=person.org_id if person else None,
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
        status="success" if person else "denied",
    )

    if not person:
        return generic_response

    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "person_id": person.id,
        "expires": datetime.now() + timedelta(hours=1),
    }

    # Queue the email send. Starlette runs background tasks AFTER the
    # response is sent, so HTTP timing is independent of email backend
    # latency (anti-enumeration + anti-DoS).
    background_tasks.add_task(
        _send_reset_email_quiet,
        to_email=person.email,
        name=person.name,
        reset_token=token,
        app_url=os.getenv("APP_URL", "http://localhost:8000"),
    )

    if _debug_return_reset_token():
        # Test/dev affordance ONLY. Default off.
        return {**generic_response, "token": token}

    return generic_response


@router.post("/reset-password", dependencies=[Depends(rate_limit("password_reset_confirm"))])
def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """Reset password using token."""
    token_data = reset_tokens.get(request.token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    if datetime.now() > token_data["expires"]:
        del reset_tokens[request.token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )

    # Get person
    person = db.query(Person).filter(Person.id == token_data["person_id"]).first()
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Hash new password using bcrypt (same as signup/login)
    person.password_hash = hash_password(request.new_password)
    # Invalidate any tokens issued before this reset.
    person.password_changed_at = utcnow()

    db.commit()

    # Remove used token
    del reset_tokens[request.token]

    return {"message": "Password reset successfully"}
