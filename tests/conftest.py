"""Pytest configuration and fixtures for Rostio tests."""

import pytest
import subprocess
import time
import requests
from playwright.sync_api import sync_playwright

# Test server configuration
API_BASE = "http://localhost:8000/api"
APP_URL = "http://localhost:8000"


@pytest.fixture(scope="session")
def api_server():
    """Start API server for testing session."""
    import os
    # Set test database URL environment variable
    test_env = os.environ.copy()
    test_env["DATABASE_URL"] = "sqlite:///./test_roster.db"
    test_env["TESTING"] = "true"  # Disable rate limiting during tests

    # Start server with test database
    process = subprocess.Popen(
        ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"],
        env=test_env,
    )

    # Wait for server to be ready
    server_ready = False
    for _ in range(60):
        try:
            response = requests.get(f"{API_BASE.replace('/api', '')}/health", timeout=1)
            if response.status_code == 200:
                server_ready = True
                break
        except Exception:
            time.sleep(0.5)
        else:
            time.sleep(0.5)

    if not server_ready:
        process.terminate()
        raise RuntimeError("API server failed to start within timeout window")

    # Setup test data
    from tests.setup_test_data import setup_test_data
    setup_test_data()

    yield process

    # Cleanup
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture(scope="function")
def browser_context():
    """Provide a fresh browser context for each test."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 Playwright Test",
        )
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(browser_context):
    """Provide a fresh page for each test."""
    page = browser_context.new_page()

    # Collect console errors
    page.on("console", lambda msg:
        print(f"CONSOLE: {msg.type}: {msg.text}") if msg.type in ["error", "warning"] else None
    )

    yield page
    page.close()


@pytest.fixture(scope="function")
def authenticated_page(page):
    """Provide a page with authenticated user."""
    # Go to login
    page.goto(APP_URL)
    page.wait_for_load_state("networkidle")

    # Click sign in
    if page.locator('a:has-text("Sign in")').count() > 0:
        page.locator('a:has-text("Sign in")').click()
        page.wait_for_timeout(500)

    # Login
    page.fill('input[type="email"]', "sarah@test.com")
    page.fill('input[type="password"]', "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)

    yield page


@pytest.fixture(scope="function")
def admin_page(page):
    """Provide a page with admin user."""
    page.goto(APP_URL)
    page.wait_for_load_state("networkidle")

    # Click sign-in link if present
    if page.locator('a:has-text("Sign in")').count() > 0:
        page.get_by_role("link", name="Sign in").click()
        page.wait_for_timeout(500)

    # Login as admin
    page.fill('input[type="email"]', "jane@test.com")
    page.fill('input[type="password"]', "password")
    page.get_by_role("button", name="Sign In").click()

    # Wait longer for admin dashboard to fully load
    page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")

    yield page


@pytest.fixture(scope="session")
def test_data():
    """Create test data for all tests."""
    # This would be populated by setup_test_data.py
    return {
        "org_id": "test_org",
        "users": [
            {"email": "sarah@test.com", "password": "password", "name": "Sarah Johnson"},
            {"email": "john@test.com", "password": "password", "name": "John Doe"},
            {"email": "jane@test.com", "password": "password", "name": "Jane Smith"},
        ],
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    import os
    # Set TESTING environment variable to disable rate limiting
    os.environ["TESTING"] = "true"

    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "gui: GUI tests with Playwright")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


# Database test fixtures
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import Base

TEST_DATABASE_URL = "sqlite:///./test_roster.db"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database once per test session."""
    # Remove existing test database
    if os.path.exists("test_roster.db"):
        os.remove("test_roster.db")

    # Create test database with all tables
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

    # Import all models to ensure they're registered with Base.metadata
    from api.models import (
        Organization, Person, Team, TeamMember, Resource, Event, EventTeam,
        Assignment, Solution, Availability, VacationPeriod, AvailabilityException,
        Holiday, Constraint, Invitation
    )

    Base.metadata.create_all(bind=engine)

    yield

    # Cleanup after all tests
    if os.path.exists("test_roster.db"):
        os.remove("test_roster.db")


@pytest.fixture(scope="function", autouse=True)
def override_get_db():
    """Override database dependency to use test database for unit tests."""
    from api.main import app
    from api.database import get_db
    from api.dependencies import get_current_admin_user, get_current_user, verify_org_member
    from api.models import Person

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db_dependency():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    def override_get_admin_user():
        """Mock admin user for testing - bypasses authentication."""
        return Person(
            id="test_admin",
            org_id="test_org",
            name="Test Admin",
            email="admin@test.com",
            roles=["admin"]
        )

    def override_get_user():
        """Mock user for testing - returns admin user to allow unit tests to pass.

        Note: Most unit tests expect to be able to create/update/delete resources
        without permission errors, so we return an admin user here.
        """
        return Person(
            id="test_admin",
            org_id="test_org",
            name="Test Admin",
            email="admin@test.com",
            roles=["admin"]  # Admin role allows tests to pass permission checks
        )

    def override_verify_org_member(person: Person, org_id: str) -> None:
        """Mock org membership verification - bypasses org checks for testing."""
        # In tests, allow access to all orgs
        pass

    app.dependency_overrides[get_db] = override_get_db_dependency
    app.dependency_overrides[get_current_admin_user] = override_get_admin_user
    app.dependency_overrides[get_current_user] = override_get_user

    # Override verify_org_member function (not a dependency, so we monkey patch it)
    import api.routers.people
    import api.routers.events
    import api.routers.teams

    # Store original function
    original_verify = api.dependencies.verify_org_member

    # Replace with mock
    api.dependencies.verify_org_member = override_verify_org_member
    api.routers.people.verify_org_member = override_verify_org_member
    if hasattr(api.routers.events, 'verify_org_member'):
        api.routers.events.verify_org_member = override_verify_org_member
    if hasattr(api.routers.teams, 'verify_org_member'):
        api.routers.teams.verify_org_member = override_verify_org_member

    yield

    # Restore original function
    api.dependencies.verify_org_member = original_verify
    api.routers.people.verify_org_member = original_verify
    if hasattr(api.routers.events, 'verify_org_member'):
        api.routers.events.verify_org_member = original_verify
    if hasattr(api.routers.teams, 'verify_org_member'):
        api.routers.teams.verify_org_member = original_verify

    app.dependency_overrides.clear()
