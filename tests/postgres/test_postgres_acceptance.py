"""Migration-only PostgreSQL business and concurrency acceptance."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import timedelta
from threading import Barrier

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config
from api.main import app
from api.models import (
    Assignment,
    AuditAction,
    AuditLog,
    DeliveryLog,
    Event,
    Invitation,
    Notification,
    Organization,
    Person,
    Solution,
)
from api.routers.auth import SignupRequest, signup
from api.routers.invitations import accept_invitation
from api.schemas.invitation import InvitationAccept
from api.security import hash_password
from api.services.allocation_service import AllocationConflictError, claim_open_shift
from api.services.publication_service import capture_solution_scope, publish_solution_transaction
from api.timeutils import utcnow

pytestmark = [pytest.mark.integration, pytest.mark.no_mock_auth]


def _database_url() -> str:
    value = os.environ.get("SIGNUPFLOW_POSTGRES_TEST_URL")
    if not value or not value.startswith("postgresql://") or "/signupflow_test_" not in value:
        pytest.fail("Run this suite only through `make test-postgres`.")
    return value


def _upgrade_database_url() -> str:
    value = os.environ.get("SIGNUPFLOW_POSTGRES_UPGRADE_TEST_URL")
    if not value or not value.startswith("postgresql://") or "/signupflow_test_" not in value:
        pytest.fail("The owned upgrade database was not provided by the PostgreSQL runner.")
    return value


def _alembic_config(url: str) -> Config:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    return config


@contextmanager
def _alembic_database(url: str):
    """Temporarily point Alembic's environment override at one owned database."""
    previous = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = url
    try:
        yield _alembic_config(url)
    finally:
        if previous is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous


@pytest.fixture(scope="session")
def postgres_url() -> str:
    return _database_url()


@pytest.fixture(scope="session")
def sessions(postgres_url: str):
    engine = create_engine(postgres_url, pool_pre_ping=True)
    try:
        yield sessionmaker(bind=engine, expire_on_commit=False)
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def _signup_payload(*, suffix: str = "race") -> dict[str, str]:
    return {
        "org_id": f"postgres-bootstrap-{suffix}",
        "org_name": "PostgreSQL Bootstrap",
        "name": "Owner",
        "email": f"postgres-owner-{suffix}@example.com",
        "password": "StrongPass123!",
    }


def test_migration_only_schema_is_current_and_matches_critical_contracts(postgres_url: str) -> None:
    engine = create_engine(postgres_url)
    try:
        inspector = inspect(engine)
        assert inspector.get_table_names()
        with engine.connect() as connection:
            assert connection.dialect.name == "postgresql"
            assert connection.scalar(text("SELECT version()"))
            assert (
                connection.scalar(text("SELECT version_num FROM alembic_version")) == "a9c2e4f6b8d0"
            )

        people_columns = {column["name"]: column for column in inspector.get_columns("people")}
        assignment_columns = {
            column["name"]: column for column in inspector.get_columns("assignments")
        }
        assert people_columns["roles"]["type"].__class__.__name__ in {"TEXT", "VARCHAR"}
        assert people_columns["timezone"]["nullable"] is False
        assert assignment_columns["response_status"]["nullable"] is False
        person_fks = inspector.get_foreign_keys("people")
        assert any(fk["referred_table"] == "organizations" for fk in person_fks)

        with _alembic_database(postgres_url) as config:
            command.check(config)
    finally:
        engine.dispose()


