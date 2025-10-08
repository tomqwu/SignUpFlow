# Comprehensive Test Suite Documentation

## Overview

This document describes the complete test coverage for the Rostio application, including unit tests, integration tests, and end-to-end tests.

## Test Statistics

### Current Coverage
- **Frontend Tests**: 50 tests
  - Unit tests: 37 tests
  - Integration tests: 13 tests
- **Backend Unit Tests**: 159 tests
- **Backend Integration Tests**: 7 tests (SPA routing & roles)
- **Total**: 216 automated tests

## Test Categories

### 1. Frontend Unit Tests (`frontend/tests/`)

#### `i18n.test.js` (12 tests)
- Initialization and locale management
- Translation functions
- DOM translation
- Language switching workflow
- Prevents `[object Object]` display bugs

#### `router.test.js` (9 tests)
- Navigation between screens
- Screen management
- Route handling
- Browser back/forward support
- Authentication-aware routing

#### `app-user.test.js` (16 tests)
- Session management (save/load/clear)
- Language persistence
- Role handling (strings vs objects)
- Form validation
- Translation page function
- Current view tracking

### 2. Frontend Integration Tests (`frontend/tests/integration.test.js`)

#### Role Display Integration (3 tests)
- Handles API returning role objects correctly
- Handles API returning role strings correctly
- Displays roles in settings modal without `[object Object]`

#### Router Authentication Integration (3 tests)
- Exposes `currentUser` to window for router access
- Clears `window.currentUser` on logout
- Restores `currentUser` from localStorage on page load

#### Language Persistence Integration (2 tests)
- Saves language with user data to API
- Loads user language on page load

#### Translation Integration (1 test)
- Translates page without `[object Object]`

#### Session Management Integration (2 tests)
- Saves and restores complete session
- Handles missing session gracefully

#### API Error Handling Integration (2 tests)
- Handles API errors gracefully
- Handles 404 responses correctly

### 3. Backend Unit Tests (`tests/unit/`)

#### `test_availability.py` (10 tests)
- Add/remove time-off
- Check availability conflicts
- Validate date ranges

#### `test_calendar.py` (18 tests)
- ICS calendar generation
- Calendar subscriptions
- Export functionality

#### `test_db_helpers.py` (17 tests)
- Database operations
- CRUD helpers
- Data validation

#### `test_dependencies.py` (16 tests)
- Dependency injection
- Authentication dependencies
- Database session management

#### `test_event_roles.py` (7 tests)
- Event role assignment
- Role validation
- Role updates

#### `test_events.py` (18 tests)
- Event creation
- Recurring events
- Event updates and deletion

#### `test_organizations.py` (12 tests)
- Organization CRUD
- Configuration management
- Multi-org support

#### `test_people.py` (16 tests)
- Person CRUD
- Role assignment
- Language preferences

#### `test_person_language.py` (5 tests)
- Language field validation
- Language persistence
- Default language handling

#### `test_security.py` (27 tests)
- Authentication
- Password hashing
- Token management
- Permission checks

#### `test_teams.py` (13 tests)
- Team management
- Member assignment
- Team roles

### 4. Backend Integration Tests (`tests/integration/`)

#### `test_spa_routing_and_roles.py` (7 tests)
**Critical Bug Prevention Tests:**

1. **SPA Routing on Reload**
   - Verifies `/availability` returns HTML on reload
   - Prevents "Unexpected token '<'" errors

2. **Static Assets MIME Types**
   - JavaScript files: `application/javascript` ✅
   - CSS files: `text/css` ✅

3. **Absolute Paths in HTML**
   - Ensures scripts use `/js/...` not `js/...`
   - Prevents path resolution bugs on nested routes

4. **Role Display Structure**
   - Validates roles are strings, not objects
   - Prevents `[object Object]` display bug

5. **Nested Routes Serve Index.html**
   - All app routes (`/`, `/login`, `/availability`, etc.) return HTML
   - Absolute paths preserved on all routes

6. **API Routes Isolation**
   - API routes return JSON, never HTML
   - SPA fallback doesn't interfere with API

7. **Locale Files Served Correctly**
   - JSON files have `application/json` MIME type
   - All locales (en, zh-CN, zh-TW) accessible

#### Other Integration Tests
- `test_auth.py`: Authentication workflows
- `test_availability_crud.py`: Availability CRUD operations
- `test_invitations.py`: Invitation system
- `test_multi_org_workflow.py`: Multi-organization workflows

### 5. End-to-End Tests (`tests/e2e/`)

#### `test_complete_user_workflow.py` (7 tests)
**Full User Journey Tests:**

1. **Complete Signup and Login Workflow**
   - Uses i18n selectors for language independence
   - Tests organization creation
   - Profile setup
   - Navigation between views

2. **Page Reload Preserves State**
   - Reloading on `/availability` works correctly
   - No JavaScript loading errors
   - Session persists across reloads

3. **Role Display - No [object Object]**
   - Settings modal shows roles correctly
   - Role badges display properly
   - No object stringification bugs

4. **Admin Workflow Complete**
   - Event creation
   - Role assignment
   - Schedule generation

5. **Language Switching Works**
   - Switch between English and Chinese
   - Translations apply immediately
   - UI updates correctly

