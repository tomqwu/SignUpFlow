"""Web app assembly: Jinja2 templates + static mount + routers +
the unauthenticated-redirect handler. Mounted into the main FastAPI
app from api/main.py."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

_WEB_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(_WEB_DIR / "templates"))

# Combined web router (auth + pages). Imported lazily inside functions
# elsewhere to avoid circular imports with `templates`.
from web import auth as _auth  # noqa: E402
from web.routers import pages as _pages  # noqa: E402
from web.deps import _RedirectToLogin  # noqa: E402

router = APIRouter()
router.include_router(_auth.router)
router.include_router(_pages.router)


def mount_web(app: FastAPI) -> None:
    """Wire the web app into the main FastAPI instance."""
    app.mount(
        "/web/static",
        StaticFiles(directory=str(_WEB_DIR / "static")),
        name="web-static",
    )
    # include_in_schema=False keeps the HTML routes out of /openapi.json
    # so they don't leak into the Dart client codegen or break the
    # contract snapshot test (tests/contract/openapi.snapshot.json).
    app.include_router(router, include_in_schema=False)

    @app.exception_handler(_RedirectToLogin)
    async def _redirect_to_login(request: Request, exc: _RedirectToLogin):
        return RedirectResponse(url="/auth/login", status_code=303)
