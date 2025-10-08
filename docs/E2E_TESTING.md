# End-to-End Testing Guide

## Overview

This document describes the E2E test suite for Rostio, which validates all user stories and critical workflows using Playwright browser automation.

## Test Suite Structure

### Test Files

1. **test_auth_flows.py** - Authentication workflows
   - Signup new user
   - Login existing user
   - Logout functionality
   - Protected route redirects
   - Session persistence
   - Invalid credentials handling

2. **test_login_flow.py** - Detailed login flow testing
   - Login page display
   - Form submission
   - Console log verification

3. **test_invitation_flow.py** - Invitation system
   - Admin sending invitations
   - Token validation
   - Accepting invitations

4. **test_calendar_features.py** - Calendar export/subscription
   - Export personal calendar (ICS)
   - Webcal subscription URLs
   - Calendar feed endpoints
   - Admin org calendar export

5. **test_admin_console.py** - Admin functionality
   - Tab navigation (Events, People, Teams, Roles, Settings)
   - Create events
   - Manage people
   - Manage teams
   - Role management
   - Organization settings
   - Permission checks

6. **test_user_features.py** - Regular user features
   - View schedule
   - Set availability/blocked dates
   - Browse events
   - Join events
   - Change language
   - Update profile
   - Timezone support

## Running Tests

### Run All E2E Tests

```bash
./run_e2e_tests.sh
```

### Run Specific Test Suite

```bash
# Authentication tests
poetry run pytest tests/e2e/test_auth_flows.py -v

# Admin console tests
poetry run pytest tests/e2e/test_admin_console.py -v

# Calendar features
poetry run pytest tests/e2e/test_calendar_features.py -v
```

### Run Individual Test

```bash
poetry run pytest tests/e2e/test_auth_flows.py::test_login_existing_user -v -s
```

### Run with Screenshots

```bash
poetry run pytest tests/e2e/ -v --screenshot=on
```

## Test Coverage

### ✅ Currently Tested

- **Authentication**: Login, logout, session persistence, protected routes
- **JWT Security**: Token-based authentication, auto-redirect on 401
- **Basic Navigation**: Router functionality, screen transitions
- **Error Handling**: Invalid credentials, console error detection

### 🔄 Partially Tested

- **Admin Console**: Tab structure verified, CRUD operations need implementation testing
- **Calendar Features**: Export endpoints verified, full workflow needs testing
- **User Features**: UI navigation verified, data persistence needs testing

### ⏳ To Be Tested

- **Invitation Workflow**: End-to-end invitation acceptance (requires valid tokens)
- **Role Management**: Create/edit/delete roles, assign to users
- **Recurring Events**: Create and manage recurring events
- **Conflict Detection**: Availability conflict warnings
- **i18n**: Language switching persistence across page reloads

## Test Results

### Current Status (as of latest run)

```
Authentication Flows: 5/6 passing (83%)
Login Flow: 2/3 passing (67%)
Admin Console: Exploratory (UI verification)
Calendar Features: Exploratory (endpoint verification)
User Features: Exploratory (UI verification)
```

### Known Issues

1. **Signup flow test fails**: Needs investigation of profile creation step
2. **Some tests are exploratory**: They verify UI exists but don't fully test functionality

## Writing New E2E Tests

### Test Template

```python
import pytest
from playwright.sync_api import Page, expect


def test_feature_name(page: Page):
    """Test description."""
    # Login if needed
    page.goto("http://localhost:8000/login")
    page.fill("#login-email", "pastor@grace.church")
    page.fill("#login-password", "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    # Navigate to feature
    page.goto("http://localhost:8000/app/feature")
    page.wait_for_timeout(1000)

    # Interact with UI
    button = page.locator("button:has-text('Action')")
    button.click()

    # Verify result
    expect(page.locator("#result")).to_be_visible()

    # Take screenshot for debugging
    page.screenshot(path="/tmp/e2e-feature.png")
```

### Best Practices

1. **Use wait_for_timeout sparingly**: Prefer `expect().to_be_visible()` with timeout
2. **Take screenshots**: Helps debug failing tests
3. **Check multiple locators**: Use fallbacks (CSS, text, role)
4. **Test error cases**: Not just happy paths
5. **Keep tests independent**: Each test should work in isolation

## Debugging Failed Tests

### View Screenshots

```bash
ls -lh /tmp/e2e-*.png
open /tmp/e2e-*.png  # macOS
xdg-open /tmp/e2e-*.png  # Linux
```

### Run with Browser Visible

```python
# Change in test file temporarily
browser = p.chromium.launch(headless=False)
```

### Check Console Logs

```python
def log_console(msg):
    print(f"[CONSOLE {msg.type}]: {msg.text}")

page.on("console", log_console)
```

### Enable Slow Motion

```python
browser = p.chromium.launch(headless=False, slow_mo=1000)  # 1 second delay
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          poetry install
          poetry run playwright install chromium
      - name: Start server
        run: poetry run uvicorn api.main:app &
      - name: Run E2E tests
        run: poetry run pytest tests/e2e/ -v
      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-screenshots
          path: /tmp/e2e-*.png
```

## Maintenance

### When to Update Tests

- ✅ After implementing new features
- ✅ When UI changes significantly
- ✅ When adding new user stories
- ✅ After fixing bugs (add regression test)

### Test Health Checks

Run E2E suite at least:
- Before each release
- After major refactoring
- Weekly in CI/CD

## Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Pytest Playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [User Stories](../docs/SAAS_DESIGN.md)
- [API Documentation](../docs/API.md)
