# Contributing to Rostio

## Before Making ANY Changes

### The Golden Rule
**If a user will see it, it needs an e2e test. No exceptions.**

---

## Development Workflow

### 1. Plan the Feature
- [ ] Write down the user journey in plain English
- [ ] Identify what screens/forms/buttons are involved
- [ ] Note any dependencies (i18n, timezone, roles, etc.)

### 2. Write the E2E Test FIRST
- [ ] Create test in `tests/e2e/test_[feature].py`
- [ ] Use the template from [E2E_TESTING_CHECKLIST.md](docs/E2E_TESTING_CHECKLIST.md)
- [ ] Test should simulate EXACT user clicks/inputs
- [ ] Test should verify WHAT USER SEES (not just API responses)
- [ ] Run test - it should FAIL (test-first approach)

### 3. Implement the Feature
- [ ] Write minimum code to make e2e test pass
- [ ] Check for dependencies:
  - [ ] i18n translations for all text
  - [ ] Timezone handling
  - [ ] Role/permission checks
  - [ ] Form validation (both frontend and backend)
  - [ ] Error handling with user-friendly messages

### 4. Verify the Feature
- [ ] Run e2e test - it should PASS
- [ ] Manually test in browser
- [ ] Check browser console for errors
- [ ] Check network tab for failed requests
- [ ] Test with different user roles
- [ ] Test with different languages (if i18n)

### 5. Before Submitting
- [ ] Run ALL e2e tests: `poetry run pytest tests/e2e/ -v`
- [ ] All tests pass
- [ ] No TODOs or FIXMEs in code
- [ ] No console errors in browser
- [ ] Screenshot test passes (if UI change)

---

## E2E Test Requirements

Every user-facing feature MUST have:

1. **Happy Path Test** - User does everything correctly
   ```python
   def test_[feature]_complete_user_journey(page: Page):
       # Simulate exact user clicks
       # Verify what user sees at each step
   ```

2. **Validation Test** - User submits invalid data
   ```python
   def test_[feature]_validation_errors(page: Page):
       # Submit empty form
       # Submit invalid data
       # Verify error messages appear
   ```

3. **UI State Test** - Verify UI elements are correct
   ```python
   def test_[feature]_ui_state(page: Page):
       # Check elements are visible/hidden correctly
       # Check form fields are pre-filled
       # Check timezone/language auto-detection
   ```

---

## Common Feature Dependencies

### Authentication Features
- [ ] JWT token handling
- [ ] Role-based access control
- [ ] Session persistence
- [ ] Logout functionality

### Forms
- [ ] Client-side validation
- [ ] Server-side validation
- [ ] Error messages in UI
- [ ] Success feedback
- [ ] i18n for all text
- [ ] Timezone handling (if date/time fields)

### Navigation
- [ ] URL routing
- [ ] Back button handling
- [ ] Screen transitions
- [ ] State cleanup between screens

### i18n
- [ ] All text in translation files
- [ ] Language switcher updates all text
- [ ] Fallback to English if translation missing
- [ ] Date/time formatting respects locale

---

## Testing Checklist

### Before Saying "Done"

**Feature Implementation:**
- [ ] E2E test exists and covers complete user journey
- [ ] E2E test verifies UI state (what user sees)
- [ ] E2E test passes consistently
- [ ] Manually tested in browser
- [ ] All console errors fixed
- [ ] All network errors fixed

**Code Quality:**
- [ ] No hardcoded strings (use i18n)
- [ ] No TODOs or FIXMEs
- [ ] Error handling for all async operations
- [ ] Loading states for all async operations

**Dependencies:**
- [ ] i18n translations added (all languages)
- [ ] Timezone handling implemented
- [ ] Role/permission checks in place
- [ ] Form validation (frontend + backend)

**Testing:**
- [ ] Unit tests for business logic
- [ ] E2E tests for user journeys
- [ ] All tests pass
- [ ] No flaky tests

---

## Red Flags

🚩 **"The API works"** → Did you test the UI?

🚩 **"The test passes"** → Did you test the COMPLETE user journey?

🚩 **"It should work"** → Did you actually TEST it in the browser?

🚩 **"Can you test it?"** → NO. Test it yourself FIRST.

🚩 **"I'll add tests later"** → NO. Tests come FIRST.

---

## Example: Good vs Bad Approach

### ❌ Bad Approach
1. Implement feature
2. Write API test
3. API test passes
4. Say "it's done"
5. User reports bug
6. Waste time debugging
7. Realize UI was never tested

### ✅ Good Approach
1. Write user journey description
2. Write e2e test simulating user clicks
3. Test fails (good!)
4. Implement feature
5. Test passes
6. Manually verify in browser
7. Ship with confidence

---

## Running Tests

```bash
# Run all e2e tests before committing
poetry run pytest tests/e2e/ -v

# Run specific test file
poetry run pytest tests/e2e/test_org_creation.py -v -s

# Run all tests (unit + e2e)
make test-all

# Run with browser visible (debugging)
poetry run pytest tests/e2e/ -v --headed --slowmo 500
```

---

## Questions?

See [E2E_TESTING_CHECKLIST.md](docs/E2E_TESTING_CHECKLIST.md) for detailed testing guidelines.

**Remember**: If a user can see it, click it, or type in it → it needs an e2e test. No exceptions.
