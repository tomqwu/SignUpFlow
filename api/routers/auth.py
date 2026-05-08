"""Authentication endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_organization_by_id
from api.models import Person
from api.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from api.timeutils import utcnow
from api.utils.rate_limit_middleware import rate_limit


def _pwd_iat_for(person: Person) -> float:
    """Token claim representing the password version this token was issued for."""
    if person.password_changed_at is not None:
        return person.password_changed_at.timestamp()
    return utcnow().timestamp()


router = APIRouter(prefix="/auth", tags=["auth"])


# Schemas
class SignupRequest(BaseModel):
    """Signup request."""

    org_id: str = Field(..., description="Organization ID")
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    roles: list[str] | None = Field(default_factory=list, description="User roles")
    timezone: str | None = Field(default="UTC", description="User timezone")
    language: str | None = Field(default="en", description="User language")


class LoginRequest(BaseModel):
    """Login request."""

    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class AuthResponse(BaseModel):
    """Authentication response."""

    person_id: str
    org_id: str
    name: str
    email: str
    roles: list[str]
    timezone: str
    language: str
    token: str
    refresh_token: str = Field(
        default="",
        description="Refresh token (long-lived). Use POST /auth/refresh to "
        "exchange for a fresh access+refresh token pair.",
    )


class RefreshRequest(BaseModel):
    """Request to exchange a refresh token for a new access+refresh pair."""

    refresh_token: str = Field(..., description="The refresh_token from the prior auth response")


class RefreshResponse(BaseModel):
    """Refresh response — both tokens are rotated on every refresh."""

    token: str
    refresh_token: str


# Endpoints
@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("signup"))],
)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account. Rate limited to 3 requests per hour per IP."""

    # Check if email already exists
    existing = db.query(Person).filter(Person.email == request.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Verify organization exists
    get_organization_by_id(request.org_id, db)

    # Check if this is the first user in the organization
    existing_users_count = db.query(Person).filter(Person.org_id == request.org_id).count()
    is_first_user = existing_users_count == 0

    # Create person ID from email
    person_id = f"person_{request.email.split('@')[0]}_{uuid.uuid4().hex[:8]}"

    # Hash password
    password_hash = hash_password(request.password)

    # Determine roles: first user gets admin, others cannot self-assign admin
    if is_first_user:
        # First user in the organization automatically becomes admin
        roles = ["admin"]
    else:
        # Non-first users cannot self-assign admin role during signup
        # Admin role can only be granted by existing admins via invitation or role management
        requested_roles = request.roles if request.roles else []
        # Filter out admin role from requested roles (security: users can't make themselves admin)
        safe_roles = [role for role in requested_roles if role != "admin"]
        # Default to volunteer if no valid roles requested
        roles = safe_roles if safe_roles else ["volunteer"]

    # Create person
    person = Person(
        id=person_id,
        org_id=request.org_id,
        name=request.name,
        email=request.email,
        password_hash=password_hash,
        roles=roles,
        timezone=request.timezone,
        language=request.language,
        password_changed_at=utcnow(),
        extra_data={},
    )

    db.add(person)
    db.commit()
    db.refresh(person)

    # Generate access + refresh tokens (pwd_iat allows revocation on password change).
    pwd_iat = _pwd_iat_for(person)
    access_token = create_access_token(data={"sub": person.id, "pwd_iat": pwd_iat})
    refresh_token = create_refresh_token(data={"sub": person.id, "pwd_iat": pwd_iat})

    return AuthResponse(
        person_id=person.id,
        org_id=person.org_id,
        name=person.name,
        email=person.email,
        roles=person.roles or [],
        timezone=person.timezone or "UTC",
        language=person.language or "en",
        token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=AuthResponse, dependencies=[Depends(rate_limit("login"))])
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password. Rate limited to 5 requests per 5 minutes per IP."""

    # Find user by email
    person = db.query(Person).filter(Person.email == request.email).first()
    if not person or not person.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(request.password, person.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Generate access + refresh tokens (pwd_iat allows revocation on password change).
    pwd_iat = _pwd_iat_for(person)
    access_token = create_access_token(data={"sub": person.id, "pwd_iat": pwd_iat})
    refresh_token = create_refresh_token(data={"sub": person.id, "pwd_iat": pwd_iat})

    return AuthResponse(
        person_id=person.id,
        org_id=person.org_id,
        name=person.name,
        email=person.email,
        roles=person.roles or [],
        timezone=person.timezone or "UTC",
        language=person.language or "en",
        token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    dependencies=[Depends(rate_limit("refresh_token"))],
)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a refresh token for a new access+refresh pair.

    Both tokens are rotated on every successful refresh, so the prior
    refresh token can no longer be used after this call (one-time-use
    semantics for the rotation, even though the JWT itself is still
    technically valid until ``exp`` — the mobile client overwrites the
    stored refresh token immediately).

    Validates:
    - JWT signature + non-expired
    - ``type == "refresh"`` (rejects access tokens)
    - The user still exists
    - ``pwd_iat`` matches the user's current ``password_changed_at`` —
      i.e., the refresh token was not invalidated by a subsequent
      password change.
    """
    payload = decode_refresh_token(request.refresh_token)
    person_id = payload.get("sub")
    token_pwd_iat = payload.get("pwd_iat")

    if not person_id or token_pwd_iat is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # If the password was changed after this refresh token was issued,
    # invalidate the refresh token (mirrors how access tokens get
    # revoked via pwd_iat in get_current_user).
    if abs(_pwd_iat_for(person) - float(token_pwd_iat)) > 1.0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalidated by password change",
        )

    # Rotate both tokens.
    pwd_iat = _pwd_iat_for(person)
    new_access = create_access_token(data={"sub": person.id, "pwd_iat": pwd_iat})
    new_refresh = create_refresh_token(data={"sub": person.id, "pwd_iat": pwd_iat})

    return RefreshResponse(token=new_access, refresh_token=new_refresh)


@router.post("/check-email")
def check_email(email: EmailStr, db: Session = Depends(get_db)):
    """Check if email is already registered."""
    exists = db.query(Person).filter(Person.email == email).first() is not None
    return {"exists": exists}
