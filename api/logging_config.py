"""Logging configuration for Rostio API."""

import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # Console handler
        logging.StreamHandler(sys.stdout),
        # File handler
        logging.FileHandler(LOGS_DIR / "rostio.log"),
        # Error file handler
        logging.FileHandler(LOGS_DIR / "rostio_errors.log", level=logging.ERROR),
    ]
)

# Get logger
logger = logging.getLogger("rostio")

# Reduce noise from other libraries
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
