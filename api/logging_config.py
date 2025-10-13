"""Logging configuration for Rostio API."""

import logging
import sys
import os
from pathlib import Path

# Determine if debug mode is enabled
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
ENV = os.getenv("ENVIRONMENT", "production").lower()

# Auto-enable debug in development/staging environments
if ENV in ("development", "dev", "staging", "local"):
    DEBUG = True

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Set log level based on debug mode
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

# Create handlers
console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(LOGS_DIR / "rostio.log")
error_handler = logging.FileHandler(LOGS_DIR / "rostio_errors.log")
error_handler.setLevel(logging.ERROR)

# Configure logging format
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
if DEBUG:
    # More detailed format in debug mode
    log_format = '%(asctime)s - %(name)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=log_format,
    handlers=[console_handler, file_handler, error_handler]
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
