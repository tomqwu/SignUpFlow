# Comprehensive Testing Plan

This document outlines the complete testing strategy for the Roster scheduling application.

## Test Structure

```
tests/
├── unit/                  # Unit tests for individual components
│   ├── test_auth.py      # Authentication endpoints
│   ├── test_organizations.py
│   ├── test_people.py
│   ├── test_events.py
│   ├── test_availability.py
│   ├── test_solver.py
│   └── test_solutions.py
│
├── integration/           # Integration tests for workflows
│   ├── test_user_journey.py
│   ├── test_admin_workflow.py
│   └── test_schedule_generation.py
│
├── gui/                   # GUI/Frontend tests
│   ├── test_login_flow.py
│   ├── test_admin_dashboard.py
│   ├── test_user_features.py
│   └── test_export_features.py
│
└── e2e/                   # End-to-end tests
    ├── test_complete_flow.py
    └── test_export_workflow.py
```

## Unit Tests (Per Feature)

### 1. Authentication (`test_auth.py`)
- [x] `test_signup_success` - Create account with valid data
- [x] `test_signup_duplicate_email` - Reject duplicate email
- [x] `test_signup_invalid_org` - Fail with bad org ID
- [x] `test_login_success` - Login with correct credentials
- [x] `test_login_wrong_password` - Reject wrong password
- [x] `test_login_nonexistent_user` - Reject unknown email
- [ ] `test_password_hashing` - Verify passwords are hashed
- [ ] `test_token_generation` - Token is generated on login

### 2. Organizations (`test_organizations.py`)
- [ ] `test_create_organization` - Create org with valid data
- [ ] `test_create_duplicate_org` - Reject duplicate org ID
- [ ] `test_list_organizations` - Get all orgs
- [ ] `test_get_organization` - Get single org by ID
- [ ] `test_get_nonexistent_org` - 404 for missing org
- [ ] `test_update_organization` - Update org details
- [ ] `test_delete_organization` - Delete org (cascade)

### 3. People (`test_people.py`)
- [ ] `test_create_person` - Create person with roles
- [ ] `test_create_person_no_email` - Allow null email
- [ ] `test_list_people` - Get all people in org
- [ ] `test_list_people_filtered` - Filter by role
- [ ] `test_get_person` - Get person by ID
- [ ] `test_update_person` - Update person roles
- [ ] `test_delete_person` - Delete person

### 4. Events (`test_events.py`)
- [ ] `test_create_event` - Create event with all fields
- [ ] `test_create_event_minimal` - Create with required fields only
- [ ] `test_list_events` - Get all events for org
- [ ] `test_list_events_date_range` - Filter by date
- [ ] `test_get_event` - Get single event
- [ ] `test_update_event` - Update event details
- [ ] `test_delete_event` - Delete event

### 5. Availability (`test_availability.py`)
- [ ] `test_add_timeoff` - Add time-off period
- [ ] `test_add_timeoff_invalid_dates` - Reject end before start
- [ ] `test_list_timeoff` - Get all time-off periods
- [ ] `test_delete_timeoff` - Remove time-off period
- [ ] `test_overlapping_timeoff` - Handle overlapping periods

### 6. Solver (`test_solver.py`)
- [ ] `test_generate_schedule` - Generate solution
- [ ] `test_solver_no_events` - Handle no events gracefully
- [ ] `test_solver_no_people` - Handle no people gracefully
- [ ] `test_solver_constraints` - Respect time-off constraints
- [ ] `test_solver_role_matching` - Match people to event roles

### 7. Solutions (`test_solutions.py`)
- [ ] `test_list_solutions` - Get all solutions for org
- [ ] `test_get_solution` - Get solution by ID
- [ ] `test_get_assignments` - Get assignments for solution
- [ ] `test_export_csv` - Export solution as CSV
- [ ] `test_export_ics` - Export solution as ICS (calendar)
- [ ] `test_export_no_assignments` - Error when no assignments

## Integration Tests

### 8. User Journey (`test_user_journey.py`)
- [ ] `test_signup_to_schedule` - Complete user flow:
  1. Signup
  2. Join org
  3. Set availability
  4. View assigned schedule

- [ ] `test_timeoff_respected` - Time-off blocks assignments

### 9. Admin Workflow (`test_admin_workflow.py`)
- [ ] `test_admin_create_event` - Admin creates event
- [ ] `test_admin_generate_schedule` - Admin runs solver
- [ ] `test_admin_view_assignments` - Admin views all assignments
- [ ] `test_admin_export_schedule` - Admin exports CSV

### 10. Schedule Generation (`test_schedule_generation.py`)
- [ ] `test_simple_schedule` - 2 people, 2 events
- [ ] `test_role_matching` - People assigned to matching roles only
- [ ] `test_availability_respected` - No assignments during time-off
- [ ] `test_load_balancing` - Fair distribution of assignments

