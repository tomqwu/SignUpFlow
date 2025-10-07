"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
import traceback

from api.database import init_db
from api.logging_config import logger
from api.routers import (
    password_reset,
    analytics,
    auth,
    organizations,
    people,
    teams,
    events,
    constraints,
    solver,
    solutions,
    availability,
    conflicts,
    invitations,
    calendar,
)

# Create FastAPI app
app = FastAPI(
    title="Rostio API",
    description="Team scheduling made simple - constraint-based roster scheduling",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Error handling middleware
@app.middleware("http")
async def error_logging_middleware(request: Request, call_next):
    """Log all errors and return user-friendly messages."""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again later."}
        )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "rostio-api", "version": "0.2.0"}


# Register routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(organizations.router, prefix="/api")
app.include_router(people.router, prefix="/api")
app.include_router(teams.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(constraints.router, prefix="/api")
app.include_router(solver.router, prefix="/api")
app.include_router(solutions.router, prefix="/api")
app.include_router(availability.router, prefix="/api")
app.include_router(conflicts.router, prefix="/api")
app.include_router(password_reset.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(invitations.router, prefix="/api")
app.include_router(calendar.router, prefix="/api")

# API Info endpoint
@app.get("/api", tags=["root"])
def api_info():
    """API information endpoint."""
    return {
        "service": "Rostio API",
        "version": "0.2.0",
        "description": "Constraint-based scheduling for teams, events, and resources",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "organizations": "/api/organizations",
            "people": "/api/people",
            "teams": "/api/teams",
            "events": "/api/events",
            "constraints": "/api/constraints",
            "solver": "/api/solver/solve",
            "solutions": "/api/solutions",
        },
    }

# Mount locales directory for i18n
locales_path = os.path.join(os.path.dirname(__file__), "..", "locales")
if os.path.exists(locales_path):
    app.mount("/locales", StaticFiles(directory=locales_path), name="locales")

# Mount static files (frontend) at root
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Startup event
@app.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    init_db()
    logger.info("🚀 Rostio API started")
    logger.info("📖 API docs available at http://localhost:8000/docs")
    print("🚀 Rostio API started")
    print("📖 API docs available at http://localhost:8000/docs")


# Shutdown event
@app.on_event("shutdown")
def on_shutdown():
    """Cleanup on shutdown."""
    print("👋 Rostio API shutting down")


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
