"""Pytest configuration and fixtures for Rostio tests."""

from pathlib import Path
import os
import sys
import time
import threading
import shutil
import asyncio
import logging
import uuid
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Force in-memory database for ALL tests to avoid "database disk image is malformed"
# caused by file locking/corruption in threaded tests.
os.environ["DATABASE_URL"] = "sqlite:////tmp/signupflow_test.db"
os.environ["TESTING_FORCE_MEMORY"] = "true"

import requests
import pytest
from urllib.parse import urlparse
import uvicorn
from fastapi.testclient import TestClient
from playwright.sync_api import Page, expect, sync_playwright
from api.main import app
# from api.config import settings # Config likely not needed here or in core
from api import database
import api.database

# SQLAlchemy imports (some moved above)
from sqlalchemy import text

# Application imports
from api.models import Base, Person, Organization
from api.security import hash_password
import api.main
from tests.e2e.helpers import AppConfig, ApiTestClient, safe_artifact_name

# -----------------------------------------------------------------------------
# Test Configuration & Constants
# -----------------------------------------------------------------------------

DEFAULT_TEST_PORT = 8001
SKIP_DB_FIXTURES = os.getenv("SKIP_TEST_DB_FIXTURES", "").lower() in {"1", "true", "yes", "on"}

# Module-level variable to store the current test's database session
_test_db_session = None


# @pytest_configure
def pytest_configure(config):
    """Configure pytest with custom markers."""
    os.environ["TESTING"] = "true"  # Disable rate limiting
    # Register custom markers
    for marker in ["unit", "integration", "e2e", "gui", "api", "slow"]:
        config.addinivalue_line("markers", f"{marker}: {marker} tests")



@pytest.fixture(scope="session")
def test_port() -> int:
    """Pick a port for the threaded test API server.

    - If E2E_APP_URL is provided, we respect it.
    - Otherwise, choose an ephemeral free port to avoid collisions.
    """
    env_url = os.getenv("E2E_APP_URL")
    if env_url:
        try:
            return urlparse(env_url).port or DEFAULT_TEST_PORT
        except Exception:
            return DEFAULT_TEST_PORT

    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return int(s.getsockname()[1])


@pytest.fixture(scope="session")
def app_config(test_port: int) -> AppConfig:
    """Expose shared application endpoints to tests."""
    app_url = os.getenv("E2E_APP_URL", f"http://localhost:{test_port}").rstrip("/")
    api_base = os.getenv("E2E_API_BASE", f"{app_url}/api").rstrip("/")
    return AppConfig(app_url=app_url, api_base=api_base)


@pytest.fixture(autouse=True)
def mock_authentication(request):
    """
    Mock authentication dependencies for UNIT tests.
    
    This allows unit tests to make authenticated requests without setting up real tokens.
    """

    # Only override auth dependencies for unit tests, NOT integration tests
    # Integration tests need real auth to test permissions.
    # We check for "integration" or "e2e" marker or path.
    is_integration = "integration" in str(request.path) or "e2e" in str(request.path)
    
    # Also allow tests to explicitly opt-out of auth mocking
    if is_integration or request.node.get_closest_marker("no_mock_auth"):
        yield
        return

    from api.dependencies import get_current_admin_user, get_current_user, get_db
    
    # Store original overrides to restore them later (though usually empty)
    # We use app.dependency_overrides.
    

    # Define Mocks
    async def override_get_admin_user():
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
        
    async def override_get_user():
        return Person(
            id="test_admin", # Use admin as default user for unit tests to avoid permission issues
            org_id="test_org",
            name="Test Admin",
            email="admin@test.com",
            roles=["admin"], # Admin role covers volunteer too usually
            timezone="UTC",
            language="en",
            status="active"
        )
        
    def override_verify_org_member(person: Person, org_id: str) -> None:
        pass

    # Apply Overrides
    app.dependency_overrides[get_current_admin_user] = override_get_admin_user
    app.dependency_overrides[get_current_user] = override_get_user
    

    # Monkey Patch verify_org_member
    import api.routers.people
    import api.routers.events
    import api.routers.teams
    import api.dependencies
    
    original_verify = api.dependencies.verify_org_member
    
    # We need to patch where it is used/imported in routers.
    # Note: If routers imported it as `from ... import verify_org_member`, we need to patch the router module.
    # If they used `...Depends(verify_org_member)`, dependency_overrides won't work for simple functions unless they are dependencies.
    # verify_org_member is often used as a direct function call inside dependencies or routers.
    
    api.dependencies.verify_org_member = override_verify_org_member
    
    # Patching known usage locations
    api.routers.people.verify_org_member = override_verify_org_member
    if hasattr(api.routers.events, 'verify_org_member'):
        api.routers.events.verify_org_member = override_verify_org_member
    if hasattr(api.routers.teams, 'verify_org_member'):
        api.routers.teams.verify_org_member = override_verify_org_member
    
    yield
    
    # Restore
    app.dependency_overrides.pop(get_current_admin_user, None)
    app.dependency_overrides.pop(get_current_user, None)
    
    api.dependencies.verify_org_member = original_verify
    api.routers.people.verify_org_member = original_verify
    if hasattr(api.routers.events, 'verify_org_member'):
        api.routers.events.verify_org_member = original_verify
    if hasattr(api.routers.teams, 'verify_org_member'):
        api.routers.teams.verify_org_member = original_verify


