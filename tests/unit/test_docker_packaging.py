"""Marathon P3.18 — production Docker image + compose invariants.

Static guards (no Docker daemon needed): the image must package the web
app and migrate on boot, and compose must wire the API to Postgres. The
`web/`-missing case is a real regression that crashed the image.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_dockerfile_packages_web_and_migrates():
    df = (ROOT / "Dockerfile").read_text()
    # api.main does `from web.app import mount_web` — the app won't start
    # without web/ in the image.
    assert "COPY web/ ./web/" in df
    assert "COPY api/ ./api/" in df
    assert "COPY docker-entrypoint.sh" in df
    assert 'ENTRYPOINT ["/app/docker-entrypoint.sh"]' in df
    assert "uvicorn" in df and "api.main:app" in df


def test_entrypoint_runs_migrations_then_execs():
    p = ROOT / "docker-entrypoint.sh"
    txt = p.read_text()
    assert "alembic upgrade head" in txt
    assert 'exec "$@"' in txt
    # Executable bit tracked in git so the image can run it.
    assert os.stat(p).st_mode & stat.S_IXUSR


def test_compose_wires_api_to_postgres():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    svcs = compose["services"]

    assert "db" in svcs and "postgres" in svcs["db"]["image"]
    api = svcs["api"]
    assert "build" in api
    # API waits for a healthy database.
    assert api["depends_on"]["db"]["condition"] == "service_healthy"
    # API talks to the compose Postgres, not sqlite.
    assert "postgresql://" in api["environment"]["DATABASE_URL"]
    assert "@db:5432/" in api["environment"]["DATABASE_URL"]
    # Container healthcheck hits the real /health endpoint.
    assert "/health" in " ".join(api["healthcheck"]["test"])
