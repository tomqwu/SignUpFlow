# Testing Strategy - SignUpFlow

## Testing Framework Structure

```
tests/
├── unit/                   # Fast, isolated unit tests
│   ├── test_models.py      # SQLAlchemy model tests
│   ├── test_security.py    # JWT, bcrypt, RBAC tests
│   ├── test_services/      # Service layer tests
│   │   ├── test_email_service.py
│   │   ├── test_notification_service.py
│   │   └── test_solver_service.py
│   └── test_utils/         # Utility function tests
│
├── integration/            # API integration tests (TestClient)
│   ├── test_auth_api.py    # Authentication endpoints
│   ├── test_people_api.py  # /api/people/* endpoints
│   ├── test_events_api.py  # /api/events/* endpoints
│   ├── test_teams_api.py   # /api/teams/* endpoints
│   ├── test_solver_api.py  # /api/solver/* endpoints
│   ├── test_notification_api.py
│   └── test_email_integration.py  # REAL SMTP tests
│
├── e2e/                    # End-to-end browser tests (Playwright)
│   ├── test_auth_flows.py  # Login, signup, logout
│   ├── test_user_workflows.py  # Volunteer user journeys
│   ├── test_admin_workflows.py # Admin console workflows
│   ├── test_scheduler.py   # Full scheduling workflow
│   └── reports/            # Playwright HTML reports
│
├── conftest.py             # Pytest fixtures (shared)
└── pytest.ini              # Pytest configuration
```

## Test Types

### 1. Unit Tests (Fast, Isolated)

**Purpose**: Test individual functions/classes in isolation

**Characteristics**:
- Use mocks for external dependencies
- No database (or in-memory SQLite)
- No network calls
- Fast execution (< 1s each)

**Example**:
```python
# tests/unit/test_email_service.py
from unittest.mock import Mock, patch
from api.services.email_service import EmailService

def test_send_email_success():
    # Mock SMTP connection
    with patch('smtplib.SMTP') as mock_smtp:
        service = EmailService()
        result = service.send_email(...)
        assert result is not None
        mock_smtp.assert_called_once()
```

**Run**: `poetry run pytest tests/unit/ -v`

---

### 2. Integration Tests (TestClient, Real Database)

**Purpose**: Test API endpoints with real database but mocked auth

**Characteristics**:
- Use FastAPI TestClient
- Real SQLite test database
- Auth dependency overrides (no real JWT needed)
- No real external services (mock SMTP, etc.)

**Example**:
```python
# tests/integration/test_events_api.py
from fastapi.testclient import TestClient

def test_create_event(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/events?org_id=test_org",
        json={"title": "Test Event", ...},
        headers=auth_headers  # Mocked JWT
    )
    assert response.status_code == 201
```

**Run**: `poetry run pytest tests/integration/ -v`

---

### 3. E2E Tests (Playwright, Real Browser)

**Purpose**: Test complete user workflows in real browser

**Characteristics**:
- Real browser automation (Chromium/Firefox/WebKit)
- Real server running on localhost
- Real user interactions (click, type, navigate)
- Visual testing with screenshots

**Example**:
```python
# tests/e2e/test_auth_flows.py
from playwright.sync_api import Page, expect

def test_login_flow(page: Page):
    page.goto("http://localhost:8000/")
    page.locator('[data-i18n="auth.login"]').click()
    page.locator('input[type="email"]').fill("test@example.com")
    page.locator('input[type="password"]').fill("password")
    page.locator('button[type="submit"]').click()
    expect(page.locator('h1[data-i18n="app.dashboard"]')).to_be_visible()
```

**Run**: `poetry run pytest tests/e2e/ -v --html=reports/e2e-report.html`

---

## Current Issues & Fixes Needed

### Issue #1: comprehensive_test_suite.py Uses Real HTTP Requests ❌

**Problem**:
```python
# WRONG: Using requests.post() with real HTTP
response = requests.post(f"{API_BASE}/auth/login", json={...})
```

This bypasses:
- TestClient fixtures
- Dependency overrides
- Fast execution
- Proper test isolation

**Fix**: Convert to use TestClient from conftest.py
```python
# CORRECT: Using TestClient
def test_create_person(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/people/?org_id=test_org",
        json={...},
        headers=auth_headers
    )
    assert response.status_code == 201
```

---

### Issue #2: Playwright Browsers Not Installed ❌

**Problem**:
```
playwright._impl._errors.Error: Executable doesn't exist at /home/ubuntu/.cache/ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell
```

**Fix**:
```bash
playwright install chromium
```

---

### Issue #3: No HTML Test Reports for Playwright ❌

**Current**: No visual test reports

**Fix**: Add pytest-html plugin and configure Playwright HTML reports

