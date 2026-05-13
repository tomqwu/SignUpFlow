"""JWT Authentication and security utilities for Rostio API."""

import os
from datetime import timedelta

import bcrypt
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from api.timeutils import utcnow

# passlib<1.7.5 expects bcrypt.__about__.__version__; newer bcrypt dropped it.
if not hasattr(bcrypt, "__about__"):

    class _BcryptAbout:
        __version__ = getattr(bcrypt, "__version__", "0")

    bcrypt.__about__ = _BcryptAbout()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-use-env-var")
ALGORITHM = "HS256"
# Read from env via direct os.getenv (not Settings) so the smoke runbook's
# short-TTL workflow works without restart-coupling to Settings reload.
# Default 24h matches the prior hardcoded value. Fractional hours via
# float lets the mobile refresh-interceptor smoke set e.g. 0.05 (3 min)
# to deterministically force a 401 during a smoke walk.
ACCESS_TOKEN_EXPIRE_MINUTES = int(float(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24")) * 60)
REFRESH_TOKEN_EXPIRE_DAYS = 30  # Refresh token lifetime (rotated on every refresh)

# Token type marker — distinguishes access from refresh in the `type` claim.
# Access tokens are accepted by `verify_token` for normal API auth; refresh
# tokens are only accepted by `decode_refresh_token` for the /auth/refresh
# endpoint. This prevents stealing one and using it as the other.
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password

    Note:
        Bcrypt has a 72-byte limit. Longer passwords are truncated.
    """
    # Bcrypt has a 72-byte limit - truncate if necessary
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode("utf-8", errors="ignore")

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to compare against

    Returns:
        True if password matches hash
    """
    # Bcrypt has a 72-byte limit - truncate if necessary
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        plain_password = password_bytes.decode("utf-8", errors="ignore")

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Tags the token with ``type:"access"`` so refresh-only endpoints can
    reject access tokens being misused as refresh tokens (and vice versa).

    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = utcnow() + expires_delta
    else:
        expire = utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": TOKEN_TYPE_ACCESS})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT refresh token.

    Same shape as the access token but with ``type:"refresh"`` and a
    longer lifetime. Refresh tokens are only accepted by
    ``/auth/refresh`` (via ``decode_refresh_token``); they cannot be used
    to authenticate normal API requests.

    Args:
        data: Dictionary of claims to encode (must include ``sub`` and
              ``pwd_iat`` so the refresh endpoint can detect post-password-
              change invalidation, mirroring the access-token claims).
        expires_delta: Optional custom expiration; default
              ``REFRESH_TOKEN_EXPIRE_DAYS``.

    Returns:
        JWT refresh token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = utcnow() + expires_delta
    else:
        expire = utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": TOKEN_TYPE_REFRESH})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT access token.

    Rejects refresh tokens (``type:"refresh"``) so they can't be used to
    authenticate normal API requests. Tokens minted before the ``type``
    claim was introduced are also accepted for backward compatibility —
    they were always access tokens by construction.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or is a refresh token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_type = payload.get("type")
    if token_type is not None and token_type != TOKEN_TYPE_ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def decode_refresh_token(token: str) -> dict:
    """
    Decode and validate a refresh token. Used by /auth/refresh.

    Rejects access tokens (``type != "refresh"``) so they can't be used
    to mint new access tokens.

    Args:
        token: Refresh token string

    Returns:
        Decoded token payload (sub, pwd_iat, exp, type)

    Raises:
        HTTPException: If invalid, expired, or not a refresh token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != TOKEN_TYPE_REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token type",
        )

    return payload


def get_password_hash(password: str) -> str:
    """
    Alias for hash_password for backward compatibility.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password
    """
    return hash_password(password)
