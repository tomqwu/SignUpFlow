# Backend Debug Mode

## Overview

The backend uses readable development logs and structured production logs. Debug
mode automatically enables in development-like environments. Production emits
JSON to stdout, adds request/environment/release correlation, and creates no log
files inside the read-only image.

## Environment Variables

### `DEBUG`
Controls debug logging explicitly:
```bash
# Enable debug mode
export DEBUG=true
# Or
export DEBUG=1
# Or
export DEBUG=yes

# Disable debug mode (default)
export DEBUG=false
```

### `ENVIRONMENT`
Auto-enables debug mode for certain environments:
```bash
# These automatically enable debug mode:
export ENVIRONMENT=development
export ENVIRONMENT=dev
export ENVIRONMENT=staging
export ENVIRONMENT=local

# Production mode (must be selected explicitly):
export ENVIRONMENT=production
```

## Features

### Debug Mode Changes

When debug mode is enabled:

1. **Log Level**: Changes from `INFO` to `DEBUG`
2. **Log Format**: Development includes request ID, file name, and line number.
   Production emits bounded JSON fields including timestamp, level, logger,
   message, request ID, environment, and release SHA.
3. **Library Logging**: uvicorn and FastAPI logs are visible
4. **Startup Message**: Records the selected logging mode.

### Example Log Output

**Production Mode:**
```json
{"environment":"production","event":"logging.configured","level":"INFO","logger":"rostio","message":"logging.configured","release_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","request_id":"-","timestamp":"..."}
{"environment":"production","event":"application.started","level":"INFO","logger":"rostio","message":"application.started","release_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","request_id":"-","timestamp":"..."}
```

**Debug Mode:**
```
2025-10-13 10:00:00,000 - rostio - [-] - [logging_config.py:95] - INFO - Debug mode enabled (ENVIRONMENT=development)
2025-10-13 10:00:00,000 - rostio - [-] - [logging_config.py:96] - INFO - Log files: /workspace/logs
```

## Usage in Code

### Importing Logger

```python
from api.logging_config import logger

# Use logger instead of print()
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

### Example: Converting Print Statements

**Before:**
```python
try:
    result = process_data(data)
    print(f"Processed {len(result)} items")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    print(traceback.format_exc())
```

**After:**
```python
try:
    result = process_data(data)
    logger.debug("Processed %s items", len(result))
except Exception:
    logger.error("data.processing_failed", extra={"event": "data.processing_failed"})
    raise
```

### Logging Levels

Use appropriate levels:

- `logger.debug()` - Detailed diagnostic info (only in debug mode)
- `logger.info()` - General informational messages
- `logger.warning()` - Warning messages for unexpected situations
- `logger.error()` - Error messages (always logged)
- `logger.critical()` - Critical errors requiring immediate attention

### Exception Logging

Do not interpolate exception messages, credentials, customer messages, query
strings, or request bodies into production logs. Let the application middleware
capture an unhandled exception through the optional configured reporter and emit
one sanitized correlated event:

```python
try:
    dangerous_operation()
except Exception:
    logger.error("operation.failed", extra={"event": "operation.failed"})
    raise
```

## Running with Debug Mode

### Development (Local)
```bash
# Enable debug mode
export DEBUG=true
poetry run uvicorn api.main:app --reload

# Or set environment
export ENVIRONMENT=development
poetry run uvicorn api.main:app --reload
```

### Production
```bash
# Supply every required fail-closed setting, including the exact commit.
export ENVIRONMENT=production
export RELEASE_SHA=$(git rev-parse HEAD)
# See PRODUCTION_CONFIGURATION.md before startup.
```

### Docker
```yaml
# docker-compose.yml
services:
  api:
    environment:
      - DEBUG=true
      - ENVIRONMENT=development
```

## Log Files

Production writes logs to stdout only so the non-root read-only image can send
them to the deployment log collector. It does not create `logs/` or file handlers.

Development also writes:
- `logs/rostio.log` - All logs (INFO and above)
- `logs/rostio_errors.log` - Only errors (ERROR and above)

## Current Boundaries

- `api/logging_config.py` owns development text/file and production JSON/stdout behavior.
- `api/main.py` owns startup, shutdown, readiness, and unhandled-request events.
- `api/observability.py` initializes optional Sentry reporting with PII and tracing off.
- `api/operational_alerts.py` emits bounded local trigger/recovery state.

Local structured signals are not external alert-delivery evidence. See #267 and
the operations runbook for the remaining recipient, retention, and staging work.

## Benefits

1. **Environment-aware**: Automatically adjusts logging based on environment
2. **Zero configuration**: Works out of the box in development
3. **Production-safe**: No verbose logs or runtime file writes in production
4. **Structured logs**: Production records use bounded machine-readable fields
5. **Correlation**: Request ID, environment, and release SHA travel together
6. **Optional error reporting**: A configured Sentry client receives unhandled exceptions

## Best Practices

1. **Use logger, not print()**: Always use logger for all output
2. **Use debug() for verbose logs**: Detailed logs should use `logger.debug()`
3. **Include bounded context**: Use fixed event names and known-safe identifiers
4. **Use parameterized messages**: Avoid formatting secrets or customer content into logs
5. **Sanitize errors**: Log the error type and let the configured reporter capture details

## Testing

Run the maintained logging and observability contracts:

```bash
poetry run pytest tests/unit/test_logging_config.py \
  tests/unit/test_observability.py tests/unit/test_operational_alerts.py -q
```

These tests inject fake reporting and alert sinks. They do not contact Sentry or
prove delivery to a real operator.
