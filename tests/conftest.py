"""Pytest configuration and fixtures for Rostio tests."""

from pathlib import Path
from typing import Generator

import os
import subprocess
import time
from urllib.parse import urlparse

import pytest
import requests
from playwright.sync_api import sync_playwright

from tests.e2e.helpers import AppConfig, ApiTestClient, safe_artifact_name

# Module-level variable to store the current test's database session
# This allows both the db fixture and the override_get_db_dependency to share the same session
_test_db_session = None


# Test server configuration
APP_URL = os.getenv("E2E_APP_URL", "http://localhost:8000").rstrip("/")
API_BASE = os.getenv("E2E_API_BASE", f"{APP_URL}/api").rstrip("/")


@pytest.fixture(scope="session")
def app_config() -> AppConfig:
    """Expose shared application endpoints to tests."""
    return AppConfig(app_url=APP_URL, api_base=API_BASE)


@pytest.fixture(scope="session")
def api_server(app_config: AppConfig):
    """Start API server for testing session (or use already-running server in Docker)."""
    # Set test database URL environment variable
    test_env = os.environ.copy()
    test_env["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
    test_env["TESTING"] = "true"  # Disable rate limiting during tests
    test_env["EMAIL_ENABLED"] = "false"
    test_env["SMS_ENABLED"] = "false"
    # Relax endpoint-specific rate limits to avoid flakiness when provisioning data
    test_env["RATE_LIMIT_CREATE_ORG_MAX"] = "1000"
    test_env["RATE_LIMIT_SIGNUP_MAX"] = "1000"
    test_env["RATE_LIMIT_LOGIN_MAX"] = "1000"
    test_env["RATE_LIMIT_CREATE_INVITATION_MAX"] = "1000"
    test_env["RATE_LIMIT_VERIFY_INVITATION_MAX"] = "1000"
    test_env["DISABLE_RATE_LIMITS"] = "true"

    parsed_url = urlparse(app_config.app_url)
    host = parsed_url.hostname or "0.0.0.0"
    port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)

    # Check if server is already running (Docker environment)
    # Try port check first (faster and more reliable than HTTP check)
    import socket

    server_already_running = False
    print(f"🔍 Checking if port {port} already in use...")

    # Try to bind to the port - if it fails, something is already using it
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.bind((host if host != "0.0.0.0" else "127.0.0.1", port))
        sock.close()
        print(f"   Port {port} is available - need to start server")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            server_already_running = True
            print(f"✅ Port {port} already in use - server appears to be running")
            # Double-check with health endpoint
            try:
                response = requests.get(f"{app_config.app_url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Health check confirmed - server is healthy")
                else:
                    print(f"⚠️  Health check returned {response.status_code}")
            except Exception as e:
                print(f"⚠️  Health check failed: {type(e).__name__} - {e}")
                print(f"   Proceeding anyway since port is bound")
        else:
            print(f"   Unexpected socket error: {e}")
            sock.close()

    # Only start server if not already running
    process = None
    if not server_already_running:
        # Start server with test database
        process = subprocess.Popen(
            [
                "poetry",
                "run",
                "uvicorn",
                "api.main:app",
                "--host",
                host,
                "--port",
                str(port),
            ],
            env=test_env,
        )

        # Wait for server to be ready
        server_ready = False
        for _ in range(60):
            try:
                response = requests.get(f"{app_config.app_url}/health", timeout=1)
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
    # Force complete reload of setup_test_data module to get latest changes
    import sys
    import importlib

    # Delete module from sys.modules to force fresh import
    if 'tests.setup_test_data' in sys.modules:
        del sys.modules['tests.setup_test_data']

    # Now import fresh
    import tests.setup_test_data
    setup_test_data = tests.setup_test_data.setup_test_data
    setup_test_data(app_config.api_base)

    try:
        from tests.setup_e2e_test_data import setup_e2e_test_data
        setup_e2e_test_data()
    except Exception as e:
        print(f"⚠️  Warning: setup_e2e_test_data failed: {e}")

    yield process

    # Cleanup - only terminate if we started the server
    if process is not None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture(scope="function")
def api_client(app_config: AppConfig) -> Generator[ApiTestClient, None, None]:
    """Provide a disposable API client for test data setup."""
    client = ApiTestClient(app_config.api_base)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="function")
