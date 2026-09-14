"""Authentication endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.dependencies import get_current_user
from api.models import Organization, Person
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
    """Atomic organization and first-administrator bootstrap request."""

    org_id: str = Field(..., min_length=1, description="Organization ID")
    org_name: str = Field(..., min_length=1, description="Organization name")
    region: str | None = Field(None, description="Region code (e.g., CA-ON, US-CA)")
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    timezone: str = Field(default="UTC", description="User timezone")
    language: str = Field(default="en", description="User language")
    model_config = ConfigDict(extra="forbid")


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


class ChangePasswordRequest(BaseModel):
    """Authenticated self-service password change."""

    current_password: str = Field(..., description="The user's existing password")
    new_password: str = Field(..., min_length=6, description="New password (min 6 characters)")


# Endpoints
@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("signup"))],
)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create one organization and its first admin in a single transaction."""

    existing = db.query(Person).filter(Person.email == request.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    existing_org = db.query(Organization).filter(Organization.id == request.org_id).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization already exists; join it through an invitation",
        )

    person_id = f"person_{request.email.split('@')[0]}_{uuid.uuid4().hex[:8]}"
    password_hash = hash_password(request.password)
    organization = Organization(
        id=request.org_id,
        name=request.org_name,
        region=request.region,
        config={},
    )
    person = Person(
        id=person_id,
        org_id=request.org_id,
        name=request.name,
        email=request.email,
        password_hash=password_hash,
        roles=["admin"],
        timezone=request.timezone,
        language=request.language,
        password_changed_at=utcnow(),
        extra_data={},
    )

    db.add_all([organization, person])
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization or owner account already exists",
        ) from exc
    db.refresh(person)

    # Generate access + refresh tokens (pwd_iat allows revocation on password change;
    # rtv binds the refresh token to the user's current refresh-token version, so
    # rotating-on-refresh invalidates the prior refresh JWT).
    access_token = create_access_token(
        data={"sub": person.id, "org_id": person.org_id, "pwd_iat": _pwd_iat_for(person)}
    )
    refresh_token = create_refresh_token(
        data={
            "sub": person.id,
            "org_id": person.org_id,
            "pwd_iat": _pwd_iat_for(person),
            "rtv": person.refresh_token_version,
        }
    )

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
    if not person or person.status != "active" or not person.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(request.password, person.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Generate access + refresh tokens (pwd_iat allows revocation on password
    # change; rtv binds the refresh token to the user's current
    # refresh_token_version so rotating-on-refresh invalidates prior tokens).
    access_token = create_access_token(
        data={"sub": person.id, "org_id": person.org_id, "pwd_iat": _pwd_iat_for(person)}
    )
    refresh_token = create_refresh_token(
        data={
            "sub": person.id,
            "org_id": person.org_id,
            "pwd_iat": _pwd_iat_for(person),
            "rtv": person.refresh_token_version,
        }
    )

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


@router.post("/change-password", response_model=AuthResponse)
def change_password(
    request: ChangePasswordRequest,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the authenticated user's password. Verifies the current
    password, then rotates the hash and stamps password_changed_at so
    previously-issued access tokens are invalidated (same revocation
    mechanism as password reset). Returns a fresh token pair so the
    caller stays signed in."""
    if not current_user.password_hash or not verify_password(
        request.current_password, current_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.password_hash = hash_password(request.new_password)
    current_user.password_changed_at = utcnow()
    db.commit()
    db.refresh(current_user)

    access_token = create_access_token(
        data={
            "sub": current_user.id,
            "org_id": current_user.org_id,
            "pwd_iat": _pwd_iat_for(current_user),
        }
    )
    refresh_token = create_refresh_token(
        data={
            "sub": current_user.id,
            "org_id": current_user.org_id,
            "pwd_iat": _pwd_iat_for(current_user),
            "rtv": current_user.refresh_token_version,
        }
    )
    return AuthResponse(
        person_id=current_user.id,
        org_id=current_user.org_id,
        name=current_user.name,
        email=current_user.email,
        roles=current_user.roles or [],
        timezone=current_user.timezone or "UTC",
        language=current_user.language or "en",
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

    On every successful refresh:
    - Both tokens are rotated and returned.
    - ``Person.refresh_token_version`` is incremented and persisted.
    - The new refresh JWT carries the post-increment ``rtv``.
    - **The prior refresh JWT becomes unusable** because its ``rtv`` is
      now older than the user's current ``refresh_token_version``.

    Validates:
    - JWT signature + non-expired
    - ``type == "refresh"`` (rejects access tokens)
    - ``sub`` (person_id) AND ``org_id`` claims present and match a
      live user (multi-tenant filter on the DB lookup; project rule:
      every Person query filters by ``org_id``).
    - ``pwd_iat`` matches current ``password_changed_at`` (refresh
      issued before a password change is rejected).
    - ``rtv`` matches current ``refresh_token_version`` (replay of a
      prior refresh JWT is rejected).
    """
    payload = decode_refresh_token(request.refresh_token)
    person_id = payload.get("sub")
    token_org_id = payload.get("org_id")
    token_pwd_iat = payload.get("pwd_iat")
    token_rtv = payload.get("rtv")

    if not person_id or not token_org_id or token_pwd_iat is None or token_rtv is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Multi-tenant filter: lookup must match BOTH person_id AND org_id.
    person = (
        db.query(Person)
        .filter(
            Person.id == person_id,
            Person.org_id == token_org_id,
            Person.status == "active",
        )
        .first()
    )
    if not person:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # If the password was changed after this refresh token was issued,
    # invalidate it (mirrors how access tokens are revoked via pwd_iat).
    if abs(_pwd_iat_for(person) - float(token_pwd_iat)) > 1.0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalidated by password change",
        )

    # ATOMIC rotate: a single conditional UPDATE filtered by id + org_id +
    # current refresh_token_version. Whichever request commits first wins;
    # all others get rowcount==0 and 401, even under concurrent traffic
    # with the same refresh JWT.
    expected_rtv = int(token_rtv)
    new_rtv = expected_rtv + 1
    rows = (
        db.query(Person)
        .filter(
            Person.id == person_id,
            Person.org_id == token_org_id,
            Person.status == "active",
            Person.refresh_token_version == expected_rtv,
        )
        .update({Person.refresh_token_version: new_rtv}, synchronize_session=False)
    )
    db.commit()

    if rows == 0:
        # Either the rtv was already stale at decode time, or we lost a
        # concurrent rotation race. Either way the token is dead.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token superseded",
        )

    # Re-read the now-updated row so we mint tokens from a known-good value.
    db.refresh(person)

    new_access = create_access_token(
        data={"sub": person.id, "org_id": person.org_id, "pwd_iat": _pwd_iat_for(person)}
    )
    new_refresh = create_refresh_token(
        data={
            "sub": person.id,
            "org_id": person.org_id,
            "pwd_iat": _pwd_iat_for(person),
            "rtv": person.refresh_token_version,
        }
    )

    return RefreshResponse(token=new_access, refresh_token=new_refresh)


@router.post("/check-email")
def check_email(email: EmailStr, db: Session = Depends(get_db)):
    """Check if email is already registered."""
    exists = db.query(Person).filter(Person.email == email).first() is not None
    return {"exists": exists}
