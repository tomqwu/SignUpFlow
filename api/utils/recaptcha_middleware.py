"""
reCAPTCHA middleware for FastAPI endpoints.

Provides a dependency that can be added to endpoints to require reCAPTCHA verification.
"""

import os
from fastapi import HTTPException, Request, Header
from typing import Optional

from api.utils.recaptcha import verify_recaptcha


async def require_recaptcha(
    request: Request,
    x_recaptcha_token: Optional[str] = Header(None)
):
    """
    FastAPI dependency that requires reCAPTCHA verification.

    Usage:
        @router.post("/signup", dependencies=[Depends(require_recaptcha)])
        def signup(...):
            ...

    The client must include the reCAPTCHA token in the X-Recaptcha-Token header.

    Args:
        request: FastAPI request object (for getting client IP)
        x_recaptcha_token: reCAPTCHA token from request header

    Raises:
        HTTPException: 400 if reCAPTCHA verification fails

    Note:
        reCAPTCHA is bypassed for localhost/127.0.0.1 during development.
    """
    # Get client IP for reCAPTCHA verification
    client_ip = request.client.host if request.client else None

    # Bypass reCAPTCHA for localhost/development
    if client_ip in ("127.0.0.1", "localhost", "::1"):
        return True

    # TEMPORARY: Bypass reCAPTCHA for all IPs during development/testing
    # TODO: Enable reCAPTCHA with valid keys in production
    environment = os.getenv("ENVIRONMENT", "production")
    if environment != "production":
        return True

    # Verify reCAPTCHA token (returns tuple of is_valid, score)
    is_valid, score = await verify_recaptcha(x_recaptcha_token or "", client_ip)

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="reCAPTCHA verification failed. Please try again."
        )

    return True
