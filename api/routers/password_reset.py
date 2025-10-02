"""Password reset endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import secrets
import hashlib
from datetime import datetime, timedelta

from api.database import get_db
from roster_cli.db.models import Person

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


@router.post("/forgot-password")
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    """Request a password reset token."""
    person = db.query(Person).filter(Person.email == request.email).first()

    if not person:
        # Don't reveal if email exists (security)
        return {"message": "If the email exists, a reset link will be sent"}

    # Generate reset token
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "person_id": person.id,
        "expires": datetime.now() + timedelta(hours=1),
    }

    # In production, send email with reset link here
    # For now, return the token (in production, don't return it!)
    reset_link = f"http://localhost:8000/reset-password?token={token}"

    return {
        "message": "Password reset link sent to email",
        "reset_link": reset_link,  # Remove in production!
    }


@router.post("/reset-password")
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

    # Hash new password
    password_hash = hashlib.sha256(request.new_password.encode()).hexdigest()

    # Update password in extra_data
    extra_data = person.extra_data or {}
    extra_data["password_hash"] = password_hash
    person.extra_data = extra_data

    db.commit()

    # Remove used token
    del reset_tokens[request.token]

    return {"message": "Password reset successfully"}
