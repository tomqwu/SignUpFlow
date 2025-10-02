"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from api.database import init_db
from api.routers import (
    auth,
    organizations,
    people,
    teams,
    events,
    constraints,
    solver,
    solutions,
    availability,
)

# Create FastAPI app
app = FastAPI(
    title="Roster API",
    description="Microservice API for constraint-based roster scheduling",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
    return {"status": "healthy", "service": "roster-api", "version": "0.2.0"}


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

# API Info endpoint
@app.get("/api", tags=["root"])
def api_info():
    """API information endpoint."""
    return {
        "service": "Roster API",
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

# Mount static files (frontend) at root
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Startup event
@app.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    init_db()
    print("🚀 Roster API started")
    print("📖 API docs available at http://localhost:8000/docs")


# Shutdown event
@app.on_event("shutdown")
def on_shutdown():
    """Cleanup on shutdown."""
    print("👋 Roster API shutting down")


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
