"""Setup test data directly in the database for integration and E2E runs."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.models import Base, Organization, Person, Event
from api.security import hash_password


def _get_engine() -> tuple[str, sessionmaker]:
    """
    Build a SQLAlchemy session factory for the configured test database.

    Falls back to the default sqlite:///./test_roster.db used by tests when
    DATABASE_URL is not explicitly provided.
    """
    db_url = os.getenv("DATABASE_URL", "sqlite:///./test_roster.db")
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "", 1)
        if db_path.startswith("./"):
            db_path = db_path[2:]
        base_path = os.path.abspath(db_path)
        if not os.path.exists(base_path):
            # WAL/SHM cleanup removed to avoid interfering with running server
            pass
    engine = create_engine(db_url, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)
    return db_url, sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _upsert_organization(session, org_id: str, name: str, *, region: str, config: dict) -> Organization:
    organization = session.get(Organization, org_id)
    if organization is None:
        organization = Organization(id=org_id, name=name, region=region, config=config)
        session.add(organization)
    else:
        organization.name = name
        organization.region = region
        organization.config = config
    return organization


def _upsert_person(
    session,
    *,
    person_id: str,
    org_id: str,
    name: str,
    email: str,
    password: str,
    roles: Iterable[str],
) -> None:
    person = session.query(Person).filter(Person.email == email).one_or_none()
    password_hash = hash_password(password)
    roles_list = list(roles)

    if person is None:
        person = Person(
            id=person_id,
            org_id=org_id,
            name=name,
            email=email,
            password_hash=password_hash,
            roles=roles_list,
            extra_data={},
        )
        session.add(person)
    else:
        person.name = name
        person.org_id = org_id
        person.email = email
        person.roles = roles_list
        person.password_hash = password_hash


def _upsert_event(
    session,
    *,
    event_id: str,
    org_id: str,
    event_type: str,
    start_time: datetime,
    end_time: datetime,
) -> None:
    event = session.query(Event).filter(Event.id == event_id).one_or_none()
    if event is None:
        event = Event(
            id=event_id,
            org_id=org_id,
            type=event_type,
            start_time=start_time,
            end_time=end_time,
            extra_data={"role_counts": {"volunteer": 2, "leader": 1}},
        )
        session.add(event)
    else:
        event.type = event_type
        event.org_id = org_id
        event.start_time = start_time
        event.end_time = end_time
        event.extra_data = event.extra_data or {}
        event.extra_data.setdefault("role_counts", {"volunteer": 2, "leader": 1})


def setup_test_data(_: str | None = None) -> None:
    """
    Seed deterministic baseline data for tests.

    Existing records are updated in-place so repeated executions remain idempotent.
    """
    print("Setting up test data...")
    _, SessionLocal = _get_engine()
    session = SessionLocal()
    try:
        org = _upsert_organization(
            session,
            org_id="test_org",
            name="Test Organization",
            region="Test Region",
            config={"roles": ["volunteer", "leader", "admin"]},
        )

        people = [
            {
                "person_id": "person_jane_admin",
                "name": "Jane Smith",
                "email": "jane@test.com",
                "password": "password",
                "roles": ["admin"],
            },
            {
                "person_id": "person_sarah_volunteer",
                "name": "Sarah Johnson",
                "email": "sarah@test.com",
                "password": "password",
                "roles": ["volunteer"],
            },
            {
                "person_id": "person_john_volunteer",
                "name": "John Doe",
                "email": "john@test.com",
                "password": "password",
                "roles": ["volunteer"],
            },
        ]
        for person in people:
            _upsert_person(
                session,
                person_id=person["person_id"],
                org_id=org.id,
                name=person["name"],
                email=person["email"],
                password=person["password"],
                roles=person["roles"],
            )

        now = datetime.utcnow()
        events = [
            {
                "event_id": "event_001",
                "event_type": "Sunday Service",
                "start": now + timedelta(days=7, hours=9),
                "end": now + timedelta(days=7, hours=11),
            },
            {
                "event_id": "event_002",
                "event_type": "Youth Meeting",
                "start": now + timedelta(days=14, hours=18),
                "end": now + timedelta(days=14, hours=19),
            },
        ]
        for event in events:
            _upsert_event(
                session,
                event_id=event["event_id"],
                org_id=org.id,
                event_type=event["event_type"],
                start_time=event["start"],
                end_time=event["end"],
            )

        session.commit()
        print("✅ Test data setup complete\n")
    finally:
        session.close()


if __name__ == "__main__":
    setup_test_data()
