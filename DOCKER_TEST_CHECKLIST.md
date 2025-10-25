# Docker Development Environment - Test Checklist

This checklist validates that the Docker Compose development environment is working correctly.

## Automated Testing

**Quick automated test (recommended):**

```bash
./scripts/test_docker_setup.sh
```

This script runs all 18 tests below automatically.

---

## Manual Testing Checklist

Use this if you prefer to test manually or if the automated script fails.

### Prerequisites

- [ ] Docker Desktop installed and **running**
- [ ] Port 8000, 5433, and 6380 available (not in use)
- [ ] At least 2GB free disk space
- [ ] At least 2GB free RAM

### Phase 1: Build and Start

```bash
# 1. Build images
make build
```
- [ ] Build completes without errors
- [ ] No "ERROR" messages in output
- [ ] Image size ~800MB (reasonable)

```bash
# 2. Start services
make up
```
- [ ] All 3 services start (db, redis, api)
- [ ] Output shows "✅ Services started!"
- [ ] No error messages

```bash
# 3. Check service status
make ps
```
Expected output:
```
NAME                    STATUS              PORTS
signupflow-dev-api      Up (healthy)       0.0.0.0:8000->8000/tcp
signupflow-dev-db       Up (healthy)       0.0.0.0:5433->5432/tcp
signupflow-dev-redis    Up (healthy)       0.0.0.0:6380->6379/tcp
```

- [ ] All 3 services show "Up"
- [ ] All 3 services show "(healthy)" status
- [ ] Ports mapped correctly

### Phase 2: Service Health Checks

```bash
# 4. Test API health endpoint
curl http://localhost:8000/health
```
Expected output:
```json
{"status":"healthy","database":"connected"}
```

- [ ] API responds on port 8000
- [ ] Status is "healthy"
- [ ] Database is "connected"

```bash
# 5. Test API documentation
open http://localhost:8000/docs
```
- [ ] Swagger UI loads
- [ ] Can see API endpoints
- [ ] No errors in browser console

```bash
# 6. Test frontend loads
open http://localhost:8000
```
- [ ] Homepage loads
- [ ] CSS styles applied
- [ ] Login form visible
- [ ] No errors in browser console

### Phase 3: Database Operations

```bash
# 7. Run database migrations
make migrate-docker
```
- [ ] Migrations run without errors
- [ ] Output shows "✅ Migrations complete"

```bash
# 8. Open PostgreSQL shell
make db-shell
```

In the PostgreSQL shell, run:
```sql
-- List tables
\dt

-- Should see: people, events, teams, etc.

-- Query default admin user
SELECT id, email, name, roles FROM people LIMIT 1;

-- Exit
\q
```

- [ ] Shell opens successfully
- [ ] Tables exist (people, events, organizations, etc.)
- [ ] Default user exists (`jane@test.com`)
- [ ] Can exit cleanly

```bash
# 9. Test Redis
make redis-shell
```

In the Redis CLI, run:
```
PING
# Should respond: PONG

INFO server
# Should show Redis version

EXIT
```

- [ ] Redis CLI opens
- [ ] PING returns PONG
- [ ] Can exit cleanly

### Phase 4: Testing

```bash
# 10. Run unit tests
make test-docker
```
- [ ] Tests run without errors
- [ ] High pass rate (280+ tests passing)
- [ ] No critical failures

```bash
# 11. Run specific test file
docker-compose -f docker-compose.dev.yml exec api pytest tests/unit/test_calendar.py -v
```
- [ ] Specific test file runs
- [ ] Tests pass

### Phase 5: Hot-Reload Testing

```bash
# 12. View API logs in real-time
make logs-api
```
Keep this terminal open, then in another terminal:

```bash
# 13. Edit a Python file
echo "# Test comment" >> api/main.py
```

In the logs terminal:
- [ ] See "Detected file change"
- [ ] See "Reloading..."
- [ ] Reload completes in 2-3 seconds
- [ ] No errors during reload

Undo the change:
```bash
git checkout api/main.py
```

### Phase 6: Shell Access

```bash
# 14. API container shell
make shell
```

Inside the container, run:
```bash
# Check Python version
python --version
# Should be Python 3.11+

# Check installed packages
pip list | grep fastapi
# Should show fastapi

# Check file structure
ls -la /app/api/

# Exit
exit
```

- [ ] Shell opens in container
- [ ] Python 3.11+ available
- [ ] Packages installed
- [ ] Code files visible
- [ ] Can exit cleanly

### Phase 7: Makefile Commands

Test all Makefile commands work:

