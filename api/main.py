"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
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


# Application lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    init_db()
    logger.info("🚀 Rostio API started")
    logger.info("📖 API docs available at http://localhost:8000/docs")
    print("🚀 Rostio API started")
    print("📖 API docs available at http://localhost:8000/docs")

    yield

    # Shutdown
    print("👋 Rostio API shutting down")


# Create FastAPI app with lifespan handler
app = FastAPI(
    title="Rostio API",
    description="Team scheduling made simple - constraint-based roster scheduling",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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

# SPA fallback - serve index.html for all frontend routes
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve SPA - return index.html for all non-API routes."""
    # Skip API routes and special paths
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("locales/"):
        raise HTTPException(status_code=404, detail="Not Found")

    # Strip 'frontend/' prefix if present (since frontend_path already points to frontend/)
    if full_path.startswith("frontend/"):
        full_path = full_path[9:]  # Remove 'frontend/' prefix

    # Try to serve the specific file first (for assets like CSS, JS, images)
    file_path = os.path.join(frontend_path, full_path)
    if os.path.isfile(file_path):
        # Determine correct MIME type
        media_type = None
        if file_path.endswith('.js'):
            media_type = 'application/javascript'
        elif file_path.endswith('.css'):
            media_type = 'text/css'
        elif file_path.endswith('.json'):
            media_type = 'application/json'
        elif file_path.endswith('.html'):
            media_type = 'text/html'
        elif file_path.endswith('.svg'):
            media_type = 'image/svg+xml'
        elif file_path.endswith('.png'):
            media_type = 'image/png'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            media_type = 'image/jpeg'
        elif file_path.endswith('.gif'):
            media_type = 'image/gif'
        elif file_path.endswith('.ico'):
            media_type = 'image/x-icon'

        return FileResponse(file_path, media_type=media_type)

    # Otherwise serve index.html (SPA fallback)
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    raise HTTPException(status_code=404, detail="Frontend not found")


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