def test_upgrade_from_existing_data_preserves_identity_and_assignment_truth() -> None:
    url = _upgrade_database_url()
    engine = create_engine(url)
    try:
        with _alembic_database(url) as config:
            command.upgrade(config, "c5d7e9f1a3b4")
        now = utcnow().replace(tzinfo=None)
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO organizations (id, name, config, created_at, updated_at) "
                    "VALUES ('upgrade-org', 'Upgrade Org', '{}', :now, :now)"
                ),
                {"now": now},
            )
            connection.execute(
                text(
                    "INSERT INTO people "
                    "(id, org_id, name, email, roles, timezone, language, status, "
                    "is_sample, refresh_token_version, created_at, updated_at) VALUES "
                    "('upgrade-person', 'upgrade-org', 'Upgrade Person', "
                    "'upgrade-person@example.test', '[\"volunteer\", \"usher\"]', "
                    "'America/Toronto', 'en', 'active', false, 0, :now, :now)"
                ),
                {"now": now},
            )
            connection.execute(
                text(
                    "INSERT INTO events "
                    "(id, org_id, type, start_time, end_time, is_sample, "
                    "is_exception, created_at) "
                    "VALUES ('upgrade-event', 'upgrade-org', 'service', "
                    ":start, :end, false, false, :now)"
                ),
                {
                    "start": now + timedelta(days=7),
                    "end": now + timedelta(days=7, hours=1),
                    "now": now,
                },
            )
            solution_id = connection.scalar(
                text(
                    "INSERT INTO solutions (org_id, hard_violations, soft_score, health_score, "
                    "is_published, created_at) VALUES "
                    "('upgrade-org', 0, 0, 100, true, :now) RETURNING id"
                ),
                {"now": now},
            )
            connection.execute(
                text(
                    "INSERT INTO assignments "
                    "(solution_id, event_id, person_id, role, status, assigned_at) VALUES "
                    "(:solution_id, 'upgrade-event', 'upgrade-person', "
                    "'usher', 'confirmed', :now)"
                ),
                {"solution_id": solution_id, "now": now},
            )
            connection.execute(
                text(
                    "INSERT INTO invitations "
                    "(id, org_id, email, name, roles, invited_by, token, status, "
                    "expires_at, created_at, accepted_at) VALUES "
                    "('upgrade-invitation', 'upgrade-org', 'accepted@example.test', "
                    "'Accepted Member', '[\"volunteer\", \"usher\"]', "
                    "'upgrade-person', 'accepted-upgrade-token', 'accepted', "
                    ":expires_at, :now, :now)"
                ),
                {"expires_at": now + timedelta(days=1), "now": now},
            )

        with _alembic_database(url) as config:
            command.upgrade(config, "head")
            command.check(config)
        with engine.connect() as connection:
            assert (
                connection.scalar(text("SELECT version_num FROM alembic_version")) == "a9c2e4f6b8d0"
            )
            assert (
                connection.scalar(text("SELECT roles FROM people WHERE id='upgrade-person'"))
                == '["volunteer", "usher"]'
            )
            invitation = connection.execute(
                text(
                    "SELECT status, roles, accepted_at FROM invitations "
                    "WHERE id='upgrade-invitation'"
                )
            ).one()
            assert invitation.status == "accepted"
            assert invitation.roles == '["volunteer", "usher"]'
            assert invitation.accepted_at == now
            row = connection.execute(
                text(
                    "SELECT role, response_status, commitment_revision, response_revision "
                    "FROM assignments WHERE event_id='upgrade-event'"
                )
            ).one()
            assert tuple(row) == ("usher", "pending", 1, None)
    finally:
        engine.dispose()


def test_postgres_concurrent_bootstrap_creates_one_owner(sessions) -> None:
    request = SignupRequest(**_signup_payload())
    barrier = Barrier(2, timeout=15)

    def attempt() -> int:
        with sessions() as db:
            barrier.wait()
            try:
                signup(request, db)
                return 201
            except HTTPException as exc:
                return exc.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = sorted(executor.map(lambda _: attempt(), range(2)))

    assert statuses == [201, 409]
    with sessions() as db:
        assert db.query(Organization).filter_by(id=request.org_id).count() == 1
        owners = db.query(Person).filter_by(org_id=request.org_id).all()
        assert len(owners) == 1
        assert owners[0].roles == ["admin"]


def test_postgres_concurrent_invitation_acceptance_has_one_winner(sessions) -> None:
    with sessions() as db:
        db.add(Organization(id="postgres-invite-org", name="PostgreSQL Invite Org"))
        db.add(
            Person(
                id="postgres-invite-owner",
                org_id="postgres-invite-org",
                name="Owner",
                email="postgres-invite-owner@example.test",
                password_hash=hash_password("OwnerPass1!"),
                roles=["admin"],
            )
        )
        db.add(
            Invitation(
                id="postgres-race-invitation",
                org_id="postgres-invite-org",
                email="postgres-race-member@example.test",
                name="Race Member",
                roles=["volunteer", "usher"],
                invited_by="postgres-invite-owner",
                token="postgres-race-token",
                status="pending",
                expires_at=utcnow() + timedelta(days=1),
            )
        )
        db.commit()

    barrier = Barrier(2, timeout=15)

    def attempt() -> int:
        with sessions() as db:
            barrier.wait()
            try:
                accept_invitation(
                    "postgres-race-token",
                    InvitationAccept(password="MemberPass1!", timezone="UTC"),
                    db,
                )
                return 201
            except HTTPException as exc:
                return exc.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = sorted(executor.map(lambda _: attempt(), range(2)))

    assert statuses == [201, 409]
    with sessions() as db:
        member = db.query(Person).filter_by(email="postgres-race-member@example.test").one()
        assert member.roles == ["volunteer", "usher"]
        assert (
            db.query(Invitation).filter_by(id="postgres-race-invitation").one().status == "accepted"
        )


