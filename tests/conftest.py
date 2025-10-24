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


@pytest.fixture
def auth_headers():
    """
    Provide authentication headers for test requests.

    Since get_current_admin_user and get_current_user are mocked via dependency overrides,
    the actual token value doesn't matter - just needs to be present.
    """
    return {"Authorization": "Bearer test_token"}


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


# Database session fixture for integration tests
@pytest.fixture(scope="function")
def db():
    """Provide a database session for integration tests."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Helper functions for creating test data
def create_test_org(db):
    """Create a test organization."""
    from api.models import Organization
    from datetime import datetime
    import time
    import random

    # Add random component to prevent timestamp collisions
    rand_suffix = random.randint(1000, 9999)
    timestamp = int(time.time() * 1000)  # Use milliseconds for better uniqueness
    org_id = f"test_org_{timestamp}_{rand_suffix}"

    org = Organization(
        id=org_id,
        name="Test Organization",
        region="US",
        config={}
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def create_test_user(db, org_id, roles=None, email=None):
    """Create a test user/person."""
    from api.models import Person
    from api.security import hash_password
    from datetime import datetime
    import time
    import random

    if roles is None:
        roles = ["volunteer"]

    if email is None:
        # Add random component to prevent timestamp collisions
        rand_suffix = random.randint(1000, 9999)
        timestamp = int(time.time() * 1000)  # Use milliseconds for better uniqueness
        email = f"test_{timestamp}_{rand_suffix}@test.com"

    # Generate person ID in the same format as auth.py
    person_id = f"person_{email.split('@')[0]}_{int(time.time())}_{random.randint(1000, 9999)}"

    person = Person(
        id=person_id,
        org_id=org_id,
        name="Test User",
        email=email,
        password_hash=hash_password("TestPassword123!"),
        roles=roles
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@pytest.fixture(scope="function")
def client(db):
    """FastAPI TestClient for integration tests."""
    from fastapi.testclient import TestClient
    from api.main import app
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_db(db):
    """Alias for db fixture to match test naming."""
    return db


@pytest.fixture(scope="function")
def test_org_setup(db):
    """
    Setup test organization and users for comprehensive tests.

    Creates:
    - Organization with ID "test_org"
    - Test admin user
    - Test volunteer user

    Returns:
        dict: {"org": Organization, "admin": Person, "volunteer": Person}
    """
    from api.models import Organization, Person
    from api.security import hash_password

    # Check if test_org already exists
    org = db.query(Organization).filter(Organization.id == "test_org").first()
    if not org:
        # Create test organization with fixed ID
        org = Organization(
            id="test_org",
            name="Test Organization",
            region="US",
            config={}
        )
        db.add(org)
        db.flush()

    # Check if admin user already exists
    admin = db.query(Person).filter(Person.id == "test_admin").first()
    if not admin:
        admin = Person(
            id="test_admin",
            org_id="test_org",
            name="Test Admin",
            email="admin@test.com",
            password_hash=hash_password("password"),
            roles=["admin"]
        )
        db.add(admin)

    # Check if volunteer user already exists
    volunteer = db.query(Person).filter(Person.id == "test_volunteer").first()
    if not volunteer:
        volunteer = Person(
            id="test_volunteer",
            org_id="test_org",
            name="Test Volunteer",
            email="volunteer@test.com",
            password_hash=hash_password("password"),
            roles=["volunteer"]
        )
        db.add(volunteer)

    db.commit()
    db.refresh(org)
    db.refresh(admin)
    db.refresh(volunteer)

    return {"org": org, "admin": admin, "volunteer": volunteer}
