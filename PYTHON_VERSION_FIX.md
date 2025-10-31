# Python 3.14 Compatibility Issue Fix

## Problem
Python 3.14 is very new and has multiprocessing changes that aren't yet compatible with uvicorn's reload mechanism. This causes `make run` to fail with a multiprocessing error.

## Solution: Use Python 3.12 or 3.13

### Option 1: Install Python 3.12 with pyenv (Recommended)

```bash
# Install pyenv if not already installed
brew install pyenv

# Install Python 3.12
pyenv install 3.12.0

# Set Python 3.12 for this project
cd /Users/qiangwu/Documents/Projects/SignUpFlow
pyenv local 3.12.0

# Verify version
python --version  # Should show Python 3.12.0

# Reinstall dependencies with Poetry
poetry env remove python  # Remove existing environment
poetry install              # Reinstall with Python 3.12

# Now make run should work
make run
```

### Option 2: Use Docker (Recommended Alternative)

Docker uses Python 3.11 in the container, so it always works regardless of your local Python version:

```bash
# Start all services (PostgreSQL + Redis + API)
make up

# View logs
make logs

# Stop when done
make down
```

## Why This Happened

- **pyproject.toml** specified `python = "^3.11"` which allows Python 3.14
- Python 3.14 was released October 2024 and is very new
- uvicorn hasn't updated its multiprocessing code for Python 3.14 yet
- We've now restricted to `python = ">=3.11,<3.14"` to prevent this issue

## After Fix

Once you've installed Python 3.12 via pyenv and reinstalled dependencies, both workflows will work:

```bash
# Local development (now works)
make run

# Docker development (always worked)
make up
```

## Verification

```bash
# Check Python version
python --version

# Should be Python 3.12.x or 3.13.x (not 3.14.x)

# Check Poetry environment
poetry env info

# Should show Python 3.12 or 3.13 in the path
```