def test_inactive_membership_rejects_login_access_refresh_and_browser_session(
    client, sessions
) -> None:
    response = client.post("/api/v1/auth/signup", json=_signup_payload(suffix="inactive"))
    assert response.status_code == 201
    identity = response.json()
    with sessions() as db:
        person = db.query(Person).filter_by(id=identity["person_id"]).one()
        person.status = "inactive"
        db.commit()

    headers = {"Authorization": f"Bearer {identity['token']}"}
    assert client.get("/api/v1/people/me", headers=headers).status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": identity["email"], "password": "StrongPass123!"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": identity["refresh_token"]}
        ).status_code
        == 401
    )
    client.cookies.set("signupflow_session", identity["token"])
    browser = client.get("/a/dashboard", follow_redirects=False)
    assert browser.status_code == 303
    assert browser.headers["location"] == "/auth/login"
    client.cookies.clear()


def test_cancelled_organization_keeps_admin_restore_path_but_hides_default_listing(client) -> None:
    identity = client.post("/api/v1/auth/signup", json=_signup_payload(suffix="cancelled")).json()
    headers = {"Authorization": f"Bearer {identity['token']}"}
    org_id = identity["org_id"]

    assert client.post(f"/api/v1/organizations/{org_id}/cancel", headers=headers).status_code == 200
    hidden = client.get("/api/v1/organizations/", headers=headers).json()
    assert hidden["items"] == []
    assert (
        client.get(
            "/api/v1/organizations/", params={"include_cancelled": True}, headers=headers
        ).json()["items"][0]["id"]
        == org_id
    )
    assert (
        client.post(f"/api/v1/organizations/{org_id}/restore", headers=headers).status_code == 200
    )


def test_postgres_hard_delete_removes_related_rows_and_retains_audit(client, sessions) -> None:
    identity = client.post("/api/v1/auth/signup", json=_signup_payload(suffix="hard-delete")).json()
    headers = {"Authorization": f"Bearer {identity['token']}"}
    org_id = identity["org_id"]
    event_id = "postgres-hard-delete-event"
    delivery_message_id = "postgres-hard-delete-message"
    volunteer_id = "postgres-hard-delete-volunteer"
    foreign_org_id = "postgres-hard-delete-foreign"

    with sessions() as db:
        db.add(Organization(id=foreign_org_id, name="Foreign survivor"))
        db.add(
            Person(
                id="postgres-hard-delete-foreign-admin",
                org_id=foreign_org_id,
                name="Foreign Admin",
                email="postgres-hard-delete-foreign@example.test",
                roles=["admin"],
            )
        )
        volunteer = Person(
            id=volunteer_id,
            org_id=org_id,
            name="Synthetic Volunteer",
            email="postgres-hard-delete-volunteer@example.test",
            roles=["volunteer", "usher"],
        )
        event = Event(
            id=event_id,
            org_id=org_id,
            type="service",
            start_time=utcnow() + timedelta(days=7),
            end_time=utcnow() + timedelta(days=7, hours=1),
        )
        solution = Solution(
            org_id=org_id,
            hard_violations=0,
            soft_score=0,
            health_score=100,
        )
        notification = Notification(
            org_id=org_id,
            recipient=volunteer,
            event=event,
            type="assignment",
            status="delivered",
            sendgrid_message_id=delivery_message_id,
        )
        invitation = Invitation(
            id="postgres-hard-delete-invitation",
            org_id=org_id,
            email="postgres-hard-delete-invitee@example.test",
            name="Synthetic Invitee",
            roles=["volunteer", "usher"],
            invited_by=identity["person_id"],
            token="postgres-hard-delete-token",
            expires_at=utcnow() + timedelta(days=1),
        )
        db.add_all([event, solution, notification, invitation])
        db.flush()
        db.add(
            Assignment(
                solution_id=solution.id,
                event_id=event.id,
                person_id=volunteer.id,
                role="usher",
            )
        )
        db.add(
            DeliveryLog(
                notification_id=notification.id,
                event_type="delivered",
                sendgrid_message_id=delivery_message_id,
                timestamp=utcnow(),
            )
        )
        db.commit()

    response = client.delete(f"/api/v1/organizations/{org_id}", headers=headers)

    assert response.status_code == 204, response.text
    with sessions() as db:
        assert db.query(Organization).filter_by(id=org_id).count() == 0
        assert db.query(Person).filter_by(org_id=org_id).count() == 0
        assert db.query(Event).filter_by(org_id=org_id).count() == 0
        assert db.query(Solution).filter_by(org_id=org_id).count() == 0
        assert db.query(Assignment).filter_by(person_id=volunteer_id).count() == 0
        assert db.query(Invitation).filter_by(org_id=org_id).count() == 0
        assert db.query(Notification).filter_by(org_id=org_id).count() == 0
        assert db.query(DeliveryLog).filter_by(sendgrid_message_id=delivery_message_id).count() == 0
        assert db.query(Organization).filter_by(id=foreign_org_id).one()
        assert db.query(Person).filter_by(org_id=foreign_org_id).count() == 1
        audit = (
            db.query(AuditLog)
            .filter_by(
                organization_id=org_id,
                action=AuditAction.BULK_DELETE,
                resource_type="organization",
                resource_id=org_id,
            )
            .one()
        )
        assert audit.user_id == identity["person_id"]
        assert audit.user_email == identity["email"]


