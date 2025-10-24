# Docker Development Guide

**SignUpFlow Development with Docker Compose**

This guide explains how to use Docker Compose for local SignUpFlow development. Docker Compose provides a consistent development environment with PostgreSQL, Redis, and the API running in containers with hot-reload support.

---

## Table of Contents

1. [Why Docker for Development?](#why-docker-for-development)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Development Workflow](#development-workflow)
5. [Common Commands](#common-commands)
6. [Architecture](#architecture)
7. [Configuration](#configuration)
8. [Database Operations](#database-operations)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)
11. [VS Code Integration](#vs-code-integration)

---

## Why Docker for Development?

### Benefits

✅ **Consistent Environment** - Everyone on the team has the same PostgreSQL, Redis, and Python versions
✅ **No Local Installation** - No need to install PostgreSQL, Redis, or Python dependencies locally
✅ **Isolated Dependencies** - No conflicts with other projects on your machine
✅ **Production Parity** - Development environment matches production infrastructure
✅ **Quick Setup** - One command to start everything: `make up`
✅ **Easy Cleanup** - One command to remove everything: `make down`

### When to Use Docker

**Use Docker Development When:**
- You want to match production environment (PostgreSQL + Redis)
- You're testing billing, rate limiting, or caching features (requires Redis)
- You're working on database migrations
- You want a clean, isolated environment
- You're on a team and want consistent environments

**Use Local Development When:**
- You're doing rapid frontend development (faster hot-reload without Docker)
- You're writing unit tests (don't need full stack)
- You have limited disk space (Docker images ~1GB)
- You're working offline (Docker requires internet for initial setup)

---

## Prerequisites

### Required

- **Docker Desktop** (includes Docker Compose)
  - macOS: [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
  - Windows: [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
  - Linux: Install Docker Engine + Docker Compose separately

- **Make** (for convenient commands)
  - macOS/Linux: Pre-installed
  - Windows: Install via Chocolatey: `choco install make`

### Verify Installation

```bash
# Check Docker
docker --version
# Should output: Docker version 24.x.x or higher

# Check Docker Compose
docker-compose --version
# Should output: Docker Compose version 2.x.x or higher

# Check Make
make --version
# Should output: GNU Make 3.x or higher
```

---

## Quick Start

### 1. Start Development Environment

```bash
# Start all services (PostgreSQL + Redis + API)
make up
```

This command will:
1. Start PostgreSQL on `localhost:5433` (to avoid conflicts with local PostgreSQL)
2. Start Redis on `localhost:6380` (to avoid conflicts with local Redis)
3. Build and start the API on `localhost:8000`
4. Run in detached mode (background)

**Expected Output:**
```
🐳 Starting SignUpFlow development environment...
[+] Running 3/3
 ✔ Container signupflow-dev-db      Started
 ✔ Container signupflow-dev-redis   Started
 ✔ Container signupflow-dev-api     Started

✅ Services started!
   API:        http://localhost:8000
   PostgreSQL: localhost:5433 (user: signupflow, db: signupflow_dev)
   Redis:      localhost:6380

View logs:     make logs
Stop services: make down
```

### 2. Run Database Migrations

```bash
# Run migrations in Docker container
make migrate-docker
```

### 3. Verify It's Working

```bash
# Check service status
make ps

# View API logs
make logs-api

# Open the app in browser
open http://localhost:8000
```

**Default login credentials:**
- Email: `jane@test.com`
- Password: `password`

### 4. Stop Services

```bash
# Stop all services
make down
```

---

## Development Workflow

### Typical Development Day

```bash
# Morning: Start services
make up

# View logs while developing
make logs-api

# Make code changes → Hot-reload automatically updates

# Run tests
make test-docker

# Check database
make db-shell

# Evening: Stop services
make down
```

### Hot-Reload in Action

The API container has your source code mounted as volumes:

```yaml
volumes:
  - ./api:/app/api               # Backend code
  - ./frontend:/app/frontend     # Frontend code
  - ./locales:/app/locales       # Translations
  - ./tests:/app/tests           # Tests
```

**What this means:**
- Edit files in `api/` → API reloads automatically (2-3 seconds)
- Edit files in `frontend/` → Browser refresh shows changes
- Edit files in `locales/` → Translations update immediately
- No need to rebuild containers for code changes!

### When to Rebuild

You **DO** need to rebuild containers when:

1. **Dependencies change** (e.g., adding a new Python package to `pyproject.toml`)
   ```bash
   make rebuild
   ```

2. **Environment variables change** (e.g., updating `.env`)
   ```bash
   make restart-api
   ```

3. **Dockerfile changes**
   ```bash
   make rebuild
   ```

---

## Common Commands

### Starting/Stopping

```bash
# Start all services
make up

# Stop all services (keeps data)
make down

# Stop and remove volumes (deletes database data)
make clean-docker

# Rebuild images and restart
make rebuild
```

### Viewing Logs

```bash
# All services (follows logs in real-time)
make logs

# API only
make logs-api

# Database only
make logs-db

# Redis only
make logs-redis

# Exit logs: Ctrl+C
```

### Interactive Shells

```bash
# Bash shell in API container
make shell
# Now you can run: python, pytest, alembic, etc.

# PostgreSQL shell
make db-shell
# Now you can run SQL: SELECT * FROM people;

# Redis CLI
make redis-shell
# Now you can run: KEYS *, GET key, etc.
```

### Database Operations

```bash
# Run migrations
make migrate-docker

# Open PostgreSQL shell
make db-shell

# Backup database (from within db-shell)
pg_dump -U signupflow signupflow_dev > /backups/backup_$(date +%Y%m%d).sql

# Restore database (from within db-shell)
psql -U signupflow signupflow_dev < /backups/backup_20250101.sql
```

### Testing

```bash
# Run all tests in Docker
make test-docker

# Run specific test file
docker-compose -f docker-compose.dev.yml exec api pytest tests/unit/test_auth.py -v

# Run with coverage
docker-compose -f docker-compose.dev.yml exec api pytest tests/ --cov=api --cov-report=html
```

### Service Management

```bash
# Show running services
make ps

# Restart API only (fast)
make restart-api

# Restart all services
make down && make up
```

### Cleanup

```bash
# Stop services (keeps volumes/data)
make down

# Stop and remove volumes (deletes data)
make clean-docker

# Remove everything including images
make clean-docker-all
```

---

## Architecture

### Services

```
┌─────────────────────────────────────────────────────┐
│                  Host Machine                        │
│                                                       │
│  ┌─────────────────────────────────────────────┐   │
│  │  Browser → http://localhost:8000             │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │                                │
│  ┌──────────────────▼──────────────────────────┐   │
│  │  signupflow-dev-api (FastAPI)               │   │
│  │  Port: 8000 → 8000                          │   │
│  │  Hot-reload: ✅ (code volumes mounted)       │   │
│  │  Depends on: db, redis                      │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │                                │
│  ┌──────────────────▼──────────────────────────┐   │
│  │  signupflow-dev-db (PostgreSQL 16)          │   │
│  │  Port: 5433 → 5432                          │   │
│  │  Volume: postgres_dev_data                  │   │
│  │  User: signupflow                           │   │
│  │  Database: signupflow_dev                   │   │
│  └─────────────────────────────────────────────┘   │
│                                                       │
│  ┌─────────────────────────────────────────────┐   │
│  │  signupflow-dev-redis (Redis 7)             │   │
│  │  Port: 6380 → 6379                          │   │
│  │  Volume: redis_dev_data                     │   │
│  │  Used for: rate limiting, caching           │   │
│  └─────────────────────────────────────────────┘   │
│                                                       │
│  Network: signupflow-dev-network                     │
└─────────────────────────────────────────────────────┘
```

### Port Mappings

| Service | Container Port | Host Port | Reason |
|---------|---------------|-----------|--------|
| API | 8000 | 8000 | Standard HTTP |
| PostgreSQL | 5432 | **5433** | Avoid conflict with local PostgreSQL |
| Redis | 6379 | **6380** | Avoid conflict with local Redis |

### Volume Mounts

**Code Volumes (Hot-Reload):**
```yaml
- ./api:/app/api               # Backend Python code
- ./frontend:/app/frontend     # Frontend HTML/JS/CSS
- ./locales:/app/locales       # i18n translations
- ./alembic:/app/alembic       # Database migrations
- ./tests:/app/tests           # Test suites
```

**Data Volumes (Persistent):**
```yaml
- postgres_dev_data:/var/lib/postgresql/data  # Database data
- redis_dev_data:/data                        # Redis data
- ./logs:/app/logs                            # Application logs
- ./data:/app/data                            # Application data
```

---

## Configuration

### Environment Variables

Configuration is loaded from `.env` file (create from `.env.example`):

```bash
# Copy example file
cp .env.example .env

# Edit for development
nano .env
```

**Key Variables for Docker Development:**

```bash
# Database (automatic for Docker)
DATABASE_URL=postgresql://signupflow:dev_password@db:5432/signupflow_dev

# Redis (automatic for Docker)
REDIS_URL=redis://:dev_redis_password@redis:6379/0

# Application
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Email (Mailtrap for development)
MAILTRAP_SMTP_USER=your_username
MAILTRAP_SMTP_PASSWORD=your_password
EMAIL_ENABLED=true

# Stripe (test mode)
STRIPE_SECRET_KEY=sk_test_your_test_key
STRIPE_TEST_MODE=true
```

**Note:** The `docker-compose.dev.yml` sets sensible defaults, so you only need to configure external services (Mailtrap, Stripe, Twilio).

### Dockerfile.dev vs Dockerfile

| Feature | Dockerfile.dev (Development) | Dockerfile (Production) |
|---------|------------------------------|-------------------------|
| Build stages | Single-stage | Multi-stage (optimized) |
| Dependencies | All (including dev) | Production only |
| User | root | Non-root (signupflow) |
| Hot-reload | Yes (via volume mounts) | No |
| Image size | ~800MB | ~300MB |
| Build time | ~2 minutes | ~4 minutes |
| Security | Relaxed | Hardened |

---

## Database Operations

### Accessing PostgreSQL

**From host machine:**
```bash
# Using make command
make db-shell

# Using psql directly (if installed locally)
psql -h localhost -p 5433 -U signupflow -d signupflow_dev

# Using Docker directly
docker exec -it signupflow-dev-db psql -U signupflow -d signupflow_dev
```

**Common SQL Commands:**
```sql
-- List all tables
\dt

-- Describe table structure
\d people

-- Query users
SELECT id, email, name, roles FROM people;

-- Count events
SELECT COUNT(*) FROM events;

-- Exit
\q
```

### Running Migrations

```bash
# Run all pending migrations
make migrate-docker

# Create new migration
docker-compose -f docker-compose.dev.yml exec api alembic revision --autogenerate -m "Add new table"

# Rollback one migration
docker-compose -f docker-compose.dev.yml exec api alembic downgrade -1

# Show migration history
docker-compose -f docker-compose.dev.yml exec api alembic history
```

### Backup and Restore

**Backup:**
```bash
# Create backup directory (if it doesn't exist)
mkdir -p backups

# Backup database
docker exec signupflow-dev-db pg_dump -U signupflow signupflow_dev > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backups/
```

**Restore:**
```bash
# Stop API to avoid connections
docker-compose -f docker-compose.dev.yml stop api

# Drop and recreate database
docker exec signupflow-dev-db psql -U signupflow -c "DROP DATABASE IF EXISTS signupflow_dev;"
docker exec signupflow-dev-db psql -U signupflow -c "CREATE DATABASE signupflow_dev;"

# Restore from backup
docker exec -i signupflow-dev-db psql -U signupflow signupflow_dev < backups/backup_20250101_120000.sql

# Restart API
docker-compose -f docker-compose.dev.yml start api
```

### Accessing Redis

```bash
# Open Redis CLI
make redis-shell

# Common Redis commands
KEYS *                    # List all keys
GET rate_limit:login:*    # Get rate limit counter
FLUSHDB                   # Clear all keys (careful!)
INFO                      # Redis server info
```

---

## Testing

### Running Tests in Docker

**All tests:**
```bash
make test-docker
```

**Specific test file:**
```bash
docker-compose -f docker-compose.dev.yml exec api pytest tests/unit/test_auth.py -v
```

**With coverage:**
```bash
docker-compose -f docker-compose.dev.yml exec api pytest tests/ --cov=api --cov-report=html
```

**Interactive debugging:**
```bash
# Open shell in container
make shell

# Run tests with pdb
pytest tests/unit/test_auth.py -v -s --pdb
```

### Testing Database Features

```bash
# Start services
make up

# Run database-specific tests
docker-compose -f docker-compose.dev.yml exec api pytest tests/integration/ -v

# Check database state
make db-shell
SELECT * FROM people WHERE email = 'test@example.com';
```

---

## Troubleshooting

### Services Won't Start

**Problem:** `make up` fails with port conflict

```
Error: Bind for 0.0.0.0:5433 failed: port is already allocated
```

**Solution:**
```bash
# Check what's using the port
lsof -i :5433

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.dev.yml
ports:
  - "5434:5432"  # Use different port
```

### API Container Keeps Restarting

**Check logs:**
```bash
make logs-api
```

**Common causes:**

1. **Database not ready**
   - Wait for PostgreSQL health check to pass (5-10 seconds)
   - Check: `docker-compose -f docker-compose.dev.yml ps`

2. **Missing environment variables**
   - Check `.env` file exists
   - Verify required variables set

3. **Code syntax error**
   - Check logs for Python traceback
   - Fix code and container will auto-restart

### Hot-Reload Not Working

**Problem:** Code changes not reflected in API

**Solutions:**

1. **Check volume mounts:**
   ```bash
   docker-compose -f docker-compose.dev.yml exec api ls -la /app/api
   # Should show your local files
   ```

2. **Restart API container:**
   ```bash
   make restart-api
   ```

3. **Rebuild if dependencies changed:**
   ```bash
   make rebuild
   ```

### Database Connection Refused

**Problem:** API can't connect to PostgreSQL

**Check database is healthy:**
```bash
docker-compose -f docker-compose.dev.yml ps
# db should show "healthy"
```

**Check connection string:**
```bash
make shell
echo $DATABASE_URL
# Should be: postgresql://signupflow:password@db:5432/signupflow_dev
```

### Out of Disk Space

**Check Docker disk usage:**
```bash
docker system df
```

**Clean up:**
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Nuclear option (removes everything!)
docker system prune -a --volumes
```

### Permission Errors

**Problem:** Can't write to mounted volumes

**macOS/Linux:**
```bash
# Fix ownership
sudo chown -R $(whoami):$(whoami) ./data ./logs
```

**Windows:**
- Ensure Docker Desktop has access to the drive
- Check: Settings → Resources → File Sharing

---

## VS Code Integration

### Recommended Extensions

Install these VS Code extensions for better Docker development:

1. **Docker** (ms-azuretools.vscode-docker)
   - View running containers
   - View logs
   - Attach shell

2. **Remote - Containers** (ms-vscode-remote.remote-containers)
   - Develop inside container
   - Full IntelliSense
   - Debugging support

### Attach to Container

1. Open VS Code
2. Install "Remote - Containers" extension
3. Command Palette (`Cmd+Shift+P`) → "Remote-Containers: Attach to Running Container"
4. Select `signupflow-dev-api`
5. Open folder: `/app`

Now you have:
- ✅ Full IntelliSense for Python
- ✅ Debugging in container
- ✅ Terminal in container
- ✅ No need for local Python installation

### Debug Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

---

## Comparison: Docker vs Local Development

| Feature | Docker Development | Local Development |
|---------|-------------------|-------------------|
| **Setup Time** | ~5 minutes | ~15 minutes |
| **Dependencies** | All in containers | Install locally |
| **PostgreSQL** | ✅ Included | ⚠️ Manual install |
| **Redis** | ✅ Included | ⚠️ Manual install |
| **Hot-Reload** | ✅ Yes (2-3s delay) | ✅ Yes (instant) |
| **Database Testing** | ✅ Easy | ⚠️ Manual setup |
| **Billing Testing** | ✅ Easy (Redis) | ⚠️ Manual setup |
| **Production Parity** | ✅ High | ⚠️ Low (SQLite) |
| **Disk Space** | ~1GB | ~500MB |
| **Clean Uninstall** | ✅ `make clean-docker-all` | ⚠️ Manual cleanup |
| **Team Consistency** | ✅ Perfect | ⚠️ Varies |

### Recommendation

**Use Docker Development if:**
- ✅ You're working on billing, rate limiting, or caching features
- ✅ You're testing database migrations
- ✅ You're on a team and need consistent environments
- ✅ You want production-like environment

**Use Local Development if:**
- ✅ You're doing rapid frontend development (faster iteration)
- ✅ You're writing unit tests only (don't need full stack)
- ✅ You have limited disk space (<2GB free)

**Hybrid Approach (Best of Both Worlds):**
- Use Docker for database and Redis: `make up` (then stop API)
- Run API locally: `make run`
- Connect to Docker services via `localhost:5433` (PostgreSQL) and `localhost:6380` (Redis)

---

## Next Steps

### After Setup

1. **Verify Everything Works**
   ```bash
   make up
   make logs-api
   make test-docker
   ```

2. **Configure External Services**
   - Copy `.env.example` to `.env`
   - Add Mailtrap credentials (for email testing)
   - Add Stripe test keys (for billing testing)

3. **Read More Documentation**
   - [Quick Start Guide](QUICK_START.md)
   - [Deployment Guide](DEPLOYMENT.md)
   - [Security Guide](SECURITY.md)

### Production Deployment

When ready for production:

1. Use production `docker-compose.yml` (not `docker-compose.dev.yml`)
2. Follow [DEPLOYMENT.md](DEPLOYMENT.md) guide
3. Use production environment variables (no defaults)
4. Enable security features (HTTPS, secure secrets)

---

## FAQ

**Q: Do I need to install PostgreSQL locally?**
A: No! Docker includes PostgreSQL. Just run `make up`.

**Q: Will Docker containers use a lot of RAM?**
A: ~1GB RAM total. API: ~300MB, PostgreSQL: ~500MB, Redis: ~200MB.

**Q: Can I use Docker on M1/M2 Mac?**
A: Yes! Docker Desktop for Mac supports Apple Silicon. Images are built for ARM64.

**Q: How do I reset the database?**
A: `make clean-docker` removes all volumes and data. Then `make up` starts fresh.

**Q: Can I use both Docker and local development?**
A: Yes! Run Docker services (`make up`) but stop the API container, then run API locally (`make run`). Connect via `localhost:5433` (PostgreSQL) and `localhost:6380` (Redis).

**Q: Do I need to rebuild after every code change?**
A: No! Code is mounted as volumes. Only rebuild after dependency changes (`pyproject.toml`).

---

## Support

- **Documentation:** `/docs` directory
- **GitHub Issues:** https://github.com/tomqwu/signupflow/issues
- **Docker Docs:** https://docs.docker.com/compose/

---

**Last Updated:** 2025-10-24
**Version:** 1.0.0
**For:** SignUpFlow v1.0.0
