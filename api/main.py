"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.database import init_db
from api.routers import (
    organizations,
    people,
    teams,
    events,
    constraints,
    solver,
    solutions,
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


# Root endpoint
@app.get("/", tags=["root"])
def root():
    """Root endpoint with API information."""
    return {
        "service": "Roster API",
        "version": "0.2.0",
        "description": "Constraint-based scheduling for teams, events, and resources",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "organizations": "/organizations",
            "people": "/people",
            "teams": "/teams",
            "events": "/events",
            "constraints": "/constraints",
            "solver": "/solver/solve",
            "solutions": "/solutions",
        },
    }


# Register routers
app.include_router(organizations.router)
app.include_router(people.router)
app.include_router(teams.router)
app.include_router(events.router)
app.include_router(constraints.router)
app.include_router(solver.router)
app.include_router(solutions.router)


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
