# Backend Debug Mode

## Overview

The backend API now supports environment-based debug mode for conditional logging. Debug mode automatically enables in development environments and can be controlled via environment variables.

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

# Production mode (default):
export ENVIRONMENT=production
```

## Features

### Debug Mode Changes

When debug mode is enabled:

1. **Log Level**: Changes from `INFO` to `DEBUG`
2. **Log Format**: Includes file name and line number
   - Production: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
   - Debug: `%(asctime)s - %(name)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s`
3. **Library Logging**: uvicorn and FastAPI logs are visible
4. **Startup Message**: Shows debug status with emoji 🐛

### Example Log Output

**Production Mode:**
```
2025-10-13 10:00:00,000 - rostio - INFO - ✅ Production mode (ENVIRONMENT=production)
2025-10-13 10:00:00,000 - rostio - INFO - 🚀 Rostio API started
```

**Debug Mode:**
```
2025-10-13 10:00:00,000 - rostio - [logging_config.py:47] - INFO - 🐛 Debug mode ENABLED (ENVIRONMENT=development)
2025-10-13 10:00:00,000 - rostio - [logging_config.py:48] - INFO - 📍 Log files: /home/ubuntu/rostio/logs
2025-10-13 10:00:00,000 - rostio - [main.py:35] - INFO - 🚀 Rostio API started
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
    logger.debug(f"Processed {len(result)} items")  # Only logs in debug mode
except Exception as e:
    logger.error(f"Error processing data: {str(e)}", exc_info=True)  # Always logs with traceback
```

### Logging Levels

Use appropriate levels:

- `logger.debug()` - Detailed diagnostic info (only in debug mode)
- `logger.info()` - General informational messages
- `logger.warning()` - Warning messages for unexpected situations
- `logger.error()` - Error messages (always logged)
- `logger.critical()` - Critical errors requiring immediate attention

### Exception Logging

Use `exc_info=True` to include full traceback:

```python
try:
    dangerous_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
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
# Debug mode is OFF by default
poetry run uvicorn api.main:app

# Or explicitly set production
export ENVIRONMENT=production
poetry run uvicorn api.main:app
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

All logs are written to:
- `logs/rostio.log` - All logs (INFO and above)
- `logs/rostio_errors.log` - Only errors (ERROR and above)

## Files Refactored

- ✅ `/api/logging_config.py` - Enhanced with debug mode support
- ✅ `/api/routers/people.py` - Converted print() to logger.error()

## Files Remaining

Based on grep analysis:
- `/api/main.py` - 6 logger statements (already using logger)
- `/api/routers/solver.py` - 2 logger statements (already using logger)
- `/api/utils/datetime_utils.py` - 9 logger statements (already using logger)

Most files already use proper logging. Only print() statements need conversion.

## Benefits

1. **Environment-aware**: Automatically adjusts logging based on environment
2. **Zero configuration**: Works out of the box in development
3. **Production-safe**: No verbose logs in production
4. **Structured logs**: Consistent format with timestamps and levels
5. **File rotation**: Easy to implement log rotation on log files
6. **Exception tracking**: Full tracebacks with `exc_info=True`

## Best Practices

1. **Use logger, not print()**: Always use logger for all output
2. **Use debug() for verbose logs**: Detailed logs should use `logger.debug()`
3. **Include context**: Add relevant context to log messages
4. **Use f-strings**: Modern formatting is more readable
5. **Log exceptions properly**: Always use `exc_info=True` for errors

## Testing

Test that debug logs only appear in debug mode:

```bash
# Should show debug logs
export DEBUG=true
poetry run uvicorn api.main:app --reload

# Should NOT show debug logs
unset DEBUG
poetry run uvicorn api.main:app --reload
```