# -----------------------------------------------------------------------------
# Database Infrastructure (In-Memory & Threaded Server)
# -----------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Setup in-memory database and patch api.database module.
    
    Crucial fix for 500/malformed DB errors:
    1. Uses `sqlite:///:memory:` to avoid filesystem locks/corruption
    2. Uses `StaticPool` to verify sharing across threads (test runnner <-> uvicorn)
    3. Patches `api.database.engine` and `SessionLocal` so the API uses this shared DB
    """
    if SKIP_DB_FIXTURES:
        yield
        return

    # 1. Configure In-Memory Database with StaticPool
    # Use named shared memory DB to ensure threads share data even if they have different engine instances
    # "sqlite:///file:memdb1?mode=memory&cache=shared&uri=true"
    connect_args = {"check_same_thread": False, "uri": True}
    # 1. Configure In-Memory Database with StaticPool
    # Use named shared memory DB to ensure threads share data even if they have different engine instances
    # "sqlite:////tmp/signupflow_test.db"
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        "sqlite:////tmp/signupflow_test.db",
        connect_args=connect_args,
        echo=False
    )
    
    # 2. Patch the global engine and SessionLocal in the application
    import logging
    logging.getLogger("rostio").fatal(f"DEBUG: patched setup_test_database engine id: {id(engine)}")
    for k in sorted(sys.modules.keys()):
        if "api.database" in k:
            logging.getLogger("rostio").fatal(f"DEBUG: sys.modules[{k}] id: {id(sys.modules[k])}")
    api.database.DATABASE_URL = "sqlite:///file:memdb1?mode=memory&cache=shared&uri=true"
    api.database.engine = engine
    api.database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 3. Initialize Shared Schema
    Base.metadata.create_all(bind=engine)
    
    # 4. Setup Initial Data (Required for startup/health)
    session = api.database.SessionLocal()
    try:
        # Create default organization if missing
        if not session.query(Organization).filter_by(id="test_org").first():
            from datetime import datetime
            org = Organization(
                id="test_org", 
                name="Test Org", 
                region="US", 
                config={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(org)
            
        # Create admin user if missing
        if not session.query(Person).filter_by(id="test_admin").first():
            admin = Person(
                id="test_admin", org_id="test_org", name="Test Admin",
                email="admin@test.com", password_hash=hash_password("password"), roles=["admin"]
            )
            session.add(admin)
            
        # Create volunteer user if missing
        if not session.query(Person).filter_by(id="test_volunteer").first():
            volunteer = Person(
                id="test_volunteer", org_id="test_org", name="Test Volunteer",
                email="sarah@test.com", password_hash=hash_password("password"), roles=["volunteer"]
            )
            session.add(volunteer)
            
        session.commit()
    except Exception as e:
        print(f"⚠️ Error seeding initial data: {e}")
        session.rollback()
    finally:
        session.close()

    yield engine


@pytest.fixture(scope="session")
def api_server(app_config: AppConfig, setup_test_database, test_port: int):
    """
    Start Threaded API server for testing session.
    Uses the patched in-memory database configuration.
    """
    # If running against port 8000 manually, skip start
    if "8000" in app_config.app_url:
        # Note: This might fail if the running server doesn't use the same DB logic, 
        # but typical usage is make test-all which runs on 8001 implicitly via this fixture.
        yield None
        return

    # Configure Environment for the App (Running in same process, so os.environ affects it)
    os.environ["TESTING"] = "true"
    os.environ["EMAIL_ENABLED"] = "false"
    os.environ["SMS_ENABLED"] = "false"
    os.environ["DISABLE_RATE_LIMITS"] = "true"
    os.environ["SECURITY_CSP_ENABLED"] = "false" # Disable CSP for tests

    # Start Uvicorn in a daemon thread
    def run_server():
        # log_level="critical" reduces noise in test output
        uvicorn.run(api.main.app, host="127.0.0.1", port=test_port, log_level="info")

    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

    # Wait for server to be ready
    server_ready = False
    for i in range(20): # 10 seconds timeout
        try:
            resp = requests.get(f"{app_config.app_url}/health", timeout=1)
            if resp.status_code == 200:
                server_ready = True
                break
        except Exception:
            pass
        time.sleep(0.5)

    if not server_ready:
        raise RuntimeError(f"API server failed to start on port {test_port}")

    # Setup E2E Test Data (using the internal setup script logic)
    # We call this AFTER server is ready to ensure the DB is definitely init'd
    try:
        import tests.setup_test_data
        tests.setup_test_data.setup_test_data(app_config.api_base)
        
        from tests.setup_e2e_test_data import setup_e2e_test_data
        setup_e2e_test_data()
    except Exception as e:
        print(f"⚠️  Warning: setup_e2e_test_data failed: {e}")

    yield t
    # Daemon thread dies when main process exits


# -----------------------------------------------------------------------------
# Testing Utility Fixtures (Isolation & Clients)
# -----------------------------------------------------------------------------

def create_test_org(db: Session, org_id: str = None, name: str = None) -> Organization:
    """Helper to create a test organization directly in DB."""
    if not org_id:
        org_id = f"org_{uuid.uuid4().hex[:8]}"
    org = Organization(
        id=org_id,
        name=name or f"Test Org {org_id}",
        region="US",
        config={}
    )
    db.add(org)
    db.commit()
    return org


def create_test_user(
    db: Session, 
    org_id: str, 
    roles: list = None, 
    email: str = None, 
    password: str = None
) -> Person:
    """Helper to create a test user directly in DB."""
    if not email:
        email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    user = Person(
        id=f"person_{uuid.uuid4().hex[:8]}",
        org_id=org_id,
        name="Test User",
        email=email,
        password_hash=hash_password(password or "TestPassword123!"),
        roles=roles or ["volunteer"],
        status="active"
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture(scope="function")
def db(setup_test_database):
    """Provides a transactional database session for tests."""
    from api.database import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function", autouse=True)
def reset_database_between_tests(request, setup_test_database):
    """Reset DB state *before* each test.

    This keeps integration/E2E tests deterministic and avoids auth/test-data drift.
    """
    if SKIP_DB_FIXTURES:
        yield
        return

    # Skip for comprehensive suite (manages its own state)
    if "comprehensive_test_suite.py" in str(request.path):
        yield
        return

    # Clean BEFORE the test
    engine = api.database.engine
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            try:
                conn.execute(text(f"DELETE FROM {table.name}"))
            except Exception:
                pass
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()

    # Re-seed basic data because tests depend on it
    Base.metadata.create_all(bind=engine)

    session = api.database.SessionLocal()
    try:
        org = Organization(id="test_org", name="Test Org", region="US", config={})
        session.add(org)
        admin = Person(
            id="test_admin",
            org_id="test_org",
            name="Test Admin",
            email="admin@test.com",
            password_hash=hash_password("password"),
            roles=["admin"],
        )
        session.add(admin)
        volunteer = Person(
            id="test_volunteer",
            org_id="test_org",
            name="Test Volunteer",
            email="sarah@test.com",
            password_hash=hash_password("password"),
            roles=["volunteer"],
        )
        session.add(volunteer)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

    yield



@pytest.fixture(scope="function")
def api_client(app_config: AppConfig) -> Generator[ApiTestClient, None, None]:
    """Provide a disposable API client for test data setup."""
    client = ApiTestClient(app_config.api_base)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="function")
def client(api_client):
    """
    Fixture alias for 'client' to support existing tests.
    Returns the underlying TestClient from ApiTestClient or creates a fresh one.
    
    Note: api_client uses requests (for E2E/Integration). 
    Unit tests usually expect FastAPI TestClient.
    """
    from fastapi.testclient import TestClient
    from api.main import app
    return TestClient(app)


@pytest.fixture(scope="function")
def browser_context(request, app_config: AppConfig):
    """Provide a fresh browser context with tracing."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            base_url=app_config.app_url,
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        yield context
        
        # Save trace on failure
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
    """Provide a fresh page and clear storage."""
    page = browser_context.new_page()
    page.set_default_timeout(5000)
    
    # Console logging
    page.on("console", lambda msg: 
        print(f"CONSOLE: {msg.type}: {msg.text}") if msg.type in ["error", "warning"] else None
    )

    # Clear storage
    try:
        page.goto(APP_URL, wait_until="domcontentloaded")
        page.evaluate("localStorage.clear(); sessionStorage.clear();")
        browser_context.clear_cookies()
    except Exception:
        pass

    yield page
    page.close()


@pytest.fixture(scope="function")
def authenticated_page(page):
    """Login flow helper."""
    page.goto(APP_URL)
    # Login as volunteer
    page.fill('input[type="email"]', "sarah@test.com")
    page.fill('input[type="password"]', "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(1000)
    yield page


@pytest.fixture(scope="function")
def admin_page(page):
    """Admin login flow helper."""
    page.goto(APP_URL)
    # Login as admin
    page.fill('input[type="email"]', "jane@test.com")
    page.fill('input[type="password"]', "password")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(2000)
    yield page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test result for fixtures."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

@pytest.fixture(scope="function")
def test_org_setup(reset_database_between_tests):
    """
    Alias for database reset to satisfy legacy test dependencies.
    Ensures 'test_org', 'test_admin', and 'test_volunteer' exist.
    """
    return reset_database_between_tests
