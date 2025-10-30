"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import os
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Sentry for error tracking (production only)
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_dsn = os.getenv("SENTRY_DSN")
environment = os.getenv("ENVIRONMENT", "development")

if sentry_dsn and environment != "development":
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
        # Adjust in production to reduce overhead (e.g., 0.1 = 10%)
        traces_sample_rate=0.1 if environment == "production" else 1.0,
        # Send errors from all environments except development
        send_default_pii=False,  # Don't send personally identifiable information
        attach_stacktrace=True,
        debug=False,
    )
    print(f"✅ Sentry initialized for {environment} environment")
else:
    print(f"ℹ️  Sentry disabled (SENTRY_DSN not set or environment is development)")

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
    sms,
    billing,
    webhooks,
    notifications,
    onboarding,
)


# Application lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    init_db()
    logger.info("🚀 SignUpFlow API started")
    logger.info("📖 API docs available at http://localhost:8000/docs")
    print("🚀 SignUpFlow API started")
    print("📖 API docs available at http://localhost:8000/docs")

    yield

    # Shutdown
    print("👋 SignUpFlow API shutting down")


# Create FastAPI app with lifespan handler
app = FastAPI(
    title="SignUpFlow API",
    description="AI-powered volunteer scheduling and sign-up management",
    version="1.0.0",
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

# Security headers middleware
from api.utils.security_headers_middleware import add_security_headers_middleware
add_security_headers_middleware(app)

# Rate limiting is applied via decorators in routers (see api/utils/rate_limit_middleware.py)
# reCAPTCHA is applied via middleware (see api/utils/recaptcha_middleware.py)

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
    """
    Health check endpoint with database connectivity check.

    Used by:
    - Docker health checks
    - Load balancers
    - Uptime monitoring (e.g., Uptime Robot, Better Stack)
    - Kubernetes liveness/readiness probes

    Returns:
        200 OK: Service and database are healthy
        503 Service Unavailable: Database connection failed
    """
    from api.database import SessionLocal
    from sqlalchemy import text

    health_status = {
        "status": "healthy",
        "service": "signupflow-api",
        "version": "1.0.0",
        "database": "unknown"
    }

    # Check database connectivity
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        return JSONResponse(
            status_code=503,
            content=health_status
        )

    return health_status


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
app.include_router(notifications.router, prefix="/api")
app.include_router(onboarding.router, prefix="/api")
app.include_router(sms.router)
app.include_router(billing.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")

# API Info endpoint
@app.get("/api", tags=["root"])
def api_info():
    """API information endpoint."""
    return {
        "service": "SignUpFlow API",
        "version": "1.0.0",
        "description": "AI-powered volunteer scheduling and sign-up management",
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
