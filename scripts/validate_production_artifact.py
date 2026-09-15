#!/usr/bin/env python3
"""Build and exercise an owned production image against private local datastores."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import tarfile
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import urlopen

import httpx

from examples.api_client_example import run_workflow
from scripts.local_tls_rehearsal import (
    LoopbackTLSProxy,
    TLSMaterial,
    verify_cookie_security,
)

ROOT = Path(__file__).resolve().parents[1]
POSTGRES_IMAGE = "postgres:16-alpine"
REDIS_IMAGE = "redis:7-alpine"
OWNERSHIP_LABEL = "io.signupflow.artifact-run"
RUN_ID_PATTERN = re.compile(r"^[a-f0-9]{8}$")
SHA_PATTERN = re.compile(r"^[a-f0-9]{40}$")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)(?:secret_key|api_key|auth_token|webhook_secret|password)\s*=\s*[^\s]+"
)


@dataclass(frozen=True)
class ArtifactTarget:
    """Names and commands for one isolated artifact validation run."""

    run_id: str
    source_sha: str
    password: str
    secret_key: str = field(default_factory=lambda: secrets.token_urlsafe(48))

    def __post_init__(self) -> None:
        if not RUN_ID_PATTERN.fullmatch(self.run_id):
            raise ValueError("Artifact run ID must be eight lowercase hex characters")
        if not SHA_PATTERN.fullmatch(self.source_sha):
            raise ValueError("Artifact source SHA must be 40 lowercase hex characters")
        if not self.password or len(self.secret_key) < 32:
            raise ValueError("Artifact credentials must not be empty")

    @property
    def image_tag(self) -> str:
        return f"signupflow-artifact:{self.source_sha[:12]}-{self.run_id}"

    @property
    def network_name(self) -> str:
        return f"signupflow-artifact-{self.run_id}"

    @property
    def postgres_name(self) -> str:
        return f"signupflow-artifact-pg-{self.run_id}"

    @property
    def redis_name(self) -> str:
        return f"signupflow-artifact-redis-{self.run_id}"

    @property
    def migration_name(self) -> str:
        return f"signupflow-artifact-migrate-{self.run_id}"

    @property
    def broker_probe_name(self) -> str:
        return f"signupflow-artifact-broker-{self.run_id}"

    @property
    def failed_app_name(self) -> str:
        return f"signupflow-artifact-unmigrated-{self.run_id}"

    @property
    def app_names(self) -> tuple[str, str]:
        return (
            f"signupflow-artifact-api-a-{self.run_id}",
            f"signupflow-artifact-api-b-{self.run_id}",
        )

    @property
    def database_name(self) -> str:
        return "signupflow_artifact"

    @property
    def unmigrated_database_name(self) -> str:
        return "signupflow_unmigrated"

    @property
    def database_user(self) -> str:
        return "signupflow_artifact"

    def network_command(self) -> list[str]:
        return [
            "docker",
            "network",
            "create",
            "--label",
            f"{OWNERSHIP_LABEL}={self.run_id}",
            self.network_name,
        ]

    def postgres_command(self) -> list[str]:
        return [
            "docker",
            "run",
            "--detach",
            "--name",
            self.postgres_name,
            "--label",
            f"{OWNERSHIP_LABEL}={self.run_id}",
            "--network",
            self.network_name,
            "--network-alias",
            "db",
            "--tmpfs",
            "/var/lib/postgresql/data:rw,noexec,nosuid,size=512m",
            "--env",
            f"POSTGRES_DB={self.database_name}",
            "--env",
            f"POSTGRES_USER={self.database_user}",
            "--env",
            f"POSTGRES_PASSWORD={self.password}",
            POSTGRES_IMAGE,
        ]

    def redis_command(self) -> list[str]:
        return [
            "docker",
            "run",
            "--detach",
            "--name",
            self.redis_name,
            "--label",
            f"{OWNERSHIP_LABEL}={self.run_id}",
            "--network",
            self.network_name,
            "--network-alias",
            "redis",
            "--tmpfs",
            "/data:rw,noexec,nosuid,size=64m",
            REDIS_IMAGE,
            "redis-server",
            "--requirepass",
            self.password,
            "--appendonly",
            "no",
        ]

    def database_url(self, database_name: str | None = None) -> str:
        name = database_name or self.database_name
        return f"postgresql://{self.database_user}:{quote_plus(self.password)}" f"@db:5432/{name}"

    def app_environment(self, database_name: str | None = None) -> dict[str, str]:
        redis_password = quote_plus(self.password)
        return {
            "ACCESS_TOKEN_EXPIRE_HOURS": "24",
            "API_BASE_URL": "https://artifact.signupflow.invalid",
            "APP_URL": "https://artifact.signupflow.invalid",
            "BILLING_ENABLED": "false",
            "CELERY_BROKER_URL": f"redis://:{redis_password}@redis:6379/0",
            "CELERY_RESULT_BACKEND": f"redis://:{redis_password}@redis:6379/0",
            "CORS_ALLOWED_ORIGINS": "https://artifact.signupflow.invalid",
            "DATABASE_URL": self.database_url(database_name),
            "DEBUG": "false",
            "DEBUG_RETURN_RESET_TOKEN": "false",
            "DISABLE_RATE_LIMITS": "false",
            "DISABLE_USAGE_LIMITS": "false",
            "EMAIL_ENABLED": "false",
            "ENVIRONMENT": "production",
            "FRONTEND_URL": "https://artifact.signupflow.invalid",
            "READINESS_FAILURE_ALERT_THRESHOLD": "3",
            "REDIS_URL": f"redis://:{redis_password}@redis:6379/0",
            "RELEASE_SHA": self.source_sha,
            "SECRET_KEY": self.secret_key,
            "SECURITY_CSP_ENABLED": "true",
            "SECURITY_HSTS_ENABLED": "true",
            "SECURITY_HSTS_MAX_AGE": "31536000",
            "SIGNUPFLOW_ALLOW_TEST_CLOCK": "false",
            "SIGNUPFLOW_LOAD_DOTENV": "false",
            "SMS_ENABLED": "false",
            "TESTING": "false",
        }

    def image_run_command(
        self,
        name: str,
        *,
        database_name: str | None = None,
        publish: bool = False,
        command: list[str] | None = None,
    ) -> list[str]:
        result = [
            "docker",
            "run",
            "--detach",
            "--name",
            name,
            "--label",
            f"{OWNERSHIP_LABEL}={self.run_id}",
            "--network",
            self.network_name,
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
        ]
        if publish:
            result.extend(["--publish", "127.0.0.1::8000"])
        for key, value in self.app_environment(database_name).items():
            result.extend(["--env", f"{key}={value}"])
        result.append(self.image_tag)
        if command:
            result.extend(command)
        return result


def parse_loopback_port(raw: str) -> int:
    """Parse Docker's published port and reject non-loopback exposure."""
    match = re.fullmatch(r"(?:127\.0\.0\.1|\[::1\]):([0-9]{1,5})", raw.strip())
    if not match:
        raise ValueError(f"Artifact app port is not loopback-only: {raw!r}")
    port = int(match.group(1))
    if not 1 <= port <= 65535:
        raise ValueError(f"Artifact app loopback port is invalid: {port}")
    return port


