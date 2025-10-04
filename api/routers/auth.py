"""Authentication endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
import hashlib
import secrets
import time

from api.database import get_db
from roster_cli.db.models import Person, Organization

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
    token: str


# Helper functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == password_hash


def generate_token() -> str:
    """Generate a simple session token."""
    return secrets.token_urlsafe(32)


# Endpoints
@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account."""

    # Check if email already exists
    existing = db.query(Person).filter(Person.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == request.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Create person ID from email
    person_id = f"person_{request.email.split('@')[0]}_{int(time.time())}"

    # Hash password
    password_hash = hash_password(request.password)

    # Create person
    person = Person(
        id=person_id,
        org_id=request.org_id,
        name=request.name,
        email=request.email,
        password_hash=password_hash,
        roles=request.roles or [],
        extra_data={}
    )

    db.add(person)
    db.commit()
    db.refresh(person)

    # Generate token
    token = generate_token()

    return AuthResponse(
        person_id=person.id,
        org_id=person.org_id,
        name=person.name,
        email=person.email,
        roles=person.roles or [],
        timezone=person.timezone or "UTC",
        token=token
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""

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

    # Generate token
    token = generate_token()

    return AuthResponse(
        person_id=person.id,
        org_id=person.org_id,
        name=person.name,
        email=person.email,
        roles=person.roles or [],
        timezone=person.timezone or "UTC",
        token=token
    )


@router.post("/check-email")
def check_email(email: EmailStr, db: Session = Depends(get_db)):
    """Check if email is already registered."""
    exists = db.query(Person).filter(Person.email == email).first() is not None
    return {"exists": exists}
