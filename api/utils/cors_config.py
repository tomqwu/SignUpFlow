"""CORS origin parsing from CORS_ALLOWED_ORIGINS env var."""

import os

DEFAULT_DEV_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]


def get_cors_origins() -> list[str]:
    """Return the configured allowed origins, or local-dev defaults if unset."""
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
    if not raw:
        return list(DEFAULT_DEV_ORIGINS)
    return [o.strip() for o in raw.split(",") if o.strip()]
