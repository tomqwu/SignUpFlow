# Developer Quickstart: Production Infrastructure

**Feature**: Production Infrastructure & Deployment
**Audience**: Developers setting up local environment with production-like infrastructure
**Time**: 15-20 minutes

---

## Prerequisites

Before starting, ensure you have:
- ✅ Docker Desktop installed (Docker 20.10+ and Docker Compose 2.0+)
- ✅ Python 3.11+ with Poetry installed
- ✅ Git repository cloned: `git clone https://github.com/tomqwu/SignUpFlow.git`
- ✅ Basic familiarity with command line and Docker

**Check Prerequisites**:
```bash
docker --version        # Should show Docker version 20.10+
docker-compose --version  # Should show Docker Compose version 2.0+
python --version         # Should show Python 3.11+
poetry --version         # Should show Poetry version 1.0+
```

---

## Quick Start (5 Minutes)

### Step 1: Start Infrastructure Services

From the project root directory:

```bash
# Start PostgreSQL and Redis via Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# NAME                COMMAND                  SERVICE   STATUS    PORTS
# signupflow-db-1     "docker-entrypoint.s…"   db        Up        5432->5432
# signupflow-redis-1  "redis-server"           redis     Up        6379->6379
```

**What this does**:
- Starts PostgreSQL 14 container on port 5432
- Starts Redis 7 container on port 6379
- Creates persistent volumes for data storage
- Both services auto-restart on failure

---

### Step 2: Configure Environment

Create `.env` file in project root (if not exists):

```bash
# Copy example environment file
cp .env.example .env

# Verify PostgreSQL connection string
cat .env | grep DATABASE_URL
```

**Expected `.env` contents**:
```bash
# Database (PostgreSQL in Docker)
DATABASE_URL=postgresql://signupflow:password@localhost:5432/signupflow

# Redis (Session storage)
REDIS_URL=redis://localhost:6379/0

# Application
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development

# External Services (Optional for local dev)
SENTRY_DSN=  # Leave empty for local development
```

---

### Step 3: Initialize Database

Run database migrations:

```bash
# Install dependencies (if not already done)
poetry install

# Run Alembic migrations
poetry run alembic upgrade head

# Verify database tables created
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow -c "\dt"

# Expected output: List of tables including deployments, health_checks, backup_jobs
```

---

### Step 4: Start Application

Start FastAPI application with PostgreSQL:

```bash
# Start development server with hot-reload
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Or use Makefile shortcut
make run
```

**Open in browser**: http://localhost:8000

**Verify health check**: http://localhost:8000/health

**Expected response**:
```json
{
  "status": "healthy",
  "version": "dev",
  "timestamp": "2025-10-20T14:31:00Z",
  "uptime_seconds": 10,
  "environment": "development",
  "checks": {
    "database": {
      "status": "connected",
      "response_time_ms": 5
    },
    "redis": {
      "status": "connected",
      "response_time_ms": 2
    }
  }
}
```

---

## Docker Compose Configuration

**File**: `docker-compose.yml` (project root)

```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    container_name: signupflow-db
    environment:
      POSTGRES_DB: signupflow
      POSTGRES_USER: signupflow
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U signupflow"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: signupflow-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
```

---

## Verifying Infrastructure Features

### 1. Health Check Endpoint

Test health check endpoint:

```bash
# Basic health check
curl http://localhost:8000/health | jq

# Expected: status = "healthy", database and redis both "connected"
```

Test degraded state (simulate slow database):
```bash
# Add artificial delay to database query
# (Implementation-specific - for testing only)

curl http://localhost:8000/health | jq

# Expected: status = "degraded", warnings array present
```

---

### 2. Database Connection Pooling

Verify PostgreSQL connection pooling works:

```python
# Python shell test
poetry run python

>>> from api.database import engine
>>> print(f"Pool size: {engine.pool.size()}")
>>> print(f"Max overflow: {engine.pool._max_overflow}")

# Expected:
# Pool size: 20
# Max overflow: 10
```

Test concurrent connections:

