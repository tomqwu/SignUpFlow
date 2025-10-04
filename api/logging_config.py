"""Logging configuration for Rostio API."""

import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Create handlers
console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(LOGS_DIR / "rostio.log")
error_handler = logging.FileHandler(LOGS_DIR / "rostio_errors.log")
error_handler.setLevel(logging.ERROR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[console_handler, file_handler, error_handler]
)

# Get logger
logger = logging.getLogger("rostio")

# Reduce noise from other libraries
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
