"""Tenant-bound access-token and active-membership regressions."""

import pytest
from jose import jwt

from api.models import Person
from api.security import ALGORITHM, SECRET_KEY, create_access_token
from api.timeutils import utcnow
from tests.api.conftest import seed_org, seed_user

pytestmark = pytest.mark.no_mock_auth


def _account(client, db, *, org_id: str, email: str):
    seed_org(client, org_id)
    auth = seed_user(client, org_id, email=email, name="Tenant Admin", password="Pass1234!")
    person = db.query(Person).filter(Person.email == email, Person.org_id == org_id).one()
    return person, auth


def test_every_issued_access_token_carries_the_account_tenant(client, db):
    person, signup = _account(client, db, org_id="token-org", email="owner@token.example")

    login = client.post(
        "/api/v1/auth/login",
        json={"email": person.email, "password": "Pass1234!"},
    )
    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login.json()["refresh_token"]},
    )

    assert refresh.status_code == 200, refresh.text
    for token in (signup["token"], login.json()["token"], refresh.json()["token"]):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == person.id
        assert payload["org_id"] == "token-org"


@pytest.mark.parametrize("token_org_id", [None, "foreign-org"])
def test_access_token_requires_matching_tenant_claim(client, db, token_org_id):
    person, _ = _account(client, db, org_id="member-org", email="member@token.example")
    claims = {"sub": person.id, "pwd_iat": utcnow().timestamp()}
    if token_org_id is not None:
        claims["org_id"] = token_org_id
    token = create_access_token(claims)

    response = client.get(
        "/api/v1/people/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_inactive_membership_revokes_login_access_and_refresh(client, db):
    person, signup = _account(client, db, org_id="inactive-org", email="inactive@token.example")
    person.status = "inactive"
    db.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": person.email, "password": "Pass1234!"},
    )
    access = client.get(
        "/api/v1/people/me",
        headers={"Authorization": f"Bearer {signup['token']}"},
    )
    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": signup["refresh_token"]},
    )

    assert login.status_code == 401
    assert access.status_code == 401
    assert refresh.status_code == 401