```bash
# Run concurrent requests
for i in {1..50}; do
  curl -s http://localhost:8000/health &
done
wait

# Verify no connection errors
# Check PostgreSQL active connections:
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow \
  -c "SELECT count(*) FROM pg_stat_activity WHERE datname='signupflow';"

# Expected: < 20 active connections (within pool limit)
```

---

### 3. Database Migration

Create and apply a test migration:

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "test_migration"

# Review generated migration in alembic/versions/
ls -la alembic/versions/

# Apply migration
poetry run alembic upgrade head

# Rollback migration (test rollback)
poetry run alembic downgrade -1

# Re-apply
poetry run alembic upgrade head
```

---

### 4. Graceful Shutdown

Test graceful shutdown handling:

```bash
# Start application in one terminal
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000

# In another terminal, send SIGTERM
ps aux | grep uvicorn  # Find process ID
kill -TERM <PID>

# Observe logs: Application should complete in-flight requests before shutting down
# Expected log: "Graceful shutdown initiated, completing active requests..."
```

---

## Testing Infrastructure Locally

### Run Infrastructure Tests

**Unit Tests** (config validation, graceful shutdown logic):
```bash
# Run infrastructure unit tests
poetry run pytest tests/unit/test_graceful_shutdown.py -v
poetry run pytest tests/unit/test_config_validation.py -v
```

**Integration Tests** (health checks, database operations):
```bash
# Run infrastructure integration tests
poetry run pytest tests/integration/test_health_checks.py -v
poetry run pytest tests/integration/test_postgres_migration.py -v
```

**E2E Tests** (deployment simulation):
```bash
# Run infrastructure E2E tests (requires Docker)
poetry run pytest tests/e2e/test_deployment.py -v
poetry run pytest tests/e2e/test_backup_restore.py -v
```

---

## Common Development Tasks

### Resetting Database

```bash
# Stop containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker volume rm signupflow_postgres_data signupflow_redis_data

# Start fresh
docker-compose up -d
poetry run alembic upgrade head
```

---

### Viewing Database Contents

```bash
# Connect to PostgreSQL
docker exec -it signupflow-db-1 psql -U signupflow -d signupflow

# List tables
\dt

# Query deployments
SELECT id, version, status, started_at FROM deployments ORDER BY started_at DESC LIMIT 5;

# Query health checks
SELECT instance_id, overall_status, timestamp FROM health_checks ORDER BY timestamp DESC LIMIT 10;

# Exit
\q
```

---

### Viewing Redis Contents

```bash
# Connect to Redis
docker exec -it signupflow-redis-1 redis-cli

# List all keys
KEYS *

# Get session data (example)
GET session:user_123

# Check Redis info
INFO stats

# Exit
exit
```

---

### Monitoring Logs

**Application logs**:
```bash
# Follow application logs
poetry run uvicorn api.main:app --log-level debug

# Or tail logs if running in background
tail -f logs/signupflow.log
```

**PostgreSQL logs**:
```bash
# Follow PostgreSQL logs
docker logs -f signupflow-db-1
```

**Redis logs**:
```bash
# Follow Redis logs
docker logs -f signupflow-redis-1
```

---

## Troubleshooting

### Issue 1: Port Already in Use

**Symptom**: `Error starting userland proxy: listen tcp 0.0.0.0:5432: bind: address already in use`

**Solution**: Stop conflicting service or change port

```bash
# Check what's using port 5432
lsof -i :5432

# Option A: Stop conflicting PostgreSQL
brew services stop postgresql  # macOS
sudo systemctl stop postgresql  # Linux

# Option B: Change port in docker-compose.yml
# Edit ports: "5433:5432" (host port 5433, container port 5432)
# Update DATABASE_URL in .env to localhost:5433
```

---

### Issue 2: Database Connection Refused

**Symptom**: `psycopg2.OperationalError: could not connect to server: Connection refused`

**Solution**: Verify Docker containers running

```bash
# Check container status
docker-compose ps

# If not running, start containers
docker-compose up -d

