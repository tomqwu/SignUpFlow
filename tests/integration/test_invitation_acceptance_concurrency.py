"""Concurrent invitation acceptance creates exactly one member account."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier, Event

import pytest
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.models import Base, Invitation, Organization, Person
from api.routers import invitations
from api.routers.invitations import accept_invitation, cancel_invitation, resend_invitation
from api.schemas.invitation import InvitationAccept
from api.security import hash_password
from api.timeutils import utcnow
from web.routers.partials import people_cancel_invitation


def _seed_invitation(session_factory):
    with session_factory() as setup:
        setup.add(Organization(id="race-org", name="Race Organization"))
        setup.add(
            Person(
                id="race-owner",
                org_id="race-org",
                name="Owner",
                email="race-owner@example.com",
                password_hash=hash_password("OwnerPass1!"),
                roles=["admin"],
            )
        )
        setup.add(
            Invitation(
                id="race-invitation",
                org_id="race-org",
                email="race-member@example.com",
                name="Race Member",
                roles=["volunteer", "usher"],
                invited_by="race-owner",
                token="race-token",
                status="pending",
                expires_at=utcnow().replace(year=utcnow().year + 1),
            )
        )
        setup.commit()


@pytest.mark.integration
def test_concurrent_invitation_acceptance_has_one_winner(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'invitation-race.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    hash_barrier = Barrier(2, timeout=10)
    real_hash_password = invitations.hash_password

    def coordinated_hash(password: str):
        hash_barrier.wait()
        return real_hash_password(password)

    SessionFactory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    _seed_invitation(SessionFactory)
    monkeypatch.setattr(invitations, "hash_password", coordinated_hash)

    def attempt_acceptance() -> int:
        with SessionFactory() as session:
            try:
                accept_invitation(
                    "race-token",
                    InvitationAccept(password="MemberPass1!", timezone="UTC"),
                    session,
                )
                return 201
            except HTTPException as exc:
                return exc.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = sorted(executor.map(lambda _: attempt_acceptance(), range(2)))

    with SessionFactory() as verification:
        assert statuses == [201, 409]
        assert verification.query(Person).filter_by(email="race-member@example.com").count() == 1
        assert (
            verification.query(Invitation).filter_by(id="race-invitation").one().status
            == "accepted"
        )

    engine.dispose()


@pytest.mark.integration
def test_cancellation_wins_before_acceptance_claim(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'invitation-cancel-race.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SessionFactory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    _seed_invitation(SessionFactory)
    hashing_started = Event()
    resume_acceptance = Event()
    real_hash_password = invitations.hash_password

    def paused_hash(password: str):
        hashing_started.set()
        assert resume_acceptance.wait(10)
        return real_hash_password(password)

    monkeypatch.setattr(invitations, "hash_password", paused_hash)

    def attempt_acceptance() -> int:
        with SessionFactory() as session:
            try:
                accept_invitation(
                    "race-token",
                    InvitationAccept(password="MemberPass1!", timezone="UTC"),
                    session,
                )
                return 201
            except HTTPException as exc:
                return exc.status_code

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(attempt_acceptance)
        try:
            assert hashing_started.wait(10)
            with SessionFactory() as session:
                admin = session.query(Person).filter(Person.id == "race-owner").one()
                response = people_cancel_invitation("race-invitation", person=admin, db=session)
                assert response.status_code == 303
        finally:
            resume_acceptance.set()
        assert future.result() == 409

    with SessionFactory() as verification:
        assert (
            verification.query(Person)
            .filter(Person.org_id == "race-org", Person.email == "race-member@example.com")
            .count()
            == 0
        )
        assert (
            verification.query(Invitation)
            .filter(Invitation.id == "race-invitation", Invitation.org_id == "race-org")
            .one()
            .status
            == "cancelled"
        )

    engine.dispose()


@pytest.mark.integration
def test_resend_rotates_token_before_acceptance_claim(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'invitation-resend-race.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SessionFactory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    _seed_invitation(SessionFactory)
    hashing_started = Event()
    resume_acceptance = Event()
    real_hash_password = invitations.hash_password

    def paused_hash(password: str):
        hashing_started.set()
        assert resume_acceptance.wait(10)
        return real_hash_password(password)

    monkeypatch.setattr(invitations, "hash_password", paused_hash)

    def attempt_acceptance() -> int:
        with SessionFactory() as session:
            try:
                accept_invitation(
                    "race-token",
                    InvitationAccept(password="MemberPass1!", timezone="UTC"),
                    session,
                )
                return 201
            except HTTPException as exc:
                return exc.status_code

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(attempt_acceptance)
        try:
            assert hashing_started.wait(10)
            with SessionFactory() as session:
                admin = session.query(Person).filter(Person.id == "race-owner").one()
                renewed = resend_invitation(
                    "race-invitation", BackgroundTasks(), admin=admin, db=session
                )
                assert renewed.token != "race-token"
        finally:
            resume_acceptance.set()
        assert future.result() == 409

    with SessionFactory() as verification:
        assert (
            verification.query(Person)
            .filter(Person.org_id == "race-org", Person.email == "race-member@example.com")
            .count()
            == 0
        )
        invitation = (
            verification.query(Invitation)
            .filter(Invitation.id == "race-invitation", Invitation.org_id == "race-org")
            .one()
        )
        assert invitation.status == "pending"
        assert invitation.token != "race-token"

    engine.dispose()


@pytest.mark.integration
def test_accepted_invitation_cannot_be_cancelled(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'invitation-accepted-cancel.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SessionFactory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    _seed_invitation(SessionFactory)

    with SessionFactory() as session:
        admin = session.query(Person).filter(Person.id == "race-owner").one()
        invitation = (
            session.query(Invitation)
            .filter(Invitation.id == "race-invitation", Invitation.org_id == "race-org")
            .one()
        )
        invitation.status = "accepted"
        session.commit()

        with pytest.raises(HTTPException) as error:
            cancel_invitation("race-invitation", admin=admin, db=session)
        assert error.value.status_code == 409
        session.refresh(invitation)
        assert invitation.status == "accepted"

    engine.dispose()


@pytest.mark.integration
def test_listing_expired_invitation_does_not_invalidate_resend(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'invitation-list-resend-race.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    session_factory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    _seed_invitation(session_factory)
    with session_factory() as session:
        invitation = (
            session.query(Invitation)
            .filter(Invitation.id == "race-invitation", Invitation.org_id == "race-org")
            .one()
        )
        invitation.expires_at = utcnow() - timedelta(minutes=1)
        session.commit()

    expiry_started = Event()
    resume_listing = Event()
    original_expire = invitations._expire_invitation

    def paused_expire(db, invitation, token):
        expiry_started.set()
        assert resume_listing.wait(10)
        return original_expire(db, invitation, token)

    monkeypatch.setattr(invitations, "_expire_invitation", paused_expire)

    def list_rows():
        with session_factory() as session:
            admin = session.query(Person).filter(Person.id == "race-owner").one()
            return asyncio.run(
                invitations.list_invitations(
                    org_id="race-org", admin=admin, status_filter=None, q=None, db=session
                )
            )

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(list_rows)
        try:
            assert expiry_started.wait(10)
            with session_factory() as session:
                admin = session.query(Person).filter(Person.id == "race-owner").one()
                renewed = resend_invitation(
                    "race-invitation", BackgroundTasks(), admin=admin, db=session
                )
                new_token = renewed.token
        finally:
            resume_listing.set()
        listing = future.result()

    assert listing.items[0].status == "pending"
    assert listing.items[0].token == new_token
    with session_factory() as session:
        invitation = (
            session.query(Invitation)
            .filter(Invitation.id == "race-invitation", Invitation.org_id == "race-org")
            .one()
        )
        assert invitation.status == "pending"
        assert invitation.token == new_token

    engine.dispose()


@pytest.mark.integration
def test_public_verify_does_not_reveal_rotated_token(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'invitation-verify-resend-race.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    session_factory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    _seed_invitation(session_factory)
    with session_factory() as session:
        invitation = (
            session.query(Invitation)
            .filter(Invitation.id == "race-invitation", Invitation.org_id == "race-org")
            .one()
        )
        invitation.expires_at = utcnow() - timedelta(minutes=1)
        session.commit()

    expiry_started = Event()
    resume_verification = Event()
    original_expire = invitations._expire_invitation

    def paused_expire(db, invitation, token):
        expiry_started.set()
        assert resume_verification.wait(10)
        return original_expire(db, invitation, token)

    monkeypatch.setattr(invitations, "_expire_invitation", paused_expire)

    def verify_old_token():
        with session_factory() as session:
            return invitations.verify_invitation("race-token", session)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(verify_old_token)
        try:
            assert expiry_started.wait(10)
            with session_factory() as session:
                admin = session.query(Person).filter(Person.id == "race-owner").one()
                renewed = resend_invitation(
                    "race-invitation", BackgroundTasks(), admin=admin, db=session
                )
                new_token = renewed.token
        finally:
            resume_verification.set()
        verification = future.result()

    assert verification.valid is False
    assert verification.invitation is None or verification.invitation.token == "race-token"
    assert new_token != "race-token"
    engine.dispose()