def verify_owned_container(target: ArtifactTarget, container_name: str, inspect_data: Any) -> None:
    """Refuse container lifecycle operations without exact ownership evidence."""
    if not isinstance(inspect_data, list) or len(inspect_data) != 1:
        raise RuntimeError("Cannot verify artifact container ownership")
    record = inspect_data[0]
    labels = record.get("Config", {}).get("Labels", {})
    if record.get("Name") != f"/{container_name}":
        raise RuntimeError("Artifact container name no longer matches")
    if labels.get(OWNERSHIP_LABEL) != target.run_id:
        raise RuntimeError("Artifact container ownership label no longer matches")


def verify_owned_network(target: ArtifactTarget, inspect_data: Any) -> None:
    """Refuse network lifecycle operations without exact ownership evidence."""
    if not isinstance(inspect_data, list) or len(inspect_data) != 1:
        raise RuntimeError("Cannot verify artifact network ownership")
    record = inspect_data[0]
    if record.get("Name") != target.network_name:
        raise RuntimeError("Artifact network name no longer matches")
    if record.get("Labels", {}).get(OWNERSHIP_LABEL) != target.run_id:
        raise RuntimeError("Artifact network ownership label no longer matches")


def _run(
    command: list[str],
    *,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if check and result.returncode != 0:
        operation = " ".join(command[:2])
        raise RuntimeError(f"{operation} failed with exit code {result.returncode}")
    return result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inspect_container(name: str) -> list[dict[str, Any]]:
    value = json.loads(_run(["docker", "inspect", name]).stdout)
    if not isinstance(value, list):
        raise RuntimeError("Docker container inspect returned an unexpected payload")
    return value


def _inspect_network(name: str) -> list[dict[str, Any]]:
    value = json.loads(_run(["docker", "network", "inspect", name]).stdout)
    if not isinstance(value, list):
        raise RuntimeError("Docker network inspect returned an unexpected payload")
    return value


def _tracked_source_sha() -> str:
    source_sha = _run(["git", "rev-parse", "HEAD"]).stdout.strip()
    if not SHA_PATTERN.fullmatch(source_sha):
        raise RuntimeError("Git HEAD is not a full lowercase commit SHA")
    dirty = _run(["git", "status", "--porcelain", "--untracked-files=no"]).stdout.strip()
    if dirty:
        raise RuntimeError("Commit tracked changes before validating a production artifact")
    return source_sha


def _wait_for_datastores(target: ArtifactTarget) -> dict[str, str]:
    deadline = time.monotonic() + 90
    postgres_version = "unavailable"
    redis_version = "unavailable"
    while time.monotonic() < deadline:
        postgres = _run(
            [
                "docker",
                "exec",
                target.postgres_name,
                "pg_isready",
                "--username",
                target.database_user,
                "--dbname",
                target.database_name,
            ],
            check=False,
        )
        redis = _run(
            [
                "docker",
                "exec",
                target.redis_name,
                "redis-cli",
                "--no-auth-warning",
                "-a",
                target.password,
                "ping",
            ],
            check=False,
        )
        if postgres.returncode == 0 and redis.returncode == 0 and redis.stdout.strip() == "PONG":
            postgres_version = _run(
                [
                    "docker",
                    "exec",
                    target.postgres_name,
                    "psql",
                    "--username",
                    target.database_user,
                    "--dbname",
                    target.database_name,
                    "--tuples-only",
                    "--no-align",
                    "--command",
                    "SHOW server_version;",
                ]
            ).stdout.strip()
            redis_version = _run(
                [
                    "docker",
                    "exec",
                    target.redis_name,
                    "redis-cli",
                    "--no-auth-warning",
                    "-a",
                    target.password,
                    "INFO",
                    "server",
                ]
            ).stdout
            version_line = next(
                (line for line in redis_version.splitlines() if line.startswith("redis_version:")),
                "redis_version:unavailable",
            )
            return {
                "postgres": postgres_version,
                "redis": version_line.split(":", 1)[1].strip(),
            }
        time.sleep(0.5)
    raise RuntimeError("Owned PostgreSQL and Redis containers did not become ready")


def _wait_for_http(port: int) -> dict[str, Any]:
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 90
    last_error = "no response"
    while time.monotonic() < deadline:
        try:
            with urlopen(f"{base_url}/ready", timeout=2) as response:
                payload = cast(dict[str, Any], json.loads(response.read()))
                if response.status == 200 and payload.get("status") == "ready":
                    return payload
        except (OSError, URLError, ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)
        time.sleep(0.5)
    raise RuntimeError(f"Artifact API did not become ready: {last_error}")


def _image_scan(target: ArtifactTarget, run_dir: Path) -> dict[str, Any]:
    scan_code = """
import importlib
import json
import os
import pathlib
import pwd
import shutil

required = [
    "/app/api/main.py",
    "/app/web/app.py",
    "/app/web/templates/auth/login.html",
    "/app/web/static/css/styles.css",
    "/app/alembic.ini",
    "/app/alembic/env.py",
]
forbidden_roots = ["/app/tests", "/app/docs", "/app/.git", "/app/.env"]
importlib.import_module("api.main")
importlib.import_module("web.app")
payload = {
    "required_paths": {path: pathlib.Path(path).exists() for path in required},
    "forbidden_paths": [path for path in forbidden_roots if pathlib.Path(path).exists()],
    "env_files": [str(path) for path in pathlib.Path("/app").rglob(".env*")],
    "runtime_user": pwd.getpwuid(os.geteuid()).pw_name,
    "runtime_uid": os.geteuid(),
    "app_root_writable": os.access("/app", os.W_OK),
    "build_tools": {name: shutil.which(name) for name in ("gcc", "make", "poetry")},
}
print(json.dumps(payload, sort_keys=True))
"""
    name = f"signupflow-artifact-scan-{target.run_id}"
    result = _run(
        [
            "docker",
            "run",
            "--rm",
            "--name",
            name,
            "--label",
            f"{OWNERSHIP_LABEL}={target.run_id}",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--entrypoint",
            "python",
            "--env",
            "SIGNUPFLOW_LOAD_DOTENV=false",
            "--env",
            "ENVIRONMENT=production",
            target.image_tag,
            "-c",
            scan_code,
        ],
        check=False,
    )
    (run_dir / "image-scan.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError("Artifact image scan failed; inspect image-scan.log")
    try:
        payload = cast(dict[str, Any], json.loads(result.stdout.splitlines()[-1]))
    except (IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError("Artifact image scan did not return JSON") from exc
    if not all(payload["required_paths"].values()):
        raise RuntimeError("Artifact image is missing required application files")
    if payload["forbidden_paths"] or payload["env_files"]:
        raise RuntimeError("Artifact image contains forbidden source or environment files")
    if payload["runtime_user"] != "signupflow" or payload["runtime_uid"] == 0:
        raise RuntimeError("Artifact image does not run as the signupflow user")
    if payload["app_root_writable"] or any(payload["build_tools"].values()):
        raise RuntimeError("Artifact image source is writable or includes build tools")
    return payload


def _sensitive_values(target: ArtifactTarget) -> list[bytes]:
    values = [target.password, target.secret_key]
    for name in (
        "OLLAMA_API_KEY",
        "SENDGRID_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "TWILIO_AUTH_TOKEN",
    ):
        value = os.environ.get(name, "")
        if len(value) >= 8:
            values.append(value)
    return [value.encode() for value in dict.fromkeys(values)]


def _scan_image_layers(target: ArtifactTarget, run_dir: Path, *, build_log: Path) -> dict[str, Any]:
    """Inspect every saved layer for env files and known in-process secret values."""
    archive_path = run_dir / "image-scan.tar"
    with archive_path.open("wb") as stream:
        saved = subprocess.run(
            ["docker", "image", "save", target.image_tag],
            cwd=ROOT,
            stdout=stream,
            stderr=subprocess.PIPE,
            check=False,
        )
    if saved.returncode != 0:
        raise RuntimeError("docker image save failed during layer inspection")

    candidates = _sensitive_values(target)
    env_files: list[str] = []
    secret_matches = 0
    layer_count = 0
    try:
        build_output = build_log.read_bytes()
        if any(value in build_output for value in candidates):
            raise RuntimeError("Artifact build output contains a sensitive value")
        with tarfile.open(archive_path, mode="r") as bundle:
            manifest_stream = bundle.extractfile("manifest.json")
            if manifest_stream is None:
                raise RuntimeError("Saved artifact image has no manifest")
            manifest = json.load(manifest_stream)
            if not isinstance(manifest, list) or len(manifest) != 1:
                raise RuntimeError("Saved artifact image manifest is unexpected")
            layers = manifest[0].get("Layers", [])
            layer_count = len(layers)
            for layer_name in layers:
                layer_stream = bundle.extractfile(layer_name)
                if layer_stream is None:
                    raise RuntimeError("Saved artifact image is missing a layer")
                with tarfile.open(fileobj=layer_stream, mode="r|*") as layer:
                    for member in layer:
                        normalized = member.name.removeprefix("./")
                        basename = Path(normalized).name
                        if normalized.startswith("app/") and (
                            basename.startswith(".env") or basename.startswith(".wh..env")
                        ):
                            env_files.append(normalized)
                        if not member.isfile() or member.size > 2 * 1024 * 1024:
                            continue
                        content_stream = layer.extractfile(member)
                        if content_stream is None:
                            continue
                        content = content_stream.read()
                        secret_matches += sum(value in content for value in candidates)
    finally:
        archive_path.unlink(missing_ok=True)
    if env_files or secret_matches:
        raise RuntimeError("Artifact image layers contain an env file or sensitive value")
    return {
        "layer_count": layer_count,
        "app_env_files": [],
        "sensitive_value_matches": 0,
        "build_output_sensitive_value_matches": 0,
    }


def _inspect_image(target: ArtifactTarget) -> dict[str, Any]:
    records = json.loads(_run(["docker", "image", "inspect", target.image_tag]).stdout)
    if not isinstance(records, list) or len(records) != 1:
        raise RuntimeError("Docker image inspect returned an unexpected payload")
    record = records[0]
    config = record.get("Config", {})
    labels = config.get("Labels", {})
    if labels.get("org.opencontainers.image.revision") != target.source_sha:
        raise RuntimeError("Artifact image revision label does not match Git HEAD")
    if config.get("User") != "signupflow":
        raise RuntimeError("Artifact image user is not signupflow")
    command = config.get("Cmd", [])
    if command.count("--workers") != 1 or command[-1] != "1":
        raise RuntimeError("Artifact image must start exactly one Uvicorn worker")

    history = _run(
        ["docker", "history", "--no-trunc", "--format", "{{json .CreatedBy}}", target.image_tag]
    ).stdout
    serialized_config = json.dumps(config, sort_keys=True)
    if SECRET_ASSIGNMENT_PATTERN.search(history + serialized_config):
        raise RuntimeError("Artifact image history or config contains a secret assignment")
    return {
        "image_id": record.get("Id"),
        "repo_digests": record.get("RepoDigests") or [],
        "revision": labels.get("org.opencontainers.image.revision"),
        "created": labels.get("org.opencontainers.image.created"),
        "runtime_user": config.get("User"),
        "entrypoint": config.get("Entrypoint"),
        "command": command,
        "rootfs_layers": record.get("RootFS", {}).get("Layers", []),
        "secret_assignment_scan": "passed",
    }


def _run_migration(target: ArtifactTarget, run_dir: Path) -> dict[str, Any]:
    command = target.image_run_command(
        target.migration_name,
        command=["python", "-m", "alembic", "upgrade", "head"],
    )
    command.remove("--detach")
    result = _run(command, check=False, timeout=120)
    (run_dir / "migration.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    inspect_data = _inspect_container(target.migration_name)
    verify_owned_container(target, target.migration_name, inspect_data)
    exit_code = inspect_data[0].get("State", {}).get("ExitCode")
    if result.returncode != 0 or exit_code != 0:
        raise RuntimeError("One-shot artifact migration failed")
    return {"container_exit_code": exit_code, "command": "python -m alembic upgrade head"}


def _probe_broker(target: ArtifactTarget, run_dir: Path) -> dict[str, Any]:
    probe_code = (
        "import os; from redis import Redis; "
        "assert Redis.from_url(os.environ['REDIS_URL']).ping(); print('broker-ping-ok')"
    )
    command = target.image_run_command(
        target.broker_probe_name,
        command=["python", "-c", probe_code],
    )
    command.remove("--detach")
    result = _run(command, check=False, timeout=45)
    (run_dir / "broker-probe.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    inspect_data = _inspect_container(target.broker_probe_name)
    verify_owned_container(target, target.broker_probe_name, inspect_data)
    exit_code = inspect_data[0].get("State", {}).get("ExitCode")
    if result.returncode != 0 or exit_code != 0 or "broker-ping-ok" not in result.stdout:
        raise RuntimeError("Built runtime image could not authenticate to the Redis broker")
    return {"container_exit_code": exit_code, "authenticated_ping": True}


def _prove_unmigrated_database_fails(target: ArtifactTarget, run_dir: Path) -> dict[str, Any]:
    _run(
        [
            "docker",
            "exec",
            target.postgres_name,
            "createdb",
            "--username",
            target.database_user,
            target.unmigrated_database_name,
        ]
    )
    _run(
        target.image_run_command(
            target.failed_app_name,
            database_name=target.unmigrated_database_name,
        )
    )
    inspect_data = _inspect_container(target.failed_app_name)
    verify_owned_container(target, target.failed_app_name, inspect_data)
    wait_result = _run(["docker", "wait", target.failed_app_name], check=False, timeout=45)
    logs = _run(["docker", "logs", target.failed_app_name], check=False)
    (run_dir / "unmigrated-app.log").write_text(logs.stdout + logs.stderr, encoding="utf-8")
    exit_code = int(wait_result.stdout.strip()) if wait_result.stdout.strip().isdigit() else 0
    if exit_code == 0 or "Database migrations are not current" not in logs.stdout + logs.stderr:
        raise RuntimeError("Application did not fail closed against an unmigrated database")
    table_name = _run(
        [
            "docker",
            "exec",
            target.postgres_name,
            "psql",
            "--username",
            target.database_user,
            "--dbname",
            target.unmigrated_database_name,
            "--tuples-only",
            "--no-align",
            "--command",
            "SELECT to_regclass('public.alembic_version');",
        ]
    ).stdout.strip()
    if table_name:
        raise RuntimeError("Application replica mutated the unmigrated database")
    return {"container_exit_code": exit_code, "alembic_version_table": None}


def _exercise_replicas(target: ArtifactTarget, run_dir: Path) -> dict[str, Any]:
    ports: list[int] = []
    for name in target.app_names:
        _run(target.image_run_command(name, publish=True))
        inspect_data = _inspect_container(name)
        verify_owned_container(target, name, inspect_data)
        if inspect_data[0].get("Mounts"):
            raise RuntimeError("Artifact API replica unexpectedly has mounted host content")
        port_output = _run(["docker", "port", name, "8000/tcp"]).stdout
        ports.append(parse_loopback_port(port_output))
    for port in ports:
        _wait_for_http(port)

    base_url = f"http://127.0.0.1:{ports[0]}"
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        login = client.get("/auth/login")
        static = client.get("/web/static/css/styles.css")
        health = client.get("/health")
        workflow = run_workflow(client, suffix=target.run_id)
    if login.status_code != 200 or static.status_code != 200 or health.status_code != 200:
        raise RuntimeError("Artifact browser, static, or health smoke failed")
    if health.headers.get("strict-transport-security") is None:
        raise RuntimeError("Artifact response is missing HSTS")
    if workflow.get("export_assignment_count", 0) < 1:
        raise RuntimeError("Artifact workflow did not export a published assignment")

    tls_rehearsal = _exercise_tls_rehearsal(
        target=target,
        backend_port=ports[0],
        run_dir=run_dir,
    )

    stopped_name = target.app_names[1]
    _run(["docker", "stop", "--timeout", "10", stopped_name])
    inspect_data = _inspect_container(stopped_name)
    verify_owned_container(target, stopped_name, inspect_data)
    exit_code = inspect_data[0].get("State", {}).get("ExitCode")
    logs = _run(["docker", "logs", stopped_name], check=False)
    (run_dir / "graceful-shutdown.log").write_text(logs.stdout + logs.stderr, encoding="utf-8")
    if exit_code != 0 or "Application shutdown complete" not in logs.stdout + logs.stderr:
        raise RuntimeError("Artifact replica did not shut down gracefully on SIGTERM")

    return {
        "replica_count": 2,
        "loopback_ports": ports,
        "browser_login_status": login.status_code,
        "static_asset_status": static.status_code,
        "health_status": health.status_code,
        "hsts": health.headers.get("strict-transport-security"),
        "tls_rehearsal": tls_rehearsal,
        "workflow": workflow,
        "graceful_shutdown_exit_code": exit_code,
    }


def _exercise_tls_rehearsal(
    *,
    target: ArtifactTarget,
    backend_port: int,
    run_dir: Path,
) -> dict[str, Any]:
    """Exercise browser-session controls through owned loopback HTTPS termination."""
    hostname = "artifact.signupflow.invalid"
    tls_dir = run_dir / "tls-rehearsal"
    material = TLSMaterial.create(tls_dir, hostname=hostname)
    try:
        with LoopbackTLSProxy(backend_port=backend_port, material=material) as proxy:
            negotiated = proxy.negotiated_protocol()
            with httpx.Client(
                base_url=proxy.url,
                verify=str(material.ca_certificate),
                headers={"Host": hostname},
                follow_redirects=False,
                timeout=30.0,
                trust_env=False,
            ) as client:
                login_form = client.get("/auth/login")
                if login_form.status_code != 200:
                    raise RuntimeError("TLS rehearsal could not load the browser login form")
                csrf_headers = login_form.headers.get_list("set-cookie")
                csrf_cookie = verify_cookie_security(
                    csrf_headers,
                    "signupflow_csrf",
                    http_only=False,
                )
                csrf_token = client.cookies.get("signupflow_csrf")
                if not csrf_token:
                    raise RuntimeError("TLS rehearsal did not retain the secure CSRF cookie")

                login = client.post(
                    "/auth/login",
                    data={
                        "email": f"manager-{target.run_id}@basketball.example",
                        "password": "LocalExample123!",
                        "csrf_token": csrf_token,
                    },
                    headers={"Origin": f"https://{hostname}"},
                )
                if login.status_code != 303 or login.headers.get("location") != "/a/dashboard":
                    raise RuntimeError("TLS rehearsal browser login did not reach the dashboard")
                session_cookie = verify_cookie_security(
                    login.headers.get_list("set-cookie"),
                    "signupflow_session",
                    http_only=True,
                )

                dashboard = client.get("/a/dashboard")
                if dashboard.status_code != 200:
                    raise RuntimeError("TLS rehearsal secure session was not usable over HTTPS")
                required_headers = {
                    "content-security-policy",
                    "strict-transport-security",
                    "x-content-type-options",
                    "x-frame-options",
                }
                if required_headers - set(dashboard.headers):
                    raise RuntimeError("TLS rehearsal dashboard is missing security headers")

                foreign_origin = client.post(
                    "/auth/logout",
                    data={"csrf_token": csrf_token},
                    headers={"Origin": "https://attacker.invalid"},
                )
                if foreign_origin.status_code != 403:
                    raise RuntimeError("TLS rehearsal foreign-origin write was not rejected")
                if client.get("/a/dashboard").status_code != 200:
                    raise RuntimeError("Rejected foreign-origin write changed the browser session")

                insecure = client.get(
                    f"http://127.0.0.1:{backend_port}/a/dashboard",
                    headers={"Host": hostname},
                )
                if insecure.status_code != 303 or insecure.headers.get("location") != "/auth/login":
                    raise RuntimeError("Secure session cookie was sent over plain HTTP")

            return {
                "scope": "owned self-signed loopback TLS termination",
                "hostname": hostname,
                "loopback_port": proxy.port,
                "ca_sha256": material.ca_sha256,
                "negotiated": negotiated,
                "login_status": login.status_code,
                "dashboard_status": dashboard.status_code,
                "foreign_origin_status": foreign_origin.status_code,
                "plain_http_session_status": insecure.status_code,
                "csrf_cookie": csrf_cookie,
                "session_cookie": session_cookie,
                "external_exposure": False,
            }
    finally:
        material.server_key.unlink(missing_ok=True)
        material.server_certificate.unlink(missing_ok=True)
        material.ca_certificate.unlink(missing_ok=True)
        tls_dir.rmdir()


def _cleanup_container(target: ArtifactTarget, name: str) -> None:
    inspect_result = _run(["docker", "inspect", name], check=False)
    if inspect_result.returncode != 0:
        return
    inspect_data = json.loads(inspect_result.stdout)
    verify_owned_container(target, name, inspect_data)
    if inspect_data[0].get("State", {}).get("Running"):
        _run(["docker", "stop", "--timeout", "5", name])
    _run(["docker", "container", "rm", name])


def _write_report(run_dir: Path, report: dict[str, Any]) -> Path:
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path


def main() -> int:
    """Run the opt-in local artifact acceptance and retain the tested image."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the owned local scope without invoking Docker",
    )
    args = parser.parse_args()
    if args.dry_run:
        print(
            "Would build the current committed source, then use one labeled private Docker "
            "network with disposable PostgreSQL, Redis, migration, and API containers."
        )
        return 0

    started_at = datetime.now(UTC)
    run_id = secrets.token_hex(4)
    run_dir = (
        ROOT
        / "test-artifacts"
        / "artifact-validation"
        / f"{started_at.strftime('%Y%m%dT%H%M%S.%fZ')}-{os.getpid()}-{run_id}"
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    created_containers: list[str] = []
    network_created = False
    target: ArtifactTarget | None = None
    report: dict[str, Any] = {
        "started_at": started_at.isoformat(),
        "outcome": "failed",
        "scope": "owned local Docker only",
        "external_providers": "disabled and not contacted",
        "staging": "not run; no target or operator authorization was supplied",
    }
    exit_code = 1

    try:
        source_sha = _tracked_source_sha()
        target = ArtifactTarget(
            run_id=run_id,
            source_sha=source_sha,
            password=secrets.token_urlsafe(24),
        )
        report["source_sha"] = source_sha
        _run(["docker", "info"])
        docker_versions = _run(
            [
                "docker",
                "version",
                "--format",
                "{{.Client.Version}}|{{.Server.Version}}",
            ]
        ).stdout.strip()
        docker_client, docker_server = docker_versions.split("|", 1)
        report["toolchain"] = {
            "docker_client": docker_client,
            "docker_server": docker_server,
            "python": sys.version.split()[0],
            "poetry": _run(["poetry", "--version"]).stdout.strip(),
        }
        report["source_inputs"] = {
            "dockerfile_sha256": _sha256(ROOT / "Dockerfile"),
            "poetry_lock_sha256": _sha256(ROOT / "poetry.lock"),
        }

        build_log = run_dir / "build.log"
        build_command = [
            "docker",
            "build",
            "--pull",
            "--label",
            f"{OWNERSHIP_LABEL}={target.run_id}",
            "--build-arg",
            f"VCS_REF={source_sha}",
            "--build-arg",
            f"BUILD_DATE={started_at.isoformat()}",
            "--tag",
            target.image_tag,
            ".",
        ]
        with build_log.open("w", encoding="utf-8") as stream:
            build = subprocess.run(
                build_command,
                cwd=ROOT,
                text=True,
                stdout=stream,
                stderr=subprocess.STDOUT,
                check=False,
            )
        if build.returncode != 0:
            raise RuntimeError(f"Artifact image build failed; inspect {build_log}")
        report["image"] = _inspect_image(target)
        report["image_scan"] = _image_scan(target, run_dir)
        report["layer_scan"] = _scan_image_layers(target, run_dir, build_log=build_log)

        _run(target.network_command())
        network_created = True
        verify_owned_network(target, _inspect_network(target.network_name))
        _run(target.postgres_command())
        created_containers.append(target.postgres_name)
        verify_owned_container(
            target, target.postgres_name, _inspect_container(target.postgres_name)
        )
        _run(target.redis_command())
        created_containers.append(target.redis_name)
        verify_owned_container(target, target.redis_name, _inspect_container(target.redis_name))
        report["datastores"] = _wait_for_datastores(target)
        report["datastores"]["published_ports"] = []

        created_containers.append(target.migration_name)
        report["migration"] = _run_migration(target, run_dir)
        created_containers.append(target.broker_probe_name)
        report["broker"] = _probe_broker(target, run_dir)
        created_containers.append(target.failed_app_name)
        report["unmigrated_startup"] = _prove_unmigrated_database_fails(target, run_dir)
        created_containers.extend(target.app_names)
        report["runtime"] = _exercise_replicas(target, run_dir)
        report["outcome"] = "passed"
        report["retained_image"] = target.image_tag
        exit_code = 0
    except (
        OSError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        RuntimeError,
        ValueError,
    ) as exc:
        report["error"] = str(exc)
        print(f"Production artifact validation failed: {exc}", file=sys.stderr)
    finally:
        cleanup_errors: list[str] = []
        if target is not None:
            for name in reversed(created_containers):
                try:
                    _cleanup_container(target, name)
                except (
                    OSError,
                    subprocess.CalledProcessError,
                    RuntimeError,
                    ValueError,
                ) as exc:
                    cleanup_errors.append(f"{name}: {exc}")
            if network_created:
                try:
                    verify_owned_network(target, _inspect_network(target.network_name))
                    _run(["docker", "network", "rm", target.network_name])
                except (
                    OSError,
                    subprocess.CalledProcessError,
                    RuntimeError,
                    ValueError,
                ) as exc:
                    cleanup_errors.append(f"{target.network_name}: {exc}")
        if cleanup_errors:
            report["cleanup_errors"] = cleanup_errors
            report["outcome"] = "failed"
            exit_code = 1
        report["finished_at"] = datetime.now(UTC).isoformat()
        report_path = _write_report(run_dir, report)
        print(f"Production artifact validation report: {report_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
