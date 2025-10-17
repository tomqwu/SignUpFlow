# End-to-End Testing Checklist

## Why This Document Exists

**Problem**: Features get implemented with unit/API tests that pass, but the actual user experience is broken because the complete flow wasn't tested.

**Solution**: Every feature MUST have an e2e test that simulates the exact user journey through the browser.

---

## Mandatory E2E Test Coverage for ALL Features

### 1. BEFORE Writing Code
- [ ] Write down the **user journey** in plain English
  - What screen does the user start on?
  - What buttons do they click?
  - What forms do they fill?
  - What should they see at each step?
  - What is the final outcome?

### 2. WHILE Writing Code
- [ ] Write the e2e test **FIRST** (TDD approach)
- [ ] Test should use Playwright to simulate real browser interactions
- [ ] Test should click actual buttons, fill actual forms
- [ ] Test should verify what the user sees on screen

### 3. AFTER Writing Code
- [ ] Run the e2e test and watch it pass
- [ ] Manually test in browser at least once
- [ ] Check for these common issues:
  - [ ] Are all UI elements visible that should be visible?
  - [ ] Are invitation-specific elements hidden for non-invitation flows?
  - [ ] Are form fields pre-filled correctly?
  - [ ] Are timezones/languages detected automatically?
  - [ ] Do error messages appear in the UI?
  - [ ] Does the success flow navigate to the right screen?

---

## User Journey Categories

### Authentication Flows
Every auth flow needs e2e tests covering:
1. **New Org Creator Journey**
   - Create org → Fill profile → Auto-become admin → See main app
   - Test: timezone detection, no invitation fields shown, admin role assigned

2. **Invitation Acceptance Journey**
   - Click invitation link → Pre-filled form → Set password → See main app
   - Test: name/email readonly, roles shown, correct org joined

3. **Login Journey**
   - Enter credentials → See main app → Correct role/org displayed
   - Test: remember me, language persistence, timezone

4. **Password Reset Journey**
   - Request reset → Click email link → Set new password → Login
   - Test: token validation, password requirements, success redirect

### Feature Flows
Every feature needs e2e test covering:
1. **Happy Path** - User does everything correctly
2. **Validation Errors** - User submits invalid data
3. **Edge Cases** - Empty states, conflicts, permissions

---

## E2E Test Template

```python
"""
E2E test for [FEATURE NAME]
Tests the complete user journey from [START] to [END]
"""
import pytest
from playwright.sync_api import Page, expect
import time


def test_[feature_name]_complete_user_journey(page: Page):
    """
    User Journey:
    1. [Step 1 - what user does]
    2. [Step 2 - what user does]
    3. [Step 3 - expected outcome]
    """

    # Setup - unique test data
    timestamp = int(time.time())
    test_data = {
        # ... generate unique test data
    }

    # Step 1: [Description]
    print("Step 1: [What we're testing]...")
    page.goto("http://localhost:8000/[starting-point]")
    page.wait_for_load_state("networkidle")

    # Verify starting state
    expect(page.locator('#[element]')).to_be_visible()

    # Step 2: [User action]
    print("Step 2: [What user does]...")
    page.locator('button:has-text("[Button Text]")').click()

    # Step 3: [Verification]
    print("Step 3: Verifying [expected outcome]...")
    expect(page.locator('#[expected-element]')).to_be_visible()

    # Verify UI state (IMPORTANT - check what user sees)
    # - Is correct data displayed?
    # - Are appropriate elements hidden/shown?
    # - Is user on the right screen?

    # Verify backend state (if applicable)
    # - Was data saved to database?
    # - Was API called correctly?

    # Take screenshot on failure
    try:
        assert_something()
    except AssertionError:
        page.screenshot(path=f"/tmp/test_failure_{timestamp}.png")
        raise

    print("✅ [FEATURE] complete user journey PASSED")


def test_[feature_name]_validation_errors(page: Page):
    """Test that user sees helpful errors for invalid input"""
    # Test empty form, invalid data, etc.
    pass


def test_[feature_name]_edge_cases(page: Page):
    """Test edge cases and error states"""
    # Test conflicts, permissions, missing data, etc.
    pass
```

---

## Red Flags That Indicate Missing E2E Tests

🚩 "The API test passes" - **Not enough!** Test the UI too.

🚩 "I tested the function" - **Not enough!** Test the user journey.

🚩 "It should work" - **Prove it!** Run an e2e test.

🚩 "Can you test it?" - **No!** Test it yourself BEFORE asking user.

🚩 "Backend is working" - **But what about the frontend?** Test the integration.

---

## Checklist Before Saying "It's Done"

- [ ] E2E test exists for this feature
- [ ] E2E test covers the complete user journey (not just API calls)
- [ ] E2E test validates what the user SEES (UI state)
- [ ] E2E test validates what the user EXPERIENCES (interactions)
- [ ] E2E test PASSES consistently
- [ ] Manually tested in browser at least once
- [ ] No TODOs or FIXMEs left in the code
- [ ] Error states are handled with user-friendly messages
- [ ] Loading states are handled (no blank screens)
- [ ] i18n translations exist for all user-visible text

---

## Common Mistakes to Avoid

### ❌ Testing Only the API
```python
# BAD - Only tests backend
def test_create_org():
    response = requests.post("/api/organizations/", json={...})
    assert response.status_code == 201
```

### ✅ Testing the User Journey
```python
# GOOD - Tests complete user experience
def test_create_org_user_journey(page: Page):
    # User clicks button
    page.locator('button:has-text("Create Organization")').click()

    # User fills form
    page.locator('#org-name').fill("My Org")

    # User submits
    page.locator('button[type="submit"]').click()

    # User sees success (on the screen, not just API response)
    expect(page.locator('#main-app')).to_be_visible()
    expect(page.locator('#org-name-display')).to_have_text("My Org")
```

### ❌ Not Checking UI State
```python
# BAD - Doesn't verify what user sees
def test_timezone():
    # Set timezone in code
    # Don't check if it's actually shown in UI
```

### ✅ Checking UI State
```python
# GOOD - Verifies user sees correct timezone
def test_timezone_auto_detection(page: Page):
    # Navigate to form
    # Check that timezone dropdown shows detected value
    timezone = page.locator('#user-timezone').input_value()
    assert timezone != "UTC"  # Should auto-detect, not default
```

---

## Test Coverage Goals

- **100% of user-facing features** must have e2e tests
- **All authentication flows** must be tested end-to-end
- **All forms** must be tested (submit, validation, errors)
- **All navigation** must be tested (screen transitions)

---

## Running E2E Tests

```bash
# Run all e2e tests
poetry run pytest tests/e2e/ -v

# Run specific user journey
poetry run pytest tests/e2e/test_org_creation.py -v -s

# Run with browser visible (for debugging)
poetry run pytest tests/e2e/ -v --headed

# Run and keep browser open on failure
poetry run pytest tests/e2e/ -v --headed --slowmo 500
```

---

## When to Skip E2E Tests

**Never.** If it's user-facing, it needs an e2e test.

Internal utilities, helper functions, and backend-only features can have unit tests only.
But anything a user interacts with = e2e test required.
