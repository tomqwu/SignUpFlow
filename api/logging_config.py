"""Logging configuration for Rostio API."""

import logging
import os
import sys
from pathlib import Path

# Determine if debug mode is enabled
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
ENV = os.getenv("ENVIRONMENT", "development").strip().lower()

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


for _handler in handlers:
    _handler.addFilter(RequestIDFilter())

# Configure logging format
log_format = "%(asctime)s - %(name)s - [%(request_id)s] - %(levelname)s - %(message)s"
if DEBUG:
    # More detailed format in debug mode
    log_format = "%(asctime)s - %(name)s - [%(request_id)s] - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s"

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL, format=log_format, handlers=handlers
)

# Get logger
logger = logging.getLogger("rostio")

# Log startup information
if DEBUG:
    logger.info(f"🐛 Debug mode ENABLED (ENVIRONMENT={ENV})")
    logger.info(f"📍 Log files: {LOGS_DIR.absolute()}")
else:
    logger.info(f"✅ Production mode (ENVIRONMENT={ENV})")

# Reduce noise from other libraries
if DEBUG:
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
else:
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
