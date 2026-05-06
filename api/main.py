"""FastAPI application entry point."""

import traceback
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load environment variables from .env file
load_dotenv()

from api.database import init_db
from api.logging_config import logger
from api.routers import (
    analytics,
    auth,
    availability,
    calendar,
    conflicts,
    constraints,
    events,
    invitations,
    organizations,
    password_reset,
    people,
    solutions,
    solver,
    teams,
)


# Application lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    init_db()
    logger.info("🚀 SignUpFlow API started")
    logger.info("📖 API docs available at http://localhost:8000/docs")
    print("🚀 SignUpFlow API started")
    print("📖 API docs available at http://localhost:8000/docs")

    yield

    print("👋 SignUpFlow API shutting down")


app = FastAPI(
    title="SignUpFlow API",
    description="AI-powered volunteer scheduling and sign-up management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.middleware("http")
async def error_logging_middleware(request: Request, call_next):
    """Log all errors and return user-friendly messages."""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error. Please try again later."}
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


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint with database connectivity check.

    Returns:
        200 OK: Service and database are healthy
        503 Service Unavailable: Database connection failed
    """
    from sqlalchemy import text

    from api.database import SessionLocal

    health_status = {
        "status": "healthy",
        "service": "signupflow-api",
        "version": "1.0.0",
        "database": "unknown",
    }

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        return JSONResponse(status_code=503, content=health_status)

    return health_status


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


@app.get("/api/v1", tags=["root"])
def api_info():
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
def api_redirect():
    """Redirect bare /api to versioned /api/v1 for one release."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/api/v1", status_code=308)


def start():
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
