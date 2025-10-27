# Environment Setup Guide

**Last Updated:** 2025-10-27
**Status:** Production-Ready YAML Profile System

This guide explains SignUpFlow's clean environment configuration system using YAML profiles and secret management.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Environment Profiles](#environment-profiles)
5. [Secret Management](#secret-management)
6. [Docker Configuration](#docker-configuration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Design Philosophy

SignUpFlow uses a **two-layer configuration system**:

1. **YAML Profiles** (`config/*.yaml`) - Define structure and defaults (committed to git)
2. **Environment Variables** (`.env`) - Provide secrets and overrides (NOT committed to git)

**Benefits:**
- ✅ Clean git workspace (no secret pollution)
- ✅ Separation of structure from secrets
- ✅ Environment-specific defaults
- ✅ Easy to audit and maintain
- ✅ Production-ready from day one

### File Structure

```
SignUpFlow/
├── config/                      # YAML profiles (committed to git)
│   ├── env.dev.yaml            # Development defaults
│   ├── env.test.yaml           # Testing defaults
│   └── env.prod.yaml           # Production defaults
│
├── .env                         # Secrets (NOT in git)
├── .env.example                 # Template (in git)
│
└── docker-compose.dev.yml      # Uses YAML profiles
```

---

## Quick Start

### 1. First-Time Setup

```bash
# 1. Copy template to .env
cp .env.example .env

# 2. Edit .env and fill in your secrets
nano .env  # or use your favorite editor

# 3. Start Docker services (automatically uses config/env.dev.yaml)
docker-compose -f docker-compose.dev.yml up

# 4. The app loads: config/env.dev.yaml + .env overrides
```

### 2. Minimal .env for Development

```bash
# Database
POSTGRES_PASSWORD=dev_strong_password_here
POSTGRES_USER=signupflow
POSTGRES_DB=signupflow_dev

# Redis
REDIS_PASSWORD=dev_redis_password_here

# Application
SECRET_KEY=your-secret-key-min-32-chars-here

# Optional: External Services (leave empty to disable)
MAILTRAP_SMTP_USER=
MAILTRAP_SMTP_PASSWORD=
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
```

### 3. Verify Setup

```bash
# Check environment is loaded correctly
docker-compose -f docker-compose.dev.yml exec api env | grep CONFIG_PROFILE
# Should output: CONFIG_PROFILE=dev

# Check database connection
docker-compose -f docker-compose.dev.yml exec api python -c "from api.database import engine; print(engine.url)"
```

---

## Architecture

### Configuration Loading Priority

```
1. config/env.{PROFILE}.yaml  ← Base defaults (dev/test/prod)
2. .env file                  ← Override defaults with secrets
3. docker-compose environment ← Runtime overrides (rare)
```

**Example:**

```yaml
# config/env.dev.yaml
database:
  host: db
  port: 5432
  name: signupflow_dev
  user: signupflow
  # password: FROM .env (POSTGRES_PASSWORD)  ← Comment indicates secret source
```

```bash
# .env
POSTGRES_PASSWORD=actual_secret_password_here
```

**Result:** App uses `config/env.dev.yaml` structure with `POSTGRES_PASSWORD` from `.env`

### How the App Reads Config

```python
# Pseudocode (actual implementation in api/core/config.py)
import os
import yaml

# 1. Load YAML profile
profile = os.getenv('CONFIG_PROFILE', 'dev')  # dev/test/prod
with open(f'config/env.{profile}.yaml') as f:
    config = yaml.safe_load(f)

# 2. Override with .env values
config['database']['password'] = os.getenv('POSTGRES_PASSWORD')
config['auth']['secret_key'] = os.getenv('SECRET_KEY')
# ... etc for all secrets

# 3. Use merged configuration
DATABASE_URL = f"postgresql://{config['database']['user']}:{config['database']['password']}@..."
```

---

## Environment Profiles

### Development Profile (`config/env.dev.yaml`)

**Purpose:** Local development with hot-reload and debugging.

**Key Settings:**
- `debug: true` - Enable debug mode
- `reload: true` - Hot-reload on code changes
- `log_level: DEBUG` - Verbose logging
- `workers: 1` - Single worker (easier debugging)
- `rate_limiting: relaxed` - No annoying rate limits
- External services: `enabled: false` (use mocks)

**Use Case:** Daily development work

### Testing Profile (`config/env.test.yaml`)

**Purpose:** Automated testing in Docker with Playwright.

**Key Settings:**
- `debug: true` - Enable for test failure debugging
- `reload: false` - No hot-reload during tests
- `log_level: INFO` - Less verbose
- `rate_limiting: disabled` - Fast test execution
- `session_ttl_hours: 1` - Shorter TTL for tests
- External services: `enabled: false` (isolated tests)

**Use Case:** `make test-docker`, CI/CD pipelines

### Production Profile (`config/env.prod.yaml`)

**Purpose:** Production deployment with security and performance.

**Key Settings:**
- `debug: false` - **NEVER enable debug in production**
- `reload: false` - No hot-reload
- `log_level: WARNING` - Only warnings and errors
- `workers: 4` - Multiple workers (CPU cores × 2)
- `rate_limiting: strict` - Prevent abuse
- External services: `enabled: true` (all required)
- SSL/TLS: `required` - HTTPS only
- Monitoring: `sentry.enabled: true` - Error tracking

**Use Case:** Production deployment

---

## Secret Management

### What Goes in .env (Secrets)

**ALWAYS in .env, NEVER in YAML:**
- Database passwords
- Redis passwords
- JWT secret keys
- API keys (Stripe, SendGrid, Twilio)
- Encryption keys (TOTP)
- OAuth credentials
- Webhook secrets

### What Goes in YAML (Structure)

**ALWAYS in YAML, safe to commit:**
- Default values (timeouts, limits, TTLs)
- Feature flags (enable/disable features)
- Hostnames (db, redis service names)
- Port numbers (5432, 6379)
- Algorithm choices (HS256, bcrypt)
- Configuration structure

### .env Template (.env.example)

The `.env.example` file is the **source of truth** for required secrets:

```bash
# =============================================================================
# SignUpFlow Environment Variables Template
# =============================================================================
# Copy this file to .env and fill in your actual values
# NEVER commit .env to git (it contains secrets!)
#
# Usage:
#   cp .env.example .env
#   nano .env  # Fill in your secrets
#   docker-compose up
#
# Structure defined in: config/env.{dev|test|prod}.yaml
# =============================================================================

# Database Configuration
# ------------------------------------------------
POSTGRES_DB=signupflow_dev
POSTGRES_USER=signupflow
POSTGRES_PASSWORD=changeme_use_strong_password_here

# Redis Configuration
# ------------------------------------------------
REDIS_PASSWORD=changeme_use_strong_password_here

# Application Secrets
# ------------------------------------------------
SECRET_KEY=changeme_min_32_chars_for_jwt_signing

# ... (see .env.example for complete list)
```

### Security Best Practices

1. **Never commit .env files**
   - `.gitignore` already excludes all `.env*` files except `.env.example`

2. **Use strong secrets in production**
   ```bash
   # Generate strong random key (32 chars minimum)
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Rotate secrets regularly**
   - Database passwords: Every 90 days
   - JWT secret keys: Every 180 days (invalidates all tokens!)
   - API keys: When service provider recommends

4. **Use different secrets per environment**
   - Dev: Weak passwords OK (e.g., "dev_password")
   - Test: Weak passwords OK (e.g., "test_password")
   - Prod: **MUST** use strong random secrets

5. **Secure .env file permissions**
   ```bash
   chmod 600 .env  # Only owner can read/write
   ```

---

## Docker Configuration

### docker-compose.dev.yml

```yaml
services:
  api:
    # Load secrets from .env
    env_file:
      - .env

    # Tell app which YAML profile to use
    environment:
      CONFIG_PROFILE: dev

      # Runtime overrides (secrets from .env)
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0

    # Mount YAML configs (read-only for security)
    volumes:
      - ./config:/app/config:ro
```

### Switching Profiles

**Development (default):**
```bash
docker-compose -f docker-compose.dev.yml up
# Uses config/env.dev.yaml
```

**Testing:**
```bash
docker-compose -f docker-compose.dev.yml exec api \
  env CONFIG_PROFILE=test pytest tests/e2e/ -v
# Uses config/env.test.yaml
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up
# Uses config/env.prod.yaml
```

---

## Best Practices

### DO ✅

1. **Commit YAML profiles to git**
   ```bash
   git add config/env.dev.yaml config/env.test.yaml config/env.prod.yaml
   git commit -m "Add environment configuration profiles"
   ```

2. **Keep .env.example updated**
   ```bash
   # When adding new secret, add to .env.example with placeholder
   echo "NEW_API_KEY=your_new_api_key_here" >> .env.example
   ```

3. **Document secrets in YAML with comments**
   ```yaml
   auth:
     # secret_key: FROM .env (SECRET_KEY) - min 32 chars for JWT signing
   ```

4. **Use environment-specific defaults**
   ```yaml
   # config/env.dev.yaml
   rate_limiting:
     enabled: true
     login_max: 100  # Relaxed for development

   # config/env.prod.yaml
   rate_limiting:
     enabled: true
     login_max: 5  # Strict for production
   ```

### DON'T ❌

1. **Never commit secrets to git**
   ```bash
   # WRONG - contains secrets!
   git add .env
   ```

2. **Never hardcode secrets in YAML**
   ```yaml
   # WRONG - secret in git!
   auth:
     secret_key: "actual-secret-key-here"  # ❌ NEVER DO THIS

   # RIGHT - reference .env
   auth:
     # secret_key: FROM .env (SECRET_KEY)  # ✅ CORRECT
   ```

3. **Never mix secrets and structure**
   ```bash
   # WRONG - secrets mixed with config
   export SECRET_KEY=abc123
   export RATE_LIMIT_MAX=100

   # RIGHT - secrets in .env, config in YAML
   # .env: SECRET_KEY=abc123
   # config/env.dev.yaml: rate_limiting.max: 100
   ```

---

## Troubleshooting

### Problem: App can't find config file

**Error:**
```
FileNotFoundError: config/env.dev.yaml not found
```

**Solution:**
```bash
# Check config directory is mounted in docker-compose.yml
docker-compose -f docker-compose.dev.yml exec api ls /app/config

# If missing, verify volumes section:
# volumes:
#   - ./config:/app/config:ro
```

### Problem: Secrets not being loaded

**Error:**
```
KeyError: 'POSTGRES_PASSWORD'
```

**Solution:**
```bash
# 1. Check .env file exists
ls -la .env

# 2. Check .env is loaded in docker-compose.yml
# env_file:
#   - .env

# 3. Verify secret is in .env
grep POSTGRES_PASSWORD .env

# 4. Restart containers to reload .env
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up
```

### Problem: Wrong profile loaded

**Error:**
```
Using production settings in development
```

**Solution:**
```bash
# Check CONFIG_PROFILE environment variable
docker-compose -f docker-compose.dev.yml exec api env | grep CONFIG_PROFILE

# Should be: CONFIG_PROFILE=dev
# If wrong, update docker-compose.dev.yml:
# environment:
#   CONFIG_PROFILE: dev
```

### Problem: Git trying to commit .env

**Error:**
```
warning: .env is not tracked by git
```

**Solution:**
```bash
# Verify .gitignore excludes .env
grep "^\.env$" .gitignore

# If missing, add to .gitignore:
echo ".env" >> .gitignore

# Remove .env if accidentally staged
git rm --cached .env
```

---

## Migration from Old System

### Old System (Messy)

```yaml
# docker-compose.yml - 50+ environment variables!
environment:
  SECRET_KEY: ${SECRET_KEY}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  REDIS_PASSWORD: ${REDIS_PASSWORD}
  MAILTRAP_SMTP_USER: ${MAILTRAP_SMTP_USER}
  MAILTRAP_SMTP_PASSWORD: ${MAILTRAP_SMTP_PASSWORD}
  # ... 45 more lines
```

### New System (Clean)

```yaml
# docker-compose.yml - Just 3 lines!
env_file:
  - .env
environment:
  CONFIG_PROFILE: dev
volumes:
  - ./config:/app/config:ro
```

### Migration Steps

1. **Create YAML profiles** (already done)
   - `config/env.dev.yaml`
   - `config/env.test.yaml`
   - `config/env.prod.yaml`

2. **Update docker-compose.yml** (already done)
   - Add `env_file: - .env`
   - Add `CONFIG_PROFILE: dev`
   - Mount `./config:/app/config:ro`

3. **Move secrets to .env**
   ```bash
   # Extract secrets from docker-compose.yml
   # Put them in .env
   ```

4. **Update app code to read YAML**
   ```python
   # api/core/config.py
   import yaml
   import os

   profile = os.getenv('CONFIG_PROFILE', 'dev')
   with open(f'config/env.{profile}.yaml') as f:
       config = yaml.safe_load(f)
   ```

5. **Test and verify**
   ```bash
   docker-compose -f docker-compose.dev.yml up
   # Verify app starts correctly
   ```

---

## Summary

**What You Need to Know:**

1. **YAML profiles define structure** (`config/*.yaml`)
   - Safe to commit to git
   - Environment-specific defaults
   - Documents configuration structure

2. **`.env` provides secrets** (NOT committed)
   - Copy from `.env.example`
   - Fill in actual secrets
   - Different per environment

3. **Docker mounts config and loads .env**
   - `CONFIG_PROFILE=dev` selects profile
   - App merges YAML + .env
   - Clean, maintainable, secure

**Quick Commands:**

```bash
# Setup new environment
cp .env.example .env
nano .env  # Fill secrets
docker-compose up

# Switch profiles
CONFIG_PROFILE=test docker-compose up

# Verify configuration
docker-compose exec api env | grep CONFIG_PROFILE
```

---

**Last Updated:** 2025-10-27
**Author:** Claude Code
**Related Docs:**
- [DOCKER_DEVELOPMENT.md](DOCKER_DEVELOPMENT.md)
- [DOCKER_QUICK_START.md](../DOCKER_QUICK_START.md)
- [QUICK_START.md](QUICK_START.md)