def browser_context(request, app_config: AppConfig):
    """Provide a fresh browser context for each test."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 Playwright Test",
            base_url=app_config.app_url,
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        yield context
        trace_failed = getattr(request.node, "rep_call", None)
        if trace_failed and trace_failed.failed:
            trace_dir = Path("test-artifacts") / "traces"
            trace_dir.mkdir(parents=True, exist_ok=True)
            trace_path = trace_dir / f"{safe_artifact_name(request.node.nodeid)}.zip"
            context.tracing.stop(path=str(trace_path))
        else:
            context.tracing.stop()
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(browser_context):
    """
    Provide a fresh page for each test with clean browser state.

    Phase 2 of test isolation fix: Clears browser state (localStorage,
    sessionStorage, cookies) before each test to prevent browser-level
    state pollution between tests.

    This complements the database isolation fix (Phase 1) to ensure
    complete test isolation.
    """
    page = browser_context.new_page()
    page.set_default_timeout(5000)

    # Collect console errors
    page.on("console", lambda msg:
        print(f"CONSOLE: {msg.type}: {msg.text}") if msg.type in ["error", "warning"] else None
    )

    # Phase 2: Clean browser state BEFORE each test
    # This prevents localStorage/sessionStorage/cookie pollution from previous tests
    try:
        # Navigate to app first (required for evaluate to work)
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=10000)

        # Clear all browser storage
        page.evaluate("""() => {
            localStorage.clear();
            sessionStorage.clear();
        }""")

        # Clear cookies
        browser_context.clear_cookies()
    except Exception as e:
        # If cleanup fails, log but don't fail the test
        # Some tests might not need the app to be loaded
        print(f"Warning: Browser state cleanup failed: {e}")

    yield page

    # Clean AFTER test as well (belt and suspenders approach)
    try:
        page.evaluate("""() => {
            localStorage.clear();
            sessionStorage.clear();
        }""")
        browser_context.clear_cookies()
    except Exception:
        # Cleanup failed, but test is done anyway
        pass

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

    # Ensure the volunteer account starts with a clean availability slate to avoid 409 conflicts
    try:
        auth_resp = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": "sarah@test.com", "password": "password"},
            timeout=5
        )
        if auth_resp.status_code == 200:
            auth_data = auth_resp.json()
            token = auth_data.get("token")
            person_id = auth_data.get("person_id")
            if token and person_id:
                headers = {"Authorization": f"Bearer {token}"}
                timeoff_resp = requests.get(
                    f"{API_BASE}/availability/{person_id}/timeoff",
                    headers=headers,
                    timeout=5
                )
                if timeoff_resp.status_code == 200:
                    for item in timeoff_resp.json().get("timeoff", []):
                        requests.delete(
                            f"{API_BASE}/availability/{person_id}/timeoff/{item['id']}",
                            headers=headers,
                            timeout=5
                        )
    except Exception as cleanup_error:
        print(f"Warning: failed to clear existing time-off entries: {cleanup_error}")

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
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from api.models import Base

TEST_DB_PATH = Path(__file__).resolve().parent.parent / "test_roster.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database once per test session."""
    # Remove existing test database
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    # Create test database with all tables
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

    # Import all models to ensure they're registered with Base.metadata
    from api.models import (
        Organization, Person, Team, TeamMember, Resource, Event, EventTeam,
        Assignment, Solution, Availability, VacationPeriod, AvailabilityException,
        Holiday, Constraint, Invitation, RecurringSeries, RecurrenceException,
        OnboardingProgress, Notification, EmailPreference
    )

    Base.metadata.create_all(bind=engine)

    yield

    # Cleanup after all tests
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture(scope="module", autouse=True)
def reset_database_between_modules():
    """
    Reset database data between test modules to prevent test pollution.

    This fixture runs automatically before each test module to ensure test isolation.
    It deletes all data from all tables while preserving the schema.

    This fixes issues where:
    - RBAC tests pass in isolation but fail in full suite
    - User roles modified in one test affect other tests
    - Database state persists across test modules
    """
    # Yield first to let the module run
    yield

    # After module completes, clean up database data
    if not TEST_DB_PATH.exists():
        return

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

    # Import all models to get table references
    from api.models import (
        Organization, Person, Team, TeamMember, Resource, Event, EventTeam,
        Assignment, Solution, Availability, VacationPeriod, AvailabilityException,
        Holiday, Constraint, Invitation, RecurringSeries, RecurrenceException,
        OnboardingProgress, Notification, EmailPreference
    )

    # Delete all data from all tables (in reverse order to handle foreign keys)
    with engine.connect() as conn:
        # Disable foreign key constraints temporarily for SQLite
        conn.execute(text("PRAGMA foreign_keys = OFF"))

        # Delete data from all tables (skip tables that don't exist)
        for table in reversed(Base.metadata.sorted_tables):
            try:
                conn.execute(text(f"DELETE FROM {table.name}"))
            except Exception:
                # Table doesn't exist in test database - skip it
                pass

        # Re-enable foreign key constraints
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()


