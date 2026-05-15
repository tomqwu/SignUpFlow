"""Web test fixtures. Mirrors tests/api/conftest.py's in-memory DB
override; adds a TestClient that does NOT auto-follow redirects so the
cookie/redirect handshake is assertable. Root conftest's autouse
mock_authentication is suppressed (web auth is cookie-based, exercised
for real)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.database import get_db
from api.main import app
from api.models import Base, Organization, Person
from api.security import hash_password


@pytest.fixture(autouse=True)
def _strict_tenancy_guard(monkeypatch):
    monkeypatch.setenv("TENANCY_GUARD", "strict")


@pytest.fixture(autouse=True)
def mock_authentication():
    """Web tests use the real cookie session — suppress root mocking."""
    yield


@pytest.fixture(autouse=True)
def reset_database_between_tests():
    yield


@pytest.fixture(scope="function")
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine)
    session = factory()

    def _override():
        s = factory()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _override
    try:
        yield session
    finally:
        session.close()
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()


@pytest.fixture(scope="function")
def client():
    # follow_redirects=False so we can assert the 303 + Set-Cookie.
    with TestClient(app, follow_redirects=False) as c:
        yield c


def seed_person(
    db,
    *,
    person_id="web_user",
    org_id="web_org",
    email="user@web.test",
    password="WebPass123!",
    roles=None,
):
    if not db.query(Organization).filter(Organization.id == org_id).first():
        db.add(Organization(id=org_id, name="Web Org", region="Test"))
    person = Person(
        id=person_id,
        org_id=org_id,
        name="Web User",
        email=email,
        password_hash=hash_password(password),
        roles=roles if roles is not None else ["volunteer"],
        status="active",
    )
    db.add(person)
    db.commit()
    return person
