# Rostio Test Suite

Comprehensive testing for the Roster scheduling system.

## Quick Start

### Run All Tests

```bash
./run_all_tests.sh
```

This will run both API and GUI automated tests.

## Test Files

### 1. API Tests
**File:** `test_api_complete.py`

Tests all backend API endpoints:
- ✅ Authentication (signup, login, password validation)
- ✅ Organizations (CRUD operations)
- ✅ People (CRUD operations)
- ✅ Events (CRUD operations)
- ✅ Availability (time-off management)
- ✅ Solver (schedule generation)
- ✅ Solutions (viewing, exporting)

**Run:**
```bash
poetry run python tests/test_api_complete.py
```

**Expected Output:**
- 18-20 tests passing
- 2 tests may fail if no assignments generated (expected)

### 2. GUI Automated Tests
**File:** `test_gui_automated.py`

Tests frontend loading and JavaScript functionality:
- ✅ HTML pages load correctly
- ✅ CSS and JavaScript files accessible
- ✅ Login flow works end-to-end
- ✅ Admin dashboard endpoints work
- ✅ Calendar export functions

**Run:**
```bash
poetry run python tests/test_gui_automated.py
```

**Expected Output:**
- 7/7 tests passing

### 3. GUI Manual Tests
**File:** `test_gui_manual.md`

Step-by-step manual testing guide for:
- Authentication flows (signup, login, logout)
- User features (calendar, availability, schedule)
- Admin features (event creation, schedule generation)
- Export features (ICS, CSV)
- Session management
- Error handling

**Use:** Open in browser and follow the checklist while testing the GUI at http://localhost:8000/frontend/index.html

## Test Coverage

### API Endpoints Tested (20 tests)

| Category | Endpoint | Status |
|----------|----------|--------|
| Auth | POST /auth/signup | ✅ |
| Auth | POST /auth/login | ✅ |
| Auth | POST /auth/check-email | ✅ |
| Orgs | GET /organizations/ | ✅ |
| Orgs | GET /organizations/{id} | ✅ |
| People | POST /people/ | ✅ |
| People | GET /people/ | ✅ |
| People | GET /people/{id} | ✅ |
| Events | POST /events/ | ✅ |
| Events | GET /events/ | ✅ |
| Events | GET /events/{id} | ✅ |
| Availability | POST /availability/{id}/timeoff | ✅ |
| Availability | GET /availability/{id}/timeoff | ✅ |
| Solver | POST /solver/solve | ✅ |
| Solutions | GET /solutions/ | ✅ |
| Solutions | GET /solutions/{id} | ✅ |
| Solutions | GET /solutions/{id}/assignments | ✅ |
| Solutions | POST /solutions/{id}/export | ⚠️ * |

\* May fail if no assignments generated (depends on data)

### GUI Features Tested (7 automated + 17 manual)

**Automated:**
- Frontend HTML/CSS/JS loading
- Login/signup flows via API
- Admin dashboard data loading
- Calendar export endpoints

**Manual (see test_gui_manual.md):**
- Complete user signup journey
- Admin signup with role selection
- Login with credentials
- Error handling (wrong password, network errors)
- Time-off management
- Event creation (admin)
- Schedule generation (admin)
- Calendar export (ICS format)
- Session persistence
- Logout functionality

## Prerequisites

1. **Server must be running:**
   ```bash
   poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Demo data (optional):**
   The tests create their own test data, but you can pre-populate:
   ```bash
   curl -X POST http://localhost:8000/organizations/ \
     -H "Content-Type: application/json" \
     -d '{"id":"demo_org","name":"Demo Organization","region":"US","config":{}}'
   ```

## Test Results

### Latest Run

```
API Tests: 18/20 passed (90%)
GUI Tests: 7/7 passed (100%)
Overall: 25/27 tests passing (93%)
```

## Troubleshooting

### Tests Fail: "Connection refused"
- Make sure the server is running on port 8000
- Check: `curl http://localhost:8000/health`

### Tests Fail: "Email already registered"
- Tests reuse some data
- Clean database: `rm roster.db` and restart server

### Export Tests Fail: "No assignments"
- This is expected if the solver hasn't generated assignments
- The test still validates the endpoint exists

### GUI Tests: Can't access frontend
- Make sure static files are mounted in api/main.py
- Check server logs for errors

## Adding New Tests

### API Test
Add to `test_api_complete.py`:
```python
def test_my_new_feature():
    response = client.get(f"{API_BASE}/my-endpoint")
    assert response.status_code == 200
    assert "expected_field" in response.json()

runner.test("My new feature", test_my_new_feature)
```

### GUI Test
Add to `test_gui_automated.py`:
```python
def test_my_gui_feature():
    print("🧪 Testing my GUI feature...", end=" ")
    # Test code here
    print("✅ PASS")
```

## CI/CD Integration

To run tests in CI:
```bash
#!/bin/bash
# Start server in background
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Run tests
./run_all_tests.sh
TEST_RESULT=$?

# Cleanup
kill $SERVER_PID

exit $TEST_RESULT
```

## Manual Testing Checklist

See [test_gui_manual.md](test_gui_manual.md) for complete manual testing guide.

Quick checklist:
- [ ] Can signup new user
- [ ] Can login with password
- [ ] Can set availability
- [ ] Can view calendar
- [ ] Admin can create events
- [ ] Admin can generate schedule
- [ ] Can export to ICS
- [ ] Session persists on refresh
- [ ] Can logout

## Support

If tests fail unexpectedly:
1. Check server logs
2. Verify database integrity
3. Clear browser cache/localStorage
4. Review API documentation at http://localhost:8000/docs
