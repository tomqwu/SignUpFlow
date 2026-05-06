"""Password reset endpoints."""

import os
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import AuditAction, Person
from api.security import hash_password
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


@router.post("/forgot-password", dependencies=[Depends(rate_limit("password_reset"))])
def request_password_reset(
    request: PasswordResetRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Request a password reset token.

    Always returns the same generic message regardless of whether the email
    exists. Audits every request. The reset token is held in-memory and is
    NEVER returned in the response in production. Set
    `DEBUG_RETURN_RESET_TOKEN=true` in dev/test environments to opt into
    receiving the token in the JSON body for E2E exercise.
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

    db.commit()

    # Remove used token
    del reset_tokens[request.token]

    return {"message": "Password reset successfully"}
