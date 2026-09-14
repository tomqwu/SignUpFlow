"""Membership entry points share one access-role policy."""

import pytest

from api.models import Invitation, Person
from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin(client, org_id: str):
    seed_org(client, org_id, name=f"Organization {org_id}")
    seed_user(
        client,
        org_id,
        email=f"owner-{org_id}@example.com",
        name="Owner",
        password="OwnerPass1!",
    )
    return auth_headers(client, f"owner-{org_id}@example.com", "OwnerPass1!")


@pytest.mark.no_mock_auth
def test_invitation_defaults_qualification_only_roles_to_volunteer(client):
    headers = _admin(client, "role-invite-default")

    response = client.post(
        "/api/v1/invitations?org_id=role-invite-default",
        headers=headers,
        json={"email": "usher@example.com", "name": "Usher", "roles": ["usher"]},
    )

    assert response.status_code == 201, response.text
    assert response.json()["roles"] == ["volunteer", "usher"]


@pytest.mark.no_mock_auth
@pytest.mark.parametrize("roles", [["Admin"], ["admin", "volunteer"]])
def test_invitation_rejects_ambiguous_access_roles(client, db, roles):
    headers = _admin(client, "role-invite-reject")

    response = client.post(
        "/api/v1/invitations?org_id=role-invite-reject",
        headers=headers,
        json={"email": "member@example.com", "name": "Member", "roles": roles},
    )

    assert response.status_code == 400
    assert db.query(Invitation).filter_by(email="member@example.com").count() == 0


@pytest.mark.no_mock_auth
def test_invitation_accept_body_cannot_override_org_or_roles(client, db):
    headers = _admin(client, "role-invite-accept")
    invitation = client.post(
        "/api/v1/invitations?org_id=role-invite-accept",
        headers=headers,
        json={
            "email": "invitee@example.com",
            "name": "Invitee",
            "roles": ["volunteer", "coach"],
        },
    ).json()

    response = client.post(
        f"/api/v1/invitations/{invitation['token']}/accept",
        json={
            "password": "InviteePass1!",
            "timezone": "UTC",
            "org_id": "other-org",
            "roles": ["admin"],
        },
    )

    assert response.status_code == 422
    assert db.query(Person).filter_by(email="invitee@example.com").count() == 0
    assert db.query(Invitation).filter_by(id=invitation["id"]).one().status == "pending"


@pytest.mark.no_mock_auth
def test_person_create_and_update_enforce_role_policy_before_mutation(client, db):
    headers = _admin(client, "role-person")
    created = client.post(
        "/api/v1/people/",
        headers=headers,
        json={
            "id": "role-person-member",
            "org_id": "role-person",
            "name": "Original Name",
            "roles": ["teacher"],
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["roles"] == ["volunteer", "teacher"]

    rejected = client.put(
        "/api/v1/people/role-person-member",
        headers=headers,
        json={"name": "Changed Name", "roles": ["admin", "volunteer"]},
    )

    assert rejected.status_code == 400
    db.expire_all()
    member = db.query(Person).filter_by(id="role-person-member").one()
    assert member.name == "Original Name"
    assert member.roles == ["volunteer", "teacher"]


@pytest.mark.no_mock_auth
def test_bulk_people_reports_invalid_roles_without_creating_row(client, db):
    headers = _admin(client, "role-bulk")

    response = client.post(
        "/api/v1/people/bulk?org_id=role-bulk",
        headers=headers,
        json={
            "items": [
                {"id": "valid", "name": "Valid", "roles": ["scorekeeper"]},
                {"id": "invalid", "name": "Invalid", "roles": ["VOLUNTEER"]},
            ]
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["created"] == 1
    assert response.json()["errors"][0]["id"] == "invalid"
    assert db.query(Person).filter_by(id="valid").one().roles == ["volunteer", "scorekeeper"]
    assert db.query(Person).filter_by(id="invalid").count() == 0


@pytest.mark.no_mock_auth
def test_person_email_conflicts_are_rejected_without_partial_updates(client, db):
    headers = _admin(client, "email-conflicts")
    owner = db.query(Person).filter_by(org_id="email-conflicts").one()

    create = client.post(
        "/api/v1/people/",
        headers=headers,
        json={
            "id": "duplicate-email",
            "org_id": "email-conflicts",
            "name": "Duplicate",
            "email": owner.email,
        },
    )
    assert create.status_code == 409
    assert db.query(Person).filter_by(id="duplicate-email").count() == 0

    member = client.post(
        "/api/v1/people/",
        headers=headers,
        json={
            "id": "email-member",
            "org_id": "email-conflicts",
            "name": "Original",
            "email": "original@example.com",
        },
    )
    assert member.status_code == 201
    update = client.put(
        "/api/v1/people/email-member",
        headers=headers,
        json={"name": "Changed", "email": owner.email},
    )
    assert update.status_code == 409
    db.expire_all()
    persisted = db.query(Person).filter_by(id="email-member").one()
    assert persisted.name == "Original"
    assert persisted.email == "original@example.com"


@pytest.mark.no_mock_auth
def test_bulk_people_rejects_duplicate_emails_atomically(client, db):
    headers = _admin(client, "bulk-email-conflicts")

    response = client.post(
        "/api/v1/people/bulk?org_id=bulk-email-conflicts",
        headers=headers,
        json={
            "items": [
                {"id": "first-email", "name": "First", "email": "same@example.com"},
                {"id": "second-email", "name": "Second", "email": "same@example.com"},
            ]
        },
    )

    assert response.status_code == 409
    assert db.query(Person).filter(Person.id.in_(["first-email", "second-email"])).count() == 0
