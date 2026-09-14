"""Concurrent invitation acceptance creates exactly one member account."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.models import Base, Invitation, Organization, Person
from api.routers.invitations import accept_invitation
from api.schemas.invitation import InvitationAccept
from api.security import hash_password
from api.timeutils import utcnow


@pytest.mark.integration
def test_concurrent_invitation_acceptance_has_one_winner(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'invitation-race.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    commit_barrier = Barrier(2, timeout=10)

    class CoordinatedSession(Session):
        def commit(self):
            if any(
                isinstance(record, Person) and record.email == "race-member@example.com"
                for record in self.new
            ):
                commit_barrier.wait()
            return super().commit()

    SessionFactory = sessionmaker(bind=engine, class_=CoordinatedSession)
    Base.metadata.create_all(engine)
    with SessionFactory() as setup:
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