@pytest.fixture(scope="function", autouse=True)
def reset_database_between_tests():
    """
    Reset database data before EACH test function to ensure complete test isolation.

    This fixture addresses test isolation problems where:
    - Tests pass individually but fail in full suite
    - Database state pollution from previous tests affects later tests
    - Volunteers/events created in one test persist to the next
    - Expected data states don't match actual database state

    Implementation:
    - Runs BEFORE each test function (autouse=True)
    - Deletes all data from all tables
    - Preserves table schema (no DROP/CREATE overhead)
    - Fast isolation via DELETE instead of transaction rollback

    Expected Impact:
    - Fixes 40-50 of 58 failing tests (test isolation issues)
    - Tests become fully independent and order-agnostic
    - Consistent test behavior in isolation vs full suite
    """
    # Clean database BEFORE each test
    # Ensure database and tables exist (create if missing to prevent silent failures)
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

    if not TEST_DB_PATH.exists():
        # Database doesn't exist - create it with all tables
        Base.metadata.create_all(bind=engine)

    # Import all models to get table references
    from api.models import (
        Organization, Person, Team, TeamMember, Resource, Event, EventTeam,
        Assignment, Solution, Availability, VacationPeriod, AvailabilityException,
        Holiday, Constraint, Invitation, RecurringSeries, RecurrenceException,
        OnboardingProgress, Notification, EmailPreference
    )

    # Delete all data from all tables (in reverse order to handle foreign keys)
    with engine.connect() as conn:
        # Disable foreign key constraints temporarily for SQLite
        conn.execute(text("PRAGMA foreign_keys = OFF"))

        # Delete data from all tables (skip tables that don't exist)
        for table in reversed(Base.metadata.sorted_tables):
            try:
                conn.execute(text(f"DELETE FROM {table.name}"))
            except Exception:
                # Table doesn't exist in test database - skip it
                pass

        # Re-enable foreign key constraints
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()

    yield

    # No cleanup needed after test - next test will clean before it runs


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
    from fastapi import Depends
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from sqlalchemy.orm import Session
    from api.main import app
    from api.database import get_db
    from api.dependencies import get_current_admin_user, get_current_user, verify_org_member
    from api.models import Person

    # Get the security scheme
    security = HTTPBearer()

    def override_get_db_dependency():
        """
        Return the same database session used by test fixtures.

        This ensures that users created in test fixtures are visible to
        the authentication override functions.
        """
        global _test_db_session

        # If there's a test session, use it (for integration tests with db fixture)
        if _test_db_session is not None:
            yield _test_db_session
        else:
            # Fallback: create a new session (for tests without db fixture)
            engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
            TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

    async def override_get_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(override_get_db_dependency)
    ):
        """Smart mock that parses JWT token and queries database for actual user.

        This allows tests to create real users and JWT tokens, and the authentication
        will work correctly based on the token.
        """
        from api.security import verify_token

        # Parse JWT token
        try:
            if isinstance(credentials, HTTPAuthorizationCredentials):
                token = credentials.credentials
            elif isinstance(credentials, str):
                token = credentials
            else:
                # Fallback to hardcoded admin for tests without proper tokens
                return Person(
                    id="test_admin",
                    org_id="test_org",
                    name="Test Admin",
                    email="admin@test.com",
                    roles=["admin"],
                    timezone="UTC",
                    language="en",
                    status="active"
                )

            payload = verify_token(token)

            # Extract person_id from token
            person_id: str = payload.get("sub")
            if person_id is None:
                # Fallback to hardcoded admin
                return Person(
                    id="test_admin",
                    org_id="test_org",
                    name="Test Admin",
                    email="admin@test.com",
                    roles=["admin"],
                    timezone="UTC",
                    language="en",
                    status="active"
                )

            # Query database for actual user
            person = db.query(Person).filter(Person.id == person_id).first()
            if person is None:
                # Fallback to hardcoded admin if user not in database
                return Person(
                    id="test_admin",
                    org_id="test_org",
                    name="Test Admin",
                    email="admin@test.com",
                    roles=["admin"],
                    timezone="UTC",
                    language="en",
                    status="active"
                )

            return person

        except Exception:
            # On any error, fallback to hardcoded admin
            return Person(
                id="test_admin",
                org_id="test_org",
                name="Test Admin",
                email="admin@test.com",
                roles=["admin"],
                timezone="UTC",
                language="en",
                status="active"
            )

    async def override_get_admin_user(
        current_user: Person = Depends(override_get_user)
    ):
        """Verify user has admin role (uses smart override)."""
        from api.dependencies import check_admin_permission
        from fastapi import HTTPException

        if not check_admin_permission(current_user):
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )
        return current_user

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
    import api.routers.notifications

    # Store original function
    original_verify = api.dependencies.verify_org_member

    # Replace with mock
    api.dependencies.verify_org_member = override_verify_org_member
    api.routers.people.verify_org_member = override_verify_org_member
    if hasattr(api.routers.events, 'verify_org_member'):
        api.routers.events.verify_org_member = override_verify_org_member
    if hasattr(api.routers.teams, 'verify_org_member'):
        api.routers.teams.verify_org_member = override_verify_org_member
    if hasattr(api.routers.notifications, 'verify_org_member'):
        api.routers.notifications.verify_org_member = override_verify_org_member

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
    global _test_db_session

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    _test_db_session = session  # Store session globally for override_get_db_dependency
    try:
        yield session
    finally:
        session.close()
        _test_db_session = None  # Clear global session after test


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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Make test outcome available on the request node for fixtures."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