def test_postgres_last_slot_claim_has_one_winner(sessions) -> None:
    start = utcnow() + timedelta(days=30)
    with sessions() as db:
        db.add(Organization(id="postgres-claim-org", name="PostgreSQL Claim Org"))
        for person_id in ("postgres-first", "postgres-second"):
            db.add(
                Person(
                    id=person_id,
                    org_id="postgres-claim-org",
                    name=person_id,
                    email=f"{person_id}@example.test",
                    roles=["volunteer", "usher"],
                    status="active",
                )
            )
        db.add(
            Event(
                id="postgres-service",
                org_id="postgres-claim-org",
                type="service",
                start_time=start,
                end_time=start + timedelta(hours=1),
                extra_data={"role_counts": {"usher": 1}},
            )
        )
        db.commit()

    barrier = Barrier(2, timeout=15)

    def attempt(person_id: str) -> str:
        with sessions() as db:
            barrier.wait()
            try:
                claim_open_shift(
                    db,
                    org_id="postgres-claim-org",
                    event_id="postgres-service",
                    person_id=person_id,
                    role="usher",
                    actor_email=f"{person_id}@example.test",
                )
                db.commit()
                return "won"
            except AllocationConflictError as exc:
                db.rollback()
                return exc.code

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = sorted(executor.map(attempt, ("postgres-first", "postgres-second")))

    assert results == ["role_full", "won"]


def test_postgres_concurrent_publish_leaves_one_active_solution(sessions) -> None:
    start = utcnow() + timedelta(days=31)
    with sessions() as db:
        db.add(Organization(id="postgres-publish-org", name="PostgreSQL Publish Org"))
        db.add(
            Person(
                id="postgres-publish-admin",
                org_id="postgres-publish-org",
                name="Admin",
                email="postgres-publish-admin@example.test",
                roles=["admin"],
            )
        )
        people = []
        for suffix in ("first", "second"):
            person = Person(
                id=f"postgres-publish-{suffix}",
                org_id="postgres-publish-org",
                name=suffix,
                email=f"postgres-publish-{suffix}@example.test",
                roles=["volunteer", "usher"],
            )
            people.append(person)
            db.add(person)
        event = Event(
            id="postgres-publish-event",
            org_id="postgres-publish-org",
            type="service",
            start_time=start,
            end_time=start + timedelta(hours=1),
            extra_data={"role_counts": {"usher": 1}},
        )
        db.add(event)
        db.flush()
        scope = capture_solution_scope([event], range_start=start.date(), range_end=start.date())
        solution_ids = []
        for person in people:
            solution = Solution(
                org_id="postgres-publish-org",
                hard_violations=0,
                soft_score=0,
                health_score=100,
                scope_start=scope.range_start,
                scope_end=scope.range_end,
                scope_event_ids=scope.event_ids,
                scope_fingerprint=scope.fingerprint,
            )
            db.add(solution)
            db.flush()
            db.add(
                Assignment(
                    solution_id=solution.id,
                    event_id=event.id,
                    person_id=person.id,
                    role="usher",
                )
            )
            solution_ids.append(solution.id)
        db.commit()

    barrier = Barrier(2, timeout=15)

    def publish(solution_id: int) -> None:
        with sessions() as db:
            actor = db.query(Person).filter_by(id="postgres-publish-admin").one()
            barrier.wait()
            publish_solution_transaction(
                db,
                solution_id=solution_id,
                org_id="postgres-publish-org",
                actor=actor,
            )
            db.commit()

    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(publish, solution_ids))

    with sessions() as db:
        active = (
            db.query(Solution).filter_by(org_id="postgres-publish-org", is_published=True).all()
        )
        assert len(active) == 1
        assert active[0].id in solution_ids
