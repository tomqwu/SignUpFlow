"""
FastAPI dependencies for rate limiting.
"""

import os
from fastapi import Request, HTTPException, status
from api.utils.rate_limiter import rate_limiter, RATE_LIMITS


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.

    Checks X-Forwarded-For header first (for proxies/load balancers),
    then falls back to direct client IP.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, get the first one
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(limit_type: str):
    """
    Dependency factory for rate limiting.

    Usage:
        @router.post("/signup", dependencies=[Depends(rate_limit("signup"))])
        async def signup(...):
            ...

    Args:
        limit_type: Type of rate limit (e.g., "signup", "login")

    Note:
        Rate limiting is disabled during tests (when TESTING env var is set).
    """
    def check_rate_limit(request: Request):
        # Disable rate limiting during tests or when explicitly toggled
        if os.getenv("TESTING") == "true" or os.getenv("DISABLE_RATE_LIMITS") == "true":
            return True

        client_ip = get_client_ip(request)

        # Disable rate limiting for localhost/development
        if client_ip in ("127.0.0.1", "localhost", "::1"):
            return True

        key = f"{limit_type}:{client_ip}"

        config = RATE_LIMITS.get(limit_type, {"max_requests": 10, "window_seconds": 60})

        if not rate_limiter.is_allowed(
            key,
            max_requests=config["max_requests"],
            window_seconds=config["window_seconds"]
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again later."
            )

        return True

    return check_rate_limit
