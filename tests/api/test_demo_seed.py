"""`make setup` loads a demo organization and prints logins that work.

A new contributor who finishes setup should be able to sign in and see a
schedule being made, without first inventing an organization, inviting people
and creating events by hand. The demo mirrors ``examples/church`` so the data
in the app matches the walkthrough in the README.
"""

from datetime import timedelta
from pathlib import Path

import pytest
import yaml

from api.demo_seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ORG_ID,
    DEMO_PASSWORD,
    DemoSeedRefusedError,
    seed_demo,
)
from api.models import Event, Organization, Person
from api.security import verify_password
from api.timeutils import utcnow

REPO_ROOT = Path(__file__).resolve().parents[2]


def _people(db):
    return db.query(Person).filter(Person.org_id == DEMO_ORG_ID).all()


class TestDemoSeedContents:
    def test_it_creates_one_organization_with_an_admin(self, db):
        seed_demo(db)
        assert db.query(Organization).filter(Organization.id == DEMO_ORG_ID).count() == 1
        admin = db.query(Person).filter(Person.email == DEMO_ADMIN_EMAIL).one()
        assert admin.org_id == DEMO_ORG_ID
        assert admin.roles == ["admin"]
        assert admin.status == "active"

    def test_every_login_uses_the_printed_password(self, db):
        result = seed_demo(db)
        assert result.logins, "setup would print no logins"
        for login in result.logins:
            person = db.query(Person).filter(Person.email == login.email).one()
            assert verify_password(DEMO_PASSWORD, person.password_hash)

    def test_volunteers_mirror_the_church_example(self, db):
        """The demo is the README's Church walkthrough, not a second dataset."""
        seed_demo(db)
        example = yaml.safe_load((REPO_ROOT / "examples/church/people.yaml").read_text())
        expected = {p["name"]: set(p["roles"]) for p in example["people"]}
        volunteers = {
            p.name: set(p.roles) - {"volunteer"}
            for p in _people(db)
            if "volunteer" in (p.roles or [])
        }
        assert volunteers == expected

    def test_volunteers_hold_exactly_one_permission_role(self, db):
        seed_demo(db)
        for person in _people(db):
            permissions = {"admin", "volunteer"} & set(person.roles or [])
            assert len(permissions) == 1, (person.name, person.roles)

    def test_events_are_upcoming_and_carry_role_counts(self, db):
        """Fixed dates go stale; the demo has to be in the future whenever it is loaded."""
        seed_demo(db)
        events = db.query(Event).filter(Event.org_id == DEMO_ORG_ID).all()
        assert len(events) >= 6
        now = utcnow()
        for event in events:
            assert now < event.start_time < now + timedelta(days=60)
            assert event.extra_data["role_counts"], event.id

    def test_emails_are_reserved_and_undeliverable(self, db):
        """Compose turns email on, so demo addresses must never reach a real inbox."""
        seed_demo(db)
        assert all(p.email.endswith("@example.com") for p in _people(db))


class TestDemoSeedIsSafeToRepeat:
    def test_second_run_changes_nothing(self, db):
        first = seed_demo(db)
        people = len(_people(db))
        second = seed_demo(db)
        assert first.created is True
        assert second.created is False
        assert len(_people(db)) == people
        assert second.logins == first.logins

    def test_it_never_touches_another_organization(self, db):
        db.add(Organization(id="real-org", name="Real Org"))
        db.commit()
        seed_demo(db)
        assert db.query(Organization).filter(Organization.id == "real-org").one().name == (
            "Real Org"
        )

    def test_it_refuses_a_production_environment(self, db, monkeypatch):
        """The demo password is published in the README."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        with pytest.raises(DemoSeedRefusedError):
            seed_demo(db)
        assert db.query(Organization).count() == 0


@pytest.mark.no_mock_auth
class TestDemoLoginsWork:
    def test_admin_can_sign_in_with_the_printed_login(self, client, db):
        seed_demo(db)
        resp = client.post(
            "/api/v1/auth/login", json={"email": DEMO_ADMIN_EMAIL, "password": DEMO_PASSWORD}
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["org_id"] == DEMO_ORG_ID

    def test_the_solver_can_staff_the_demo(self, client, db):
        """The point of the demo is to watch a schedule get made."""
        seed_demo(db)
        token = client.post(
            "/api/v1/auth/login", json={"email": DEMO_ADMIN_EMAIL, "password": DEMO_PASSWORD}
        ).json()["token"]
        today = utcnow().date()
        resp = client.post(
            "/api/v1/solver/solve",
            json={
                "org_id": DEMO_ORG_ID,
                "from_date": today.isoformat(),
                "to_date": (today + timedelta(days=60)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["metrics"]["hard_violations"] == 0, body
        assert body["assignment_count"] > 0, body