# Check PostgreSQL health
docker exec signupflow-db-1 pg_isready -U signupflow

# Expected: signupflow-db-1:5432 - accepting connections
```

---

### Issue 3: Migration Fails

**Symptom**: `sqlalchemy.exc.ProgrammingError: relation "deployments" already exists`

**Solution**: Check migration state

```bash
# Check current migration version
poetry run alembic current

# Check migration history
poetry run alembic history

# If out of sync, stamp database to current state
poetry run alembic stamp head

# Retry migration
poetry run alembic upgrade head
```

---

### Issue 4: Health Check Returns "unhealthy"

**Symptom**: `GET /health` returns `{"status": "unhealthy", "errors": [...]}`

**Solution**: Check dependency connections

```bash
# Test database connection
docker exec signupflow-db-1 pg_isready -U signupflow

# Test Redis connection
docker exec signupflow-redis-1 redis-cli ping

# Check application logs for specific error
tail -f logs/signupflow.log

# Restart dependencies
docker-compose restart db redis
```

---

## Production Differences

**Local Development** vs **Production**:

| Aspect | Development (Docker Compose) | Production (DigitalOcean) |
|--------|------------------------------|---------------------------|
| **Database** | PostgreSQL 14 in Docker | Managed PostgreSQL 14 |
| **Redis** | Redis 7 in Docker | Managed Redis |
| **SSL/HTTPS** | No SSL (HTTP only) | Let's Encrypt SSL (HTTPS) |
| **Backups** | Manual snapshots | Automated daily backups |
| **Scaling** | Single instance | Horizontal scaling (2-10 instances) |
| **Monitoring** | Local logs only | Centralized logging + Sentry |
| **Load Balancer** | No load balancer | DigitalOcean load balancer |

**Key Differences to Note**:
- Development uses localhost ports (5432, 6379)
- Production uses managed database URLs (internal network)
- Development has no SSL (use `http://localhost:8000`)
- Production has automatic SSL (use `https://signupflow.io`)

---

## Next Steps

After local setup complete:

1. **Test Infrastructure Features**: Run health check, verify database connection, test graceful shutdown
2. **Run Test Suite**: `make test-all` to verify infrastructure tests pass
3. **Build Docker Image**: Test containerization with `docker build -t signupflow:dev .`
4. **Review Deployment Pipeline**: Read `.github/workflows/deploy.yml` for CI/CD workflow
5. **Review Production Docs**: Read `docs/DEPLOYMENT_GUIDE.md` for production deployment

---

## Useful Commands

### Docker Compose

```bash
# Start services
docker-compose up -d

# Stop services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove containers + volumes (DELETES ALL DATA)
docker-compose down -v

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart db
docker-compose restart redis
```

### Database

```bash
# Run SQL file
docker exec -i signupflow-db-1 psql -U signupflow -d signupflow < scripts/seed_data.sql

# Export database
docker exec signupflow-db-1 pg_dump -U signupflow signupflow > backup.sql

# Import database
docker exec -i signupflow-db-1 psql -U signupflow -d signupflow < backup.sql
```

### Redis

```bash
# Flush all Redis data (WARNING: clears all sessions)
docker exec signupflow-redis-1 redis-cli FLUSHALL

# Monitor Redis commands in real-time
docker exec -it signupflow-redis-1 redis-cli MONITOR
```

---

## Resources

- **Docker Compose Docs**: https://docs.docker.com/compose/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/14/
- **Redis Docs**: https://redis.io/documentation
- **Alembic Docs**: https://alembic.sqlalchemy.org/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

---

## Support

**Issues**: If you encounter problems:
1. Check troubleshooting section above
2. Search GitHub issues: https://github.com/tomqwu/SignUpFlow/issues
3. Ask in team Slack channel: #signupflow-dev
4. Create new issue with logs and error details

**Questions**: For development questions:
- Slack: #signupflow-dev
- Email: dev@signupflow.io
- Documentation: `docs/` directory

---

**Last Updated**: 2025-10-20
**Maintainer**: SignUpFlow Infrastructure Team