```bash
make logs           # View logs (all services)
```
- [ ] Shows logs from api, db, redis
- [ ] Can Ctrl+C to exit

```bash
make logs-api       # View API logs only
```
- [ ] Shows only API logs
- [ ] Can Ctrl+C to exit

```bash
make logs-db        # View PostgreSQL logs only
```
- [ ] Shows only database logs
- [ ] Can Ctrl+C to exit

```bash
make logs-redis     # View Redis logs only
```
- [ ] Shows only Redis logs
- [ ] Can Ctrl+C to exit

```bash
make restart-api    # Restart API only
```
- [ ] API restarts quickly (~5 seconds)
- [ ] Other services not affected
- [ ] API comes back healthy

### Phase 8: Data Persistence

```bash
# 15. Create test data
make shell
```

In the container:
```bash
# Create a test file
echo "test data" > /app/data/test.txt
exit
```

```bash
# 16. Restart services
make down
make up
```

```bash
# 17. Verify data persists
make shell
cat /app/data/test.txt
# Should show: test data
exit
```

- [ ] Data persists across container restarts
- [ ] Volumes working correctly

### Phase 9: Cleanup

```bash
# 18. Stop services
make down
```
- [ ] All services stop
- [ ] Output shows "✅ Services stopped"
- [ ] No error messages

```bash
# 19. Check services stopped
make ps
```
- [ ] No services running
- [ ] Or shows "no containers"

```bash
# 20. Clean volumes (optional - deletes data)
make clean-docker
```
- [ ] Volumes removed
- [ ] Data deleted (expected)
- [ ] Ready for fresh start

---

## Test Results Summary

**Date Tested:** _______________

**Tester:** _______________

**Results:**
- Total tests attempted: _____ / 20
- Tests passed: _____ / 20
- Tests failed: _____ / 20

**Failed Tests (if any):**
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Overall Assessment:**
- [ ] ✅ All tests passed - Ready for development
- [ ] ⚠️ Some tests failed - Review troubleshooting
- [ ] ❌ Many tests failed - Needs investigation

---

## Troubleshooting

### Services won't start

**Problem:** Port already in use
```bash
lsof -i :8000
lsof -i :5433
lsof -i :6380

# Kill conflicting process or change ports in docker-compose.dev.yml
```

**Problem:** Docker daemon not running
```bash
# Start Docker Desktop application
open -a Docker
```

### Services unhealthy

**Problem:** API shows unhealthy
```bash
# View API logs
make logs-api

# Common causes:
# - Database not ready (wait 30 seconds)
# - Missing dependencies (run: make rebuild)
# - Code syntax error (check logs)
```

**Problem:** Database connection refused
```bash
# Check database is healthy
make ps

# If not healthy, restart
make restart-api
```

### Tests failing

**Problem:** Tests fail in Docker
```bash
# Check test dependencies installed
make shell
pip list | grep pytest

# Re-run specific test with more detail
pytest tests/unit/test_calendar.py -vv -s
```

### Hot-reload not working

**Problem:** Code changes not reflected
```bash
# Check volume mounts
docker-compose -f docker-compose.dev.yml exec api ls -la /app/api/

# If files not visible, rebuild
make rebuild
```

---

## Performance Benchmarks

Expected performance metrics:

| Operation | Expected Time |
|-----------|--------------|
| `make build` (first time) | 2-4 minutes |
| `make build` (cached) | 10-30 seconds |
| `make up` | 10-15 seconds |
| `make down` | 2-5 seconds |
| Hot-reload (code change) | 2-3 seconds |
| `make migrate-docker` | 5-10 seconds |
| `make test-docker` | 1-2 minutes |

---

## Success Criteria

✅ **Development environment is ready when:**

1. All services start and show "healthy" status
2. API responds on http://localhost:8000
3. Database migrations complete
4. Tests pass (280+ tests)
5. Hot-reload works (code changes apply in 2-3 seconds)
6. All shell access works (API, PostgreSQL, Redis)
7. Data persists across restarts

---

## Next Steps After Testing

Once all tests pass:

1. **Read Documentation**
   - [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)
   - [docs/DOCKER_DEVELOPMENT.md](docs/DOCKER_DEVELOPMENT.md)

2. **Start Development**
   ```bash
   make up
   # Edit code in api/ or frontend/
   # Changes apply automatically!
   ```

3. **Common Workflows**
   ```bash
   make logs-api      # Watch logs while developing
   make shell         # Debug in container
   make test-docker   # Run tests before commit
   make down          # Stop when done
   ```

---

**Last Updated:** 2025-10-24
**Version:** 1.0.0