## GUI Tests

### 11. Login Flow (`test_login_flow.py`)
- [ ] `test_login_page_loads` - Login form visible
- [ ] `test_login_submit` - Form submits to API
- [ ] `test_login_error_display` - Shows error message
- [ ] `test_login_redirect` - Redirects to app on success
- [ ] `test_session_persistence` - Stays logged in on refresh

### 12. Admin Dashboard (`test_admin_dashboard.py`)
- [ ] `test_admin_tab_visible` - Admin tab shows for admins
- [ ] `test_admin_tab_hidden` - Admin tab hidden for regular users
- [ ] `test_create_event_form` - Event creation form works
- [ ] `test_event_appears_in_list` - Created event shows in list
- [ ] `test_delete_event` - Delete button works
- [ ] `test_generate_schedule_button` - Generate button works
- [ ] `test_view_solution` - View/export button works

### 13. User Features (`test_user_features.py`)
- [ ] `test_calendar_loads` - Calendar view loads
- [ ] `test_calendar_shows_events` - Events appear on calendar
- [ ] `test_add_timeoff` - Time-off form works
- [ ] `test_timeoff_appears` - Added time-off shows in list
- [ ] `test_remove_timeoff` - Remove button works
- [ ] `test_schedule_view` - Schedule view shows assignments

### 14. Export Features (`test_export_features.py`)
- [ ] `test_export_calendar_button` - Export button exists
- [ ] `test_export_downloads_file` - File downloads on click
- [ ] `test_export_error_message` - Shows helpful error if no data
- [ ] `test_admin_export_csv` - Admin can export CSV
- [ ] `test_user_export_ics` - User can export ICS

## E2E Tests

### 15. Complete Flow (`test_complete_flow.py`)
- [ ] `test_full_user_journey`:
  1. Admin creates org
  2. Admin creates events
  3. Users signup
  4. Users set availability
  5. Admin generates schedule
  6. Users view their assignments
  7. Users export calendar

### 16. Export Workflow (`test_export_workflow.py`)
- [ ] `test_export_with_assignments`:
  1. Create org, people, events
  2. Generate schedule with assignments
  3. Export CSV
  4. Verify CSV contains correct data
  5. Export ICS
  6. Verify ICS is valid calendar format

## Test Commands

### Run All Tests
```bash
poetry run pytest tests/ -v
```

### Run Unit Tests Only
```bash
poetry run pytest tests/unit/ -v
```

### Run Integration Tests
```bash
poetry run pytest tests/integration/ -v
```

### Run GUI Tests
```bash
poetry run pytest tests/gui/ -v
```

### Run Specific Test File
```bash
poetry run pytest tests/unit/test_auth.py -v
```

### Run Specific Test
```bash
poetry run pytest tests/unit/test_auth.py::TestAuthSignup::test_signup_success -v
```

### Run with Coverage
```bash
poetry run pytest tests/ --cov=api --cov-report=html
```

## Current Status

### Completed ✅
- [x] Basic API tests (test_api_complete.py) - 18 tests
- [x] Basic GUI tests (test_gui_automated.py) - 7 tests
- [x] Auth unit tests (test_auth.py) - 6 tests
- [x] Export test framework (test_gui_export.py)

### To Do 📋
- [ ] Complete all unit tests for each endpoint
- [ ] Create integration tests for workflows
- [ ] Create GUI component tests
- [ ] Create end-to-end tests
- [ ] Add test fixtures for common data
- [ ] Add test coverage reporting
- [ ] Add CI/CD pipeline integration

## Test Data Strategy

### Fixtures
Create pytest fixtures for common test data:
```python
@pytest.fixture
def test_org():
    """Create a test organization."""
    return create_org("Test Org")

@pytest.fixture
def test_user(test_org):
    """Create a test user in the org."""
    return create_user(test_org, "test@test.com", "password")

@pytest.fixture
def test_events(test_org):
    """Create test events."""
    return [create_event(test_org, ...) for _ in range(3)]
```

### Cleanup
Use pytest fixtures with cleanup:
```python
@pytest.fixture(scope="function", autouse=True)
def clean_database():
    """Clean database before each test."""
    yield
    # Cleanup code here
```

## Coverage Goals

- **Unit Tests**: 90%+ coverage of all API endpoints
- **Integration Tests**: Cover all major user workflows
- **GUI Tests**: Cover all interactive features
- **E2E Tests**: Cover complete user journeys

## Next Steps

1. ✅ Create test structure (this document)
2. Create test fixtures and utilities
3. Implement all unit tests (80+ tests)
4. Implement integration tests (20+ tests)
5. Implement GUI tests (20+ tests)
6. Implement E2E tests (10+ tests)
7. Add coverage reporting
8. Set up CI/CD pipeline

**Total Target: 130+ comprehensive tests covering all features**
