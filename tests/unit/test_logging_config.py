"""Production logging must work with an immutable container filesystem."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_production_logging_is_stdout_only_and_creates_no_directory(tmp_path):
    script = """
import json
import logging
from api import logging_config

print(json.dumps({
    "file_logging": logging_config.FILE_LOGGING_ENABLED,
    "file_handlers": sum(
        isinstance(handler, logging.FileHandler)
        for handler in logging.getLogger().handlers
    ),
}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env={
            **os.environ,
            "ENVIRONMENT": "production",
            "PYTHONPATH": str(ROOT),
            "SIGNUPFLOW_LOAD_DOTENV": "false",
        },
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload == {"file_logging": False, "file_handlers": 0}
    assert not (tmp_path / "logs").exists()


def test_production_logs_are_structured_correlated_and_redacted(tmp_path):
    script = """
from api.logging_config import logger
from api.utils.request_context import request_id_var

token = request_id_var.set("request-abc")
try:
    logger.error(
        "request failed password=hunter2 "
        "postgresql://admin:database-secret@db.internal/signupflow",
        extra={"event": "request.failed", "path": "/example"},
    )
finally:
    request_id_var.reset(token)
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env={
            **os.environ,
            "ENVIRONMENT": "production",
            "PYTHONPATH": str(ROOT),
            "RELEASE_SHA": "abc123",
            "SIGNUPFLOW_LOAD_DOTENV": "false",
        },
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    records = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    record = next(item for item in records if item.get("event") == "request.failed")
    assert record["level"] == "ERROR"
    assert record["request_id"] == "request-abc"
    assert record["environment"] == "production"
    assert record["release_sha"] == "abc123"
    assert record["path"] == "/example"
    assert "hunter2" not in result.stdout
    assert "database-secret" not in result.stdout
    assert "[REDACTED]" in record["message"]