6. **Availability CRUD Complete**
   - Add time off
   - Edit time off
   - Delete time off
   - All operations reflect in UI

7. **Setup Test Data**
   - Fixture creates test organization
   - Creates admin user for testing
   - Cleans up after tests

#### `test_phase3_features.py` (Updated for i18n)
- Database backup/restore
- Conflict detection
- Uses `data-i18n` selectors (language-independent)

## Running Tests

### All Tests
```bash
# Frontend tests
npm test

# Backend unit tests
poetry run pytest tests/unit -v

# Backend integration tests
poetry run pytest tests/integration -v

# E2E tests (requires server running)
poetry run pytest tests/e2e -v
```

### Quick Test (Pre-commit)
```bash
# Runs automatically on git commit
.git/hooks/pre-commit

# Or manually
npm test && poetry run pytest tests/unit -q
```

### Specific Test Files
```bash
# Frontend integration
npm test -- frontend/tests/integration.test.js

# SPA routing tests
poetry run pytest tests/integration/test_spa_routing_and_roles.py -v

# User workflow E2E
poetry run pytest tests/e2e/test_complete_user_workflow.py -v
```

## Bug Prevention

### Tests That Prevent Recurring Bugs

#### 1. `[object Object]` Bug
**Prevented by:**
- `frontend/tests/app-user.test.js`: Role handling tests
- `frontend/tests/integration.test.js`: Role display integration tests
- `tests/integration/test_spa_routing_and_roles.py`: Role structure validation

#### 2. SPA Routing / JavaScript Loading Errors
**Prevented by:**
- `tests/integration/test_spa_routing_and_roles.py`: All 7 tests
- `tests/e2e/test_complete_user_workflow.py`: Page reload test
- Validates absolute paths, MIME types, and route handling

#### 3. Router Authentication Issues
**Prevented by:**
- `frontend/tests/router.test.js`: Authentication-aware routing
- `frontend/tests/integration.test.js`: Router authentication integration
- Ensures `window.currentUser` is properly synchronized

#### 4. Language/Translation Issues
**Prevented by:**
- `frontend/tests/i18n.test.js`: Translation system tests
- `frontend/tests/integration.test.js`: Translation integration
- `tests/e2e/test_complete_user_workflow.py`: Language switching test
- `tests/unit/test_person_language.py`: Language persistence

## Test Strategy

### Test-First Development
1. **Write integration tests** for new features
2. **Write unit tests** for individual functions
3. **Add E2E tests** for critical user journeys
4. **Run tests before committing** (automated via pre-commit hook)

### Coverage Goals
- **Critical paths**: 100% coverage with E2E tests
- **Business logic**: 100% coverage with unit tests
- **UI components**: Integration tests for all user interactions
- **API endpoints**: Integration tests for all routes

### When Tests Catch Bugs
1. **Analyze root cause**: Why did tests miss this?
2. **Add regression test**: Specific test for this bug
3. **Improve coverage**: Related scenarios that might break
4. **Update strategy**: Prevent similar bugs in future

## Continuous Improvement

### Recent Additions
✅ Frontend integration tests (13 tests)
✅ SPA routing integration tests (7 tests)
✅ E2E user workflow tests (7 tests)
✅ i18n selector updates for language independence

### Next Steps
- [ ] Visual regression tests (screenshot comparison)
- [ ] Performance tests (load time, API response time)
- [ ] Accessibility tests (WCAG compliance)
- [ ] Mobile responsiveness tests
- [ ] Cross-browser E2E tests

## Test Maintenance

### Pre-commit Hook
Located at `.git/hooks/pre-commit`:
- Runs frontend tests (fast)
- Runs backend unit tests (fast)
- Blocks commit if tests fail
- ~5-8 seconds total execution time

### CI/CD Integration (Future)
```yaml
# .github/workflows/test.yml
- Unit tests on PR
- Integration tests on merge
- E2E tests on staging deploy
- Coverage reports
```

## Debugging Failed Tests

### Frontend Test Failures
```bash
# Run with debug output
npm test -- --verbose

# Run single test file
npm test -- frontend/tests/integration.test.js

# Check browser console (for E2E)
# Tests will show console errors in output
```

### Backend Test Failures
```bash
# Verbose output
poetry run pytest tests/integration/test_spa_routing_and_roles.py -vv

# Show print statements
poetry run pytest tests/unit/test_people.py -s

# Run single test
poetry run pytest tests/unit/test_people.py::test_create_person -v
```

### Common Issues
1. **Server not running**: E2E tests require server at localhost:8001
2. **Database state**: Integration tests may need clean database
3. **Cached files**: Frontend tests may need `npm test -- --clearCache`
4. **Async timing**: E2E tests may need longer `wait_for_timeout`

## Success Metrics

### Test Health Indicators
- ✅ All tests passing
- ✅ No flaky tests (consistent results)
- ✅ Fast execution (< 10s for pre-commit)
- ✅ Clear error messages
- ✅ Good coverage of critical paths

### Current Status
- **Frontend**: 50/50 tests passing ✅
- **Backend Unit**: 159/159 tests passing ✅
- **Backend Integration**: 7/7 tests passing ✅
- **Total**: 216/216 tests passing ✅

**Last Updated**: 2025-10-07
**Test Suite Health**: 🟢 Excellent
