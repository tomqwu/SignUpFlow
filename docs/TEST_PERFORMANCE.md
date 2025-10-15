# Test Suite Performance Guide

This document explains the performance characteristics of the Rostio test suite and how to optimize test execution time.

## Quick Reference

| Command | Duration | Use Case |
|---------|----------|----------|
| `make test-unit` | ~10s | Full unit test suite |
| `make test-unit-fast` | ~7s | Skip slow password hashing tests |
| `make test-frontend` | ~0.4s | Frontend JavaScript tests only |
| `make pre-commit` | ~10s | Fast pre-commit validation |
| `make test-with-timing` | ~10s | Show slowest tests |
| `make test-all` | ~5min | Complete test suite (all tests) |

## Test Performance Breakdown

### Unit Tests (190 tests, ~10s total)

**Slowest Tests** (intentionally slow for security):
- Password hashing tests: 0.6-0.8s each (bcrypt is computationally expensive by design)
- These are the slowest 10-15 tests but critical for security validation

**Fast Tests** (majority):
- Most unit tests: <0.1s each
- Database operations: <0.05s each
- Model validation: <0.01s each

### Frontend Tests (50 tests, ~0.4s total)

All frontend tests are fast (<0.01s average):
- Integration tests
- Router tests
- i18n tests
- App user function tests

### E2E Tests (70 tests, variable)

E2E tests use Playwright for browser automation:
- Auth flows: ~25s (9 tests)
- Admin console: ~54s (7 tests)
- RBAC security: ~22s (27 tests)
- Settings: Variable
- Total: ~3-5 minutes

**Note**: E2E tests timeout at 30-600s depending on complexity.

## Optimization Strategies

### 1. Use Fast Test Commands

For rapid development iteration:

```bash
# Run only fast tests (skip slow password hashing)
make test-unit-fast

# Run frontend tests only (very fast)
make test-frontend

# Pre-commit validation (unit tests only)
make pre-commit
```

### 2. Test Markers

Tests are marked for selective execution:

```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run only E2E tests
pytest -m e2e
```

Available markers:
- `unit`: Unit tests
- `integration`: Integration tests
- `e2e`: End-to-end tests
- `gui`: GUI tests with Playwright
- `api`: API tests
- `slow`: Slow running tests (>0.5s)
- `fast`: Fast running tests (<0.1s)

### 3. Parallel Execution

**⚠️ Not recommended for unit tests** due to SQLite limitations.

SQLite doesn't handle concurrent writes well, leading to "disk I/O error" failures when running tests in parallel.

**Alternative**: Run different test suites in parallel terminals:

```bash
# Terminal 1
make test-frontend

# Terminal 2
make test-unit

# Terminal 3
make test-integration
```

### 4. Target Specific Tests

When working on a specific feature:

```bash
# Run specific test file
make test-unit-file FILE=tests/unit/test_people.py

# Run specific E2E test
make test-e2e-file FILE=tests/e2e/test_login_flow.py

# Run specific test function
pytest tests/unit/test_people.py::TestPeopleAPI::test_create_person -v
```

## Why Are Password Tests Slow?

The password hashing tests (0.6-0.8s each) are intentionally slow because:

1. **bcrypt is designed to be computationally expensive** - This prevents brute-force attacks
2. **Security > Speed** - Slow password hashing is a security feature, not a bug
3. **Only affects tests** - In production, users hash passwords once during signup/login

If you need faster iteration during development, use:

```bash
make test-unit-fast  # Skips password hashing tests
```

## Measuring Performance

### Show timing for slowest tests:

```bash
make test-with-timing
```

This shows the 20 slowest tests with execution times.

### Run with duration analysis:

```bash
pytest tests/unit/ --durations=0  # Show all test durations
pytest tests/unit/ --durations=10  # Show top 10 slowest
```

### Generate performance report:

```bash
pytest tests/unit/ --durations=20 --tb=no -v > performance_report.txt
```

## Best Practices

### During Development

1. **Use `make pre-commit`** before committing (fast, comprehensive)
2. **Run specific test files** when working on a feature
3. **Use `make test-unit-fast`** for rapid iteration
4. **Run `make test-all`** before pushing to remote

### In CI/CD

1. **Run all tests** (`make test-all`) for pull requests
2. **Use timeout limits** for E2E tests (default: 600s)
3. **Generate coverage reports** on main branch
4. **Cache dependencies** (poetry, npm) to speed up setup

### Test Writing Guidelines

1. **Mark slow tests** with `@pytest.mark.slow`
2. **Minimize database operations** in unit tests
3. **Use fixtures** to avoid redundant setup
4. **Mock external services** to reduce test time
5. **Keep E2E tests focused** on critical user paths

## Performance Troubleshooting

### Tests taking too long?

1. Check if database setup is running multiple times
2. Verify fixtures are using correct scope (`session` vs `function`)
3. Look for unnecessary waits in E2E tests
4. Use `--durations` to identify bottlenecks

### Tests timing out?

1. Increase timeout for E2E tests: `timeout 600 pytest tests/e2e/`
2. Check for infinite loops or blocking operations
3. Verify API server is running for E2E/integration tests
4. Check network connectivity for external service tests

### Database errors in parallel?

SQLite can't handle concurrent writes. Solutions:

1. Don't use `-n auto` for unit tests with database
2. Run test suites sequentially
3. Or switch to PostgreSQL for test database (more complex setup)

## Future Optimizations

Potential improvements (not yet implemented):

1. **Test database pooling** - Reuse database connections
2. **Fixture caching** - Cache expensive setup operations
3. **Selective test running** - Only run tests affected by changes
4. **PostgreSQL test database** - Better concurrent access
5. **Distributed testing** - Run E2E tests across multiple workers

## Summary

The Rostio test suite is optimized for reliability and security over raw speed. For development:

- **Use `make pre-commit`** for quick validation (~10s)
- **Use `make test-unit-fast`** to skip slow security tests (~7s)
- **Use `make test-frontend`** for UI iteration (~0.4s)
- **Run `make test-all`** before pushing (~5min)

The slow password tests are a feature, not a bug - they ensure our security implementation is robust.
