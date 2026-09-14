"""Atomic organization bootstrap and membership-boundary regressions."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.models import Base, Organization, Person
from api.routers.auth import SignupRequest, signup

pytestmark = pytest.mark.no_mock_auth


def _payload(**overrides):
    payload = {
        "org_id": "bootstrap-church",
        "org_name": "Bootstrap Church",
        "name": "Owner",
        "email": "owner@bootstrap.example.com",
        "password": "StrongPass123!",
    }
    payload.update(overrides)
    return payload


def test_signup_atomically_creates_organization_and_exact_admin(client, db):
    response = client.post("/api/v1/auth/signup", json=_payload())

    assert response.status_code == 201
    assert response.json()["roles"] == ["admin"]
    assert db.query(Organization).filter_by(id="bootstrap-church").one().name == "Bootstrap Church"
    assert db.query(Person).filter_by(org_id="bootstrap-church").one().roles == ["admin"]


def test_existing_organization_cannot_be_joined_without_invitation(client, db):
    db.add(Organization(id="bootstrap-church", name="Existing Church", config={}))
    db.commit()

    response = client.post("/api/v1/auth/signup", json=_payload())

    assert response.status_code == 409
    assert db.query(Person).filter_by(org_id="bootstrap-church").count() == 0
    assert db.query(Organization).filter_by(id="bootstrap-church").one().name == "Existing Church"


def test_signup_rejects_caller_supplied_roles_without_side_effects(client, db):
    response = client.post(
        "/api/v1/auth/signup",
        json=_payload(roles=["Admin", "worship_leader"]),
    )

    assert response.status_code == 422
    assert db.query(Organization).filter_by(id="bootstrap-church").count() == 0
    assert db.query(Person).filter_by(email="owner@bootstrap.example.com").count() == 0


@pytest.mark.parametrize("field", ["timezone", "language"])
def test_signup_rejects_null_account_preferences_without_side_effects(client, db, field):
    response = client.post("/api/v1/auth/signup", json=_payload(**{field: None}))

    assert response.status_code == 422
    assert db.query(Organization).filter_by(id="bootstrap-church").count() == 0
    assert db.query(Person).filter_by(email="owner@bootstrap.example.com").count() == 0


def test_duplicate_email_rolls_back_new_organization(client, db):
    first = client.post(
        "/api/v1/auth/signup",
        json=_payload(org_id="first-org", org_name="First Org"),
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/auth/signup",
        json=_payload(org_id="second-org", org_name="Second Org"),
    )

    assert second.status_code == 409
    assert db.query(Organization).filter_by(id="second-org").count() == 0
    assert db.query(Person).filter_by(org_id="second-org").count() == 0


def test_concurrent_bootstrap_creates_one_owner(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'bootstrap.db'}",
        connect_args={"check_same_thread": False, "timeout": 10},
    )
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    request = SignupRequest(**_payload())

    def attempt():
        db = sessions()
        try:
            signup(request, db)
            return 201
        except HTTPException as exc:
            return exc.status_code
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = sorted(executor.map(lambda _: attempt(), range(2)))

    with sessions() as db:
        assert results == [201, 409]
        assert db.query(Organization).filter_by(id="bootstrap-church").count() == 1
        owners = db.query(Person).filter_by(org_id="bootstrap-church").all()
        assert len(owners) == 1
        assert owners[0].roles == ["admin"]

    engine.dispose()
