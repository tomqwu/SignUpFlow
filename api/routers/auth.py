"""Authentication endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
import time

from api.database import get_db
from api.dependencies import get_organization_by_id
from api.security import hash_password, verify_password, create_access_token
from api.models import Person, Organization
from api.utils.rate_limit_middleware import rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


# Schemas
class SignupRequest(BaseModel):
    """Signup request."""
    org_id: str = Field(..., description="Organization ID")
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    roles: Optional[list[str]] = Field(default_factory=list, description="User roles")


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


# Endpoints
@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit("signup"))])
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account. Rate limited to 3 requests per hour per IP."""

    # Check if email already exists
    existing = db.query(Person).filter(Person.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Verify organization exists
    org = get_organization_by_id(request.org_id, db)

    # Check if this is the first user in the organization
    existing_users_count = db.query(Person).filter(Person.org_id == request.org_id).count()
    is_first_user = existing_users_count == 0

    # Create person ID from email
    person_id = f"person_{request.email.split('@')[0]}_{int(time.time())}"

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
        extra_data={}
    )

    db.add(person)
    db.commit()
    db.refresh(person)

    # Generate JWT access token
    access_token = create_access_token(data={"sub": person.id})

    return AuthResponse(
        person_id=person.id,
        org_id=person.org_id,
        name=person.name,
        email=person.email,
        roles=person.roles or [],
        timezone=person.timezone or "UTC",
        language=person.language or "en",
        token=access_token
    )


@router.post("/login", response_model=AuthResponse, dependencies=[Depends(rate_limit("login"))])
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password. Rate limited to 5 requests per 5 minutes per IP."""

    # Find user by email
    person = db.query(Person).filter(Person.email == request.email).first()
    if not person or not person.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(request.password, person.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT access token
    access_token = create_access_token(data={"sub": person.id})

    return AuthResponse(
        person_id=person.id,
        org_id=person.org_id,
        name=person.name,
        email=person.email,
        roles=person.roles or [],
        timezone=person.timezone or "UTC",
        language=person.language or "en",
        token=access_token
    )


@router.post("/check-email")
def check_email(email: EmailStr, db: Session = Depends(get_db)):
    """Check if email is already registered."""
    exists = db.query(Person).filter(Person.email == email).first() is not None
    return {"exists": exists}
