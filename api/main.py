"""FastAPI application entry point."""

# Tests and owned subprocesses opt out so a developer .env cannot restore
# provider credentials that the local safety boundary deliberately removed.
import os
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.routing import APIRoute
from starlette.responses import Response

if os.getenv("SIGNUPFLOW_LOAD_DOTENV", "true").lower() == "true":
    load_dotenv()

from api.core.runtime_config import validate_production_environment
from api.database import SessionLocal, init_db
from api.logging_config import logger
from api.observability import capture_unhandled_exception, initialize_error_reporting
from api.operational_alerts import record_operational_signal
from api.routers import (
    analytics,
    assignments,
    audit,
    auth,
    availability,
    billing,
    calendar,
    conflicts,
    constraints,
    events,
    holidays,
    invitations,
    notifications,
    organizations,
    password_reset,
    people,
    recurring_events,
    resources,
    sms,
    solutions,
    solver,
    teams,
    webhooks,
)


# Application lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown."""
    validate_production_environment()
    reporting = initialize_error_reporting()
    try:
        init_db()
    except Exception as exc:
        capture_unhandled_exception(exc)
        logger.error(
            "application.startup_failed",
            extra={
                "event": "application.startup_failed",
                "error_type": type(exc).__name__,
            },
        )
        raise

    logger.info(
        "application.started",
        extra={
            "event": "application.started",
            "error_reporting": (reporting.provider if reporting.enabled else reporting.reason),
        },
    )

    yield

    logger.info("application.stopping", extra={"event": "application.stopping"})


def _snake_to_camel(name: str) -> str:
    head, *tail = name.split("_")
    return head + "".join(part.title() for part in tail)


def _generate_operation_id(route: APIRoute) -> str:
    """Return stable Dart-codegen operation IDs from route function names."""
    return _snake_to_camel(route.name)


app = FastAPI(
    title="SignUpFlow API",
    description="AI-powered volunteer scheduling and sign-up management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    generate_unique_id_function=_generate_operation_id,
)


@app.middleware("http")
async def error_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Capture unhandled errors once and return a generic correlated response."""
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        capture_unhandled_exception(exc)
        logger.error(
            "request.unhandled_error",
            extra={
                "event": "request.unhandled_error",
                "error_type": type(exc).__name__,
                "method": request.method,
                "path": request.url.path,
            },
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )


from api.utils.cors_config import get_cors_origins
from api.utils.request_id_middleware import RequestIDMiddleware
from api.utils.security_headers_middleware import add_security_headers_middleware

add_security_headers_middleware(app)
app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"], response_model=None)
def health_check() -> dict[str, str]:
    """Return process liveness without opening a dependency connection."""
    return {
        "status": "healthy",
        "service": "signupflow-api",
        "version": "1.0.0",
    }


@app.get("/ready", include_in_schema=False, response_model=None)
def readiness_check() -> dict[str, str] | JSONResponse:
    """Readiness probe (ops-only, not part of the client contract).

    Distinct from /health (liveness): a 503 here tells an orchestrator
    to keep this instance out of rotation until the DB is reachable.
    """
    from sqlalchemy import text

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:
        record_operational_signal("database.readiness", healthy=False)
        logger.warning(
            "readiness.dependency_unavailable",
            extra={
                "event": "readiness.dependency_unavailable",
                "signal": "database.readiness",
                "error_type": type(exc).__name__,
            },
        )
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "dependency_unavailable"},
        )
    record_operational_signal("database.readiness", healthy=True)
    return {"status": "ready"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(people.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(constraints.router, prefix="/api/v1")
app.include_router(solver.router, prefix="/api/v1")
app.include_router(solutions.router, prefix="/api/v1")
app.include_router(availability.router, prefix="/api/v1")
app.include_router(conflicts.router, prefix="/api/v1")
app.include_router(password_reset.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(invitations.router, prefix="/api/v1")
app.include_router(calendar.router, prefix="/api/v1")
app.include_router(assignments.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(recurring_events.router, prefix="/api/v1")
app.include_router(resources.router, prefix="/api/v1")
app.include_router(holidays.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(webhooks.stripe_router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
# sms.router self-prefixes "/api/sms" (not the /api/v1 convention) — mount as-is.
app.include_router(sms.router)


@app.get("/api/v1", tags=["root"], response_model=None)
def api_info() -> dict[str, object]:
    """API information endpoint."""
    return {
        "service": "SignUpFlow API",
        "version": "1.0.0",
        "description": "AI-powered volunteer scheduling and sign-up management",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "organizations": "/api/v1/organizations",
            "people": "/api/v1/people",
            "teams": "/api/v1/teams",
            "events": "/api/v1/events",
            "constraints": "/api/v1/constraints",
            "solver": "/api/v1/solver/solve",
            "solutions": "/api/v1/solutions",
        },
    }


@app.get("/api", tags=["root"], include_in_schema=False)
def api_redirect() -> RedirectResponse:
    """Redirect bare /api to versioned /api/v1 for one release."""
    return RedirectResponse(url="/api/v1", status_code=308)


# Server-rendered responsive web app (Sprint 11). Mounted last; routes
# are include_in_schema=False so they stay out of the OpenAPI contract.
from web.app import mount_web  # noqa: E402

mount_web(app)


def start() -> None:
    """Start the API server (used by poetry script)."""
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    start()
