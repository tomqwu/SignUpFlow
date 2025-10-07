# Test Strategy for Rostio

## Problem Analysis: Why We Missed Broken Features

### Root Cause Analysis

During the i18n implementation, we broke several features that weren't caught until manual testing:

1. **[object Object] Bug** - HTML tried to display nested auth.login object
2. **Language Not Persisting** - Language preference reset on refresh
3. **Hardcoded English Text** - Many strings still in English after "completion"
4. **Modal Titles/Buttons** - Dynamic content not translated

### Why Tests Didn't Catch These Issues

1. **No Frontend Unit Tests**
   - `frontend/js/app-user.js` has 2,600+ lines with ZERO tests
   - `frontend/js/i18n.js` translation logic untested
   - No tests for translatePage() function
   - No tests for modal state changes

2. **Limited E2E Coverage**
   - Only 4 GUI tests (now 1 passing, 3 skipped)
   - No tests for language switching workflow
   - No tests for i18n attribute rendering
   - No tests for localStorage persistence

3. **No Integration Tests for New Features**
   - Added i18n but didn't write tests FIRST
   - No test for "can user change language and see Chinese"
   - No test for "language persists after refresh"
   - No test for "all visible text is translated"

4. **Test-After Approach**
   - We wrote code first, tested manually, then moved on
   - Tests were written for old features, not new changes
   - No automated regression prevention

## Test Strategy Going Forward

### Principle: Test-First Development

**BEFORE implementing any feature:**

1. Write failing tests that describe the expected behavior
2. Implement the feature
3. Run tests - they should pass
4. Refactor if needed
5. Tests prevent regression

### Test Coverage Matrix

```
Feature Type          | Unit Tests | Integration Tests | E2E Tests | API Tests
----------------------|------------|-------------------|-----------|----------
Backend API           |    ✅      |       ✅         |    ⚠️     |    ✅
Frontend Logic        |    ❌      |       ❌         |    ⚠️     |    N/A
UI Components         |    ❌      |       ❌         |    ⚠️     |    N/A
Database Operations   |    ✅      |       ✅         |    ❌     |    ✅
User Workflows        |    ❌      |       ⚠️         |    ⚠️     |    ⚠️

Legend: ✅ Good | ⚠️ Partial | ❌ Missing
```

### Required Tests for New Features

#### 1. Backend Features (API Changes)

**MUST HAVE:**
- Unit tests for new endpoints
- Schema validation tests
- Database operation tests
- Error handling tests

**Example: Adding language field to Person**
```python
def test_person_language_field():
    """Test that language field is saved and retrieved"""
    person = create_person(name="Test", language="zh-CN")
    assert person.language == "zh-CN"

    # Retrieve from database
    retrieved = get_person(person.id)
    assert retrieved.language == "zh-CN"
```

#### 2. Frontend Features (UI/Logic Changes)

**MUST HAVE:**
- Unit tests for new JavaScript functions
- Integration tests for user workflows
- E2E tests for critical paths

**Example: Language Switching**
```javascript
describe('i18n', () => {
  test('translatePage translates all data-i18n elements', () => {
    document.body.innerHTML = '<div data-i18n="common.hello">Hello</div>';
    i18n.setLocale('zh-CN');
    translatePage();
    expect(document.querySelector('[data-i18n]').textContent).toBe('你好');
  });

  test('language persists in localStorage', () => {
    i18n.setLocale('zh-CN');
    expect(localStorage.getItem('roster_user')).toContain('zh-CN');
  });
});
```

#### 3. Full-Stack Features (Backend + Frontend)

**MUST HAVE:**
- API tests
- Integration tests
- E2E tests for complete workflow

**Example: Language Preference Workflow**
```python
def test_language_preference_workflow(authenticated_page):
    """Test complete language change workflow"""
    # 1. Login
    page.goto('/login')
    login(page, 'user@test.com', 'password')

    # 2. Change language to Chinese
    page.click('[data-testid="settings-button"]')
    page.select_option('#settings-language', 'zh-CN')
    page.click('button:has-text("Save")')

    # 3. Verify UI is in Chinese
    assert page.locator('h1').text_content() == '我的日程'

    # 4. Refresh page
    page.reload()

    # 5. Verify language persisted
    assert page.locator('h1').text_content() == '我的日程'

    # 6. Verify backend stored it
    response = requests.get(f'/api/people/{user_id}')
    assert response.json()['language'] == 'zh-CN'
```

### Testing Checklist for Every Feature

Before marking a feature "complete", verify:

- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] E2E test for happy path
- [ ] Error cases tested
- [ ] Edge cases considered
- [ ] Manual testing performed
- [ ] No hardcoded values in tests
- [ ] Tests use dynamic test data
- [ ] Tests clean up after themselves

## Specific Gaps to Address

### 1. Frontend Testing Infrastructure (HIGH PRIORITY)

**Current State:** No frontend unit tests exist

**Action Items:**
- [ ] Set up Jest for JavaScript testing
- [ ] Add frontend test runner to CI
- [ ] Write tests for i18n.js
- [ ] Write tests for app-user.js core functions
- [ ] Write tests for router.js
- [ ] Add test coverage reporting

