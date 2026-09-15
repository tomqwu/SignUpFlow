"""
FastAPI dependencies for rate limiting.
"""

import os
from collections.abc import Callable
from ipaddress import ip_address, ip_network

from fastapi import HTTPException, Request, status

from api.utils.rate_limiter import RATE_LIMITS, RateLimitBackendUnavailableError, rate_limiter


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.

    Forwarded addresses are considered only when the direct peer belongs to a
    network listed in TRUSTED_PROXY_IPS. Invalid proxy configuration or an
    invalid chain fails closed to the direct peer.
    """
    direct_host = request.client.host if request.client else "unknown"
    configured = [item.strip() for item in os.getenv("TRUSTED_PROXY_IPS", "").split(",")]
    configured = [item for item in configured if item]
    if not configured:
        return direct_host

    try:
        trusted_networks = tuple(ip_network(item, strict=False) for item in configured)
        direct_address = ip_address(direct_host)
    except ValueError:
        return direct_host
    if not any(direct_address in network for network in trusted_networks):
        return direct_host

    forwarded = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For", "")
    try:
        chain = [ip_address(item.strip()) for item in forwarded.split(",") if item.strip()]
    except ValueError:
        return direct_host
    for address in reversed(chain):
        if not any(address in network for network in trusted_networks):
            return str(address)
    return direct_host


def rate_limit(limit_type: str) -> Callable[[Request], bool]:
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

    def check_rate_limit(request: Request) -> bool:
        # Disable rate limiting during tests or when explicitly toggled
        if os.getenv("TESTING") == "true" or os.getenv("DISABLE_RATE_LIMITS") == "true":
            return True

        client_ip = get_client_ip(request)

        # Keep local iteration frictionless, but never grant a production
        # bypass merely because a reverse proxy connects over loopback.
        if os.getenv("ENVIRONMENT", "development").lower() != "production" and client_ip in (
            "127.0.0.1",
            "localhost",
            "::1",
        ):
            return True

        key = f"{limit_type}:{client_ip}"

        config = RATE_LIMITS.get(limit_type, {"max_requests": 10, "window_seconds": 60})

        try:
            allowed = rate_limiter.is_allowed(
                key, max_requests=config["max_requests"], window_seconds=config["window_seconds"]
            )
        except RateLimitBackendUnavailableError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Request protection is temporarily unavailable. Please try again.",
                headers={"Retry-After": "5"},
            ) from exc

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )

        return True

    check_rate_limit.rate_limit_type = limit_type  # type: ignore[attr-defined]
    return check_rate_limit
