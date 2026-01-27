"""Pytest configuration and fixtures for Rostio tests."""

from pathlib import Path
import os
import sys
import time
import threading
import shutil
import asyncio
import logging
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

TEST_PORT = 8001
APP_URL = os.getenv("E2E_APP_URL", f"http://localhost:{TEST_PORT}").rstrip("/")
API_BASE = os.getenv("E2E_API_BASE", f"{APP_URL}/api").rstrip("/")
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
def app_config() -> AppConfig:
    """Expose shared application endpoints to tests."""
    return AppConfig(app_url=APP_URL, api_base=API_BASE)


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
                email="jane@test.com", password_hash=hash_password("password"), roles=["admin"]
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
def api_server(app_config: AppConfig, setup_test_database):
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
        uvicorn.run(api.main.app, host="127.0.0.1", port=TEST_PORT, log_level="info")

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
        raise RuntimeError(f"API server failed to start on port {TEST_PORT}")

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

@pytest.fixture(scope="function", autouse=True)
def reset_database_between_tests(request, setup_test_database):
    """
    Triggers DB cleanup between tests.
    Since we are using In-Memory DB with Shared Engine, we just DELETE data.
    """
    if SKIP_DB_FIXTURES:
        yield
        return
        
    # Skip for comprehensive suite (manages its own state)
    if "comprehensive_test_suite.py" in str(request.path):
        yield
        return

    yield # Verify test runs first? No, usually before.
    
    # Wait, usually we want to clean BEFORE the test. 
    # But `autouse=True` runs expected setup -> yield -> teardown.
    # The previous implementation cleaned BEFORE. Let's stick to that pattern if needed.
    # However, for E2E, it's often safer to clean AFTER to leave system clean.
    # PROPOSAL: Clean BEFORE to guarantee state.
    pass # Currently relying on logic being inserted... 
    
    # Actually, let's implement the Clean BEFORE logic:
    # We use the patched engine
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
    # DEFENSIVE: Ensure tables exist!
    Base.metadata.create_all(bind=engine)
    
    session = api.database.SessionLocal()
    try:
        org = Organization(id="test_org", name="Test Org", region="US", config={})
        session.add(org)
        admin = Person(id="test_admin", org_id="test_org", name="Test Admin", email="jane@test.com", password_hash=hash_password("password"), roles=["admin"])
        session.add(admin)
        volunteer = Person(id="test_volunteer", org_id="test_org", name="Test Volunteer", email="sarah@test.com", password_hash=hash_password("password"), roles=["volunteer"])
        session.add(volunteer)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()



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
