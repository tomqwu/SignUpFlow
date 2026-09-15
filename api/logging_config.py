"""Logging configuration for Rostio API."""

import json
import logging
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

# Determine if debug mode is enabled
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
ENV = os.getenv("ENVIRONMENT", "development").strip().lower()
RELEASE_SHA = os.getenv("RELEASE_SHA", "unknown").strip() or "unknown"

# Auto-enable debug in development/staging environments
if ENV in ("development", "dev", "staging", "local"):
    DEBUG = True

# Production containers are read-only and emit logs to stdout for the operator.
# Development keeps the existing convenience files.
LOGS_DIR = Path("logs")
FILE_LOGGING_ENABLED = ENV != "production"

# Set log level based on debug mode
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

# Create handlers
console_handler = logging.StreamHandler(sys.stdout)
handlers: list[logging.Handler] = [console_handler]
if FILE_LOGGING_ENABLED:
    LOGS_DIR.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(LOGS_DIR / "rostio.log")
    error_handler = logging.FileHandler(LOGS_DIR / "rostio_errors.log")
    error_handler.setLevel(logging.ERROR)
    handlers.extend((file_handler, error_handler))

from api.utils.request_context import request_id_var


class RequestIDFilter(logging.Filter):
    """Inject the current request ID (or '-') into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get() or "-"
        return True


_SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)\b(password|token|secret|api[_-]?key|authorization|cookie)\b" r"\s*[=:]\s*[^\s,;]+"
)
_CREDENTIAL_URL = re.compile(r"(?i)\b(postgresql(?:\+[a-z0-9_]+)?|postgres|redis)://[^@\s]+@")
_STRUCTURED_FIELDS = (
    "event",
    "error_type",
    "method",
    "path",
    "signal",
    "alert_state",
    "failure_count",
    "runbook",
    "error_reporting",
)


def redact_log_value(value: object) -> str:
    """Remove credential-shaped values from a bounded log field."""
    text = str(value)
    text = _SENSITIVE_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)
    return _CREDENTIAL_URL.sub(lambda match: f"{match.group(1)}://[REDACTED]@", text)


class ProductionJSONFormatter(logging.Formatter):
    """Emit a small structured production record without exception messages."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_log_value(record.getMessage()),
            "request_id": redact_log_value(getattr(record, "request_id", "-")),
            "environment": ENV,
            "release_sha": RELEASE_SHA,
        }
        for name in _STRUCTURED_FIELDS:
            if hasattr(record, name):
                value = getattr(record, name)
                payload[name] = (
                    value if isinstance(value, int | float | bool) else redact_log_value(value)
                )
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)


for _handler in handlers:
    _handler.addFilter(RequestIDFilter())

# Configure logging format
log_format = "%(asctime)s - %(name)s - [%(request_id)s] - %(levelname)s - %(message)s"
if DEBUG:
    # More detailed format in debug mode
    log_format = "%(asctime)s - %(name)s - [%(request_id)s] - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s"

# Configure logging
if ENV == "production":
    console_handler.setFormatter(ProductionJSONFormatter())
    logging.basicConfig(level=LOG_LEVEL, handlers=handlers)
else:
    logging.basicConfig(level=LOG_LEVEL, format=log_format, handlers=handlers)

# Get logger
logger = logging.getLogger("rostio")

# Log startup information
if DEBUG:
    logger.info("Debug mode enabled (ENVIRONMENT=%s)", ENV)
    logger.info("Log files: %s", LOGS_DIR.absolute())
else:
    logger.info("logging.configured", extra={"event": "logging.configured"})

# Reduce noise from other libraries
if DEBUG:
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
else:
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
logging.getLogger("sentry_sdk").setLevel(logging.WARNING)