**Implementation:**
```bash
# Install Jest
npm install --save-dev jest @testing-library/dom

# Create frontend/tests/i18n.test.js
# Create frontend/tests/router.test.js
# Create frontend/tests/app-user.test.js

# Add to package.json
"scripts": {
  "test": "jest",
  "test:watch": "jest --watch",
  "test:coverage": "jest --coverage"
}
```

### 2. E2E Test Coverage (MEDIUM PRIORITY)

**Current State:** 1 passing GUI test, 3 skipped

**Action Items:**
- [ ] Update skipped GUI tests for i18n selectors
- [ ] Add test: language switching workflow
- [ ] Add test: form submission with validation
- [ ] Add test: calendar export workflow
- [ ] Add test: blocked dates integration

### 3. Visual Regression Testing (LOW PRIORITY)

**Current State:** No visual testing

**Action Items:**
- [ ] Add Playwright visual comparison
- [ ] Capture baseline screenshots
- [ ] Test: UI in English
- [ ] Test: UI in Chinese
- [ ] Test: Mobile responsive views

## Test Automation Strategy

### Pre-Commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Running tests before commit..."

# Run fast unit tests
npm run test
if [ $? -ne 0 ]; then
  echo "❌ Frontend unit tests failed"
  exit 1
fi

# Run backend unit tests (fast)
poetry run pytest tests/ -m "not slow" --tb=short
if [ $? -ne 0 ]; then
  echo "❌ Backend tests failed"
  exit 1
fi

echo "✅ All tests passed"
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Backend Tests
        run: poetry run pytest tests/ -v

      - name: Run Frontend Tests
        run: npm test

      - name: Run E2E Tests
        run: poetry run pytest tests/comprehensive_test_suite.py -v

      - name: Generate Coverage Report
        run: |
          poetry run pytest --cov=api --cov-report=html
          npm run test:coverage
```

## Test Data Strategy

### Problem: Hardcoded Test IDs

**Before:**
```python
person_id = "person_jane_1759550943"  # ❌ Breaks when data changes
```

**After:**
```python
# ✅ Query for data
people_resp = requests.get(f"{API_BASE}/people/?org_id=test_org")
person_id = people_resp.json()["people"][0]["id"]
```

### Use Fixtures and Factories

```python
@pytest.fixture
def test_person(db):
    """Create a test person for use in tests"""
    person = Person(
        id=f"test_person_{uuid.uuid4()}",
        name="Test User",
        email="test@example.com",
        org_id="test_org",
        language="en"
    )
    db.add(person)
    db.commit()
    yield person
    db.delete(person)
    db.commit()
```

## Metrics to Track

1. **Test Coverage**: Aim for >80% code coverage
2. **Test Speed**: Unit tests <1s, Integration tests <10s, E2E tests <60s
3. **Test Reliability**: 0 flaky tests
4. **Feature Completeness**: Every feature has tests before deployment

## When to Write Tests

### Always Write Tests For:
- New API endpoints
- New database models/fields
- New UI components
- Bug fixes (regression tests)
- Critical user workflows
- Data transformations
- Authentication/authorization

### Can Skip Tests For:
- One-off scripts
- Prototypes marked as experimental
- Simple configuration files
- Documentation

## Lessons Learned from i18n Implementation

### What Went Wrong:
1. ❌ Implemented i18n without tests
2. ❌ Didn't test language persistence workflow
3. ❌ Didn't test all UI states (modals, dynamic content)
4. ❌ Relied on manual testing only
5. ❌ No automated way to catch regressions

### What Should Have Happened:
1. ✅ Write E2E test: "User changes language to Chinese, sees Chinese text"
2. ✅ Write integration test: "Language saved to database"
3. ✅ Write unit test: "translatePage() translates all elements"
4. ✅ Write unit test: "Modal text updates with language"
5. ✅ Run tests before marking feature complete
6. ✅ Tests catch issues immediately

### Moving Forward:

**For every feature, ask:**
1. What tests would have caught this bug?
2. How can I test this automatically?
3. What edge cases exist?
4. Can this feature break existing functionality?
5. Is there a happy path E2E test?

## Testing Tools Setup

### Backend Testing (Already Set Up)
- ✅ pytest
- ✅ FastAPI TestClient
- ✅ SQLAlchemy test database
- ✅ Playwright for E2E

### Frontend Testing (TO DO)
- [ ] Jest for JavaScript unit tests
- [ ] Testing Library for DOM testing
- [ ] Mock Service Worker for API mocking
- [ ] Coverage reporting

### Test Commands

```bash
# Run all tests
make test

# Run backend only
poetry run pytest tests/

# Run frontend only (once set up)
npm test

# Run E2E only
poetry run pytest tests/comprehensive_test_suite.py

# Run with coverage
poetry run pytest --cov=api --cov-report=html
npm run test:coverage

# Watch mode for development
npm run test:watch
```

## Summary

**The Problem:** We implemented features without comprehensive tests, relying on manual testing by a one-person team. This is unsustainable and error-prone.

**The Solution:** Test-first development with proper test coverage:
- Unit tests for logic
- Integration tests for workflows
- E2E tests for critical paths
- Automated test runs before commits
- No feature is "done" until tests pass

**Immediate Actions:**
1. Set up Jest for frontend testing
2. Write tests for existing i18n functionality
3. Write E2E test for language switching
4. Add pre-commit test hook
5. Never implement features without tests again

**Long-term Goal:** Every feature has automated tests that prevent regression, allowing you to ship confidently without extensive manual testing.
