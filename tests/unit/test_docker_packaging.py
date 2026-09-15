"""Production Docker image and Compose topology invariants."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_dockerfile_packages_web_for_a_nonroot_single_worker_runtime():
    df = (ROOT / "Dockerfile").read_text()
    # api.main does `from web.app import mount_web` — the app won't start
    # without web/ in the image.
    assert "COPY web/ ./web/" in df
    assert "COPY api/ ./api/" in df
    assert "COPY docker-entrypoint.sh" in df
    assert 'ENTRYPOINT ["/app/docker-entrypoint.sh"]' in df
    assert "uvicorn" in df and "api.main:app" in df
    assert "USER signupflow" in df
    assert '"--workers", "1"' in df
    assert "COPY --from=builder /usr/local/bin" not in df


def test_entrypoint_only_executes_the_declared_container_command():
    p = ROOT / "docker-entrypoint.sh"
    txt = p.read_text()
    assert "alembic" not in txt
    assert 'exec "$@"' in txt
    # Executable bit tracked in git so the image can run it.
    assert os.stat(p).st_mode & stat.S_IXUSR


def test_compose_runs_one_migration_job_before_api_replicas():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    svcs = compose["services"]

    assert "db" in svcs and "postgres" in svcs["db"]["image"]
    migrate = svcs["migrate"]
    api = svcs["api"]
    assert "build" in migrate and "build" in api
    assert migrate["depends_on"]["db"]["condition"] == "service_healthy"
    assert migrate["restart"] == "no"
    assert migrate["command"] == ["python", "-m", "alembic", "upgrade", "head"]
    assert api["depends_on"]["migrate"]["condition"] == "service_completed_successfully"
    assert api["depends_on"]["redis"]["condition"] == "service_healthy"
    # API talks to the compose Postgres, not sqlite.
    assert "postgresql://" in api["environment"]["DATABASE_URL"]
    assert "@db:5432/" in api["environment"]["DATABASE_URL"]
    assert migrate["environment"]["DATABASE_URL"] == api["environment"]["DATABASE_URL"]
    # Container health reflects dependency readiness; /health remains process liveness.
    assert "/ready" in " ".join(api["healthcheck"]["test"])


def test_compose_keeps_datastores_private_and_runtime_source_immutable():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    svcs = compose["services"]

    assert "ports" not in svcs["db"]
    assert "ports" not in svcs["redis"]
    assert "volumes" not in svcs["api"]
    assert "container_name" not in svcs["api"]
    assert svcs["api"]["read_only"] is True
    assert svcs["migrate"]["read_only"] is True
    assert svcs["api"]["cap_drop"] == ["ALL"]