```bash
# Install
poetry add --group dev pytest-html

# Run with reports
poetry run pytest tests/e2e/ --html=test-reports/e2e-report.html --self-contained-html
```

---

## Systematic Test Execution Plan

### Phase 1: Fix Test Framework (Priority 1)

1. ✅ Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

2. ✅ Convert comprehensive_test_suite.py to use TestClient:
   - Replace `requests.post()` with `client.post()`
   - Remove HTTP server dependency
   - Use conftest.py fixtures

3. ✅ Add pytest-html for reporting:
   ```bash
   poetry add --group dev pytest-html
   ```

### Phase 2: Organize Tests by Type (Priority 2)

1. Move tests to proper directories:
   - Unit tests → `tests/unit/`
   - Integration tests → `tests/integration/`
   - E2E tests → `tests/e2e/`

2. Create proper conftest.py for each directory

3. Update Makefile with organized targets:
   ```makefile
   test-unit:       # Fast unit tests only
   test-integration: # API integration tests
   test-e2e:        # Playwright E2E tests
   test-all:        # All tests with reports
   ```

### Phase 3: Add Test Reports (Priority 3)

1. **HTML Reports** (pytest-html):
   ```bash
   pytest tests/unit/ --html=test-reports/unit-report.html
   pytest tests/integration/ --html=test-reports/integration-report.html
   pytest tests/e2e/ --html=test-reports/e2e-report.html
   ```

2. **Playwright Reports** (built-in):
   ```python
   # pytest.ini
   [pytest]
   addopts = --html=test-reports/report.html --self-contained-html --tracing=on
   ```

3. **Coverage Reports** (pytest-cov):
   ```bash
   pytest tests/ --cov=api --cov-report=html:test-reports/coverage
   ```

---

## Test Execution Matrix

| Command | Tests Run | Duration | Use Case |
|---------|-----------|----------|----------|
| `make test-unit-fast` | Unit (no bcrypt) | ~7s | Quick feedback |
| `make test-unit` | All unit | ~7min | Pre-commit |
| `make test-integration` | Integration API | ~5min | API validation |
| `make test-e2e` | Playwright GUI | ~10min | Full workflows |
| `make test-all` | Everything | ~25min | CI/CD pipeline |

---

## Makefile Improvements

```makefile
# Fast unit tests (skip slow bcrypt tests)
test-unit-fast:
	poetry run pytest tests/unit/ -v -m "not slow"

# All unit tests
test-unit:
	poetry run pytest tests/unit/ -v --html=test-reports/unit-report.html

# Integration tests (API endpoints)
test-integration:
	poetry run pytest tests/integration/ -v --html=test-reports/integration-report.html

# E2E tests (Playwright)
test-e2e:
	poetry run pytest tests/e2e/ -v --html=test-reports/e2e-report.html --self-contained-html

# Email tests (REAL SMTP to Mailtrap)
test-email:
	set -a && source .env && set +a && \
	poetry run pytest tests/integration/test_email_integration.py -v --html=test-reports/email-report.html

# All tests with comprehensive reporting
test-all: test-unit test-integration test-e2e
	@echo "✅ All tests complete! Reports in test-reports/"

# Generate coverage report
test-coverage:
	poetry run pytest tests/ --cov=api --cov-report=html:test-reports/coverage --cov-report=term

.PHONY: test-unit-fast test-unit test-integration test-e2e test-email test-all test-coverage
```

---

## pytest.ini Configuration

```ini
[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Output
addopts =
    -v
    --tb=short
    --html=test-reports/report.html
    --self-contained-html
    --strict-markers

# Markers
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (TestClient, real DB)
    e2e: End-to-end tests (Playwright, real browser)
    slow: Slow tests (bcrypt, external services)
    email: Email integration tests (real SMTP)

# Asyncio
asyncio_mode = auto
```

---

## Next Steps

### Immediate (Today):
1. ✅ Install Playwright browsers
2. ✅ Fix comprehensive_test_suite.py authentication
3. ✅ Run `make test-all` and verify all pass

### Short-term (This Week):
1. Organize tests into unit/integration/e2e directories
2. Add HTML test reports
3. Create Playwright visual regression tests

### Long-term (Next Sprint):
1. Add coverage requirements (80% minimum)
2. CI/CD integration (GitHub Actions)
3. Performance benchmarking tests
4. Load testing with Locust

---

## Success Criteria

✅ **Unit Tests**: 100% pass rate, <10s execution
✅ **Integration Tests**: 100% pass rate, <5min execution
✅ **E2E Tests**: 100% pass rate, <15min execution
✅ **Test Reports**: HTML reports with screenshots for failures
✅ **Coverage**: >80% code coverage
✅ **CI/CD**: All tests passing in pipeline

---

**Status**: 🚧 In Progress - Fixing test framework structure
**Last Updated**: 2025-10-22
**Owner**: Development Team
