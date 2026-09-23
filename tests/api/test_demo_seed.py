"""`make setup` loads a demo organization that looks like a church in use.

The seed drives the public API, so these tests check what it leaves behind
through the same API and the database: a published, fully staffed schedule
with history, real responses, teams, rules and time away. What each screen
shows is covered separately in tests/web/test_demo_screens.py.
"""

import json
from collections import Counter
from datetime import timedelta
from pathlib import Path

import pytest

from api.demo_seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ORG_ID,
    DEMO_PASSWORD,
    REHEARSAL_ROLES,
    SERVICE_ROLES,
    VOLUNTEERS,
    DemoSeedConflictError,
    DemoSeedRefusedError,
    seed_demo,
)
from api.models import Assignment, Event, Organization, Person, RecurringSeries, Solution
from api.timeutils import utcnow

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _quiet_providers(monkeypatch):
    monkeypatch.setenv("DISABLE_RATE_LIMITS", "true")
    monkeypatch.setenv("EMAIL_ENABLED", "false")


def _admin_token(client):
    response = client.post(
        "/api/v1/auth/login", json={"email": DEMO_ADMIN_EMAIL, "password": DEMO_PASSWORD}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}


@pytest.mark.no_mock_auth
class TestDemoIsARealisticChurch:
    def test_roles_are_the_church_playbook(self):
        """The demo is the README's Church playbook, not a second dataset."""
        playbook = json.loads((REPO_ROOT / "docs/playbooks/church.json").read_text())
        assert SERVICE_ROLES == playbook["roles"]
        assert set(REHEARSAL_ROLES) <= set(playbook["roles"])

    def test_every_slot_has_two_qualified_people(self):
        """One absence must never leave a service uncovered."""
        qualified = Counter(q for _name, quals in VOLUNTEERS for q in quals)
        for role, count in SERVICE_ROLES.items():
            assert qualified[role] >= 2 * count, role

    def test_one_published_schedule_covers_history_and_six_weeks(self, client, db):
        result = seed_demo(client)
        assert result.created
        published = (
            db.query(Solution)
            .filter(Solution.org_id == DEMO_ORG_ID, Solution.is_published.is_(True))
            .all()
        )
        assert len(published) == 1
        events = db.query(Event).filter(Event.org_id == DEMO_ORG_ID).all()
        now = utcnow()
        assert any(e.start_time < now for e in events), "no history"
        assert any(e.start_time > now + timedelta(weeks=5) for e in events), "no horizon"

    def test_sunday_services_come_from_a_recurring_series(self, client, db):
        """The demo exercises recurring series, which the solver must staff."""
        seed_demo(client)
        services = (
            db.query(Event)
            .filter(Event.org_id == DEMO_ORG_ID, Event.type == "Sunday worship")
            .all()
        )
        assert services and all(e.series_id for e in services)
        assert db.query(RecurringSeries).filter(RecurringSeries.org_id == DEMO_ORG_ID).count() == 1

    def test_every_event_is_fully_staffed_by_qualified_people(self, client, db):
        seed_demo(client)
        people = {p.id: p for p in db.query(Person).filter(Person.org_id == DEMO_ORG_ID)}
        for event in db.query(Event).filter(Event.org_id == DEMO_ORG_ID):
            rows = db.query(Assignment).filter(Assignment.event_id == event.id).all()
            assert Counter(a.role for a in rows) == Counter(event.extra_data["role_counts"])
            for row in rows:
                assert row.role in people[row.person_id].roles

    def test_responses_look_like_a_real_week(self, client, db):
        result = seed_demo(client)
        rows = db.query(Assignment).join(Event).filter(Event.org_id == DEMO_ORG_ID).all()
        responses = Counter(a.response_status for a in rows)
        # A swap request is recorded as a decline with its own workflow status.
        swaps = [a for a in rows if a.status == "swap_requested"]
        plain_declines = [
            a for a in rows if a.response_status == "declined" and a.status != "swap_requested"
        ]
        assert responses["accepted"] >= 20
        assert len(plain_declines) == 1
        assert len(swaps) == 1 and swaps[0].decline_reason
        assert responses["pending"] > 0, "later weeks should still await replies"
        assert result.summary["swap_requests"] == 1

    def test_admin_and_printed_volunteers_can_sign_in(self, client):
        result = seed_demo(client)
        for login in result.logins:
            response = client.post(
                "/api/v1/auth/login", json={"email": login.email, "password": DEMO_PASSWORD}
            )
            assert response.status_code == 200, (login.email, response.text)
            assert response.json()["org_id"] == DEMO_ORG_ID

    def test_emails_are_reserved_and_undeliverable(self, client, db):
        seed_demo(client)
        emails = [p.email for p in db.query(Person).filter(Person.org_id == DEMO_ORG_ID)]
        assert emails and all(e.endswith("@example.com") for e in emails)


@pytest.mark.no_mock_auth
class TestDemoIsSafeToRepeat:
    def test_second_run_changes_nothing(self, client, db):
        first = seed_demo(client)
        counts = db.query(Assignment).count(), db.query(Person).count()
        second = seed_demo(client)
        assert first.created and not second.created
        assert (db.query(Assignment).count(), db.query(Person).count()) == counts
        assert second.logins == first.logins

    def test_reset_rebuilds_through_the_apps_own_delete(self, client, db):
        seed_demo(client)

        def calendar():
            return {
                (e.type, e.start_time) for e in db.query(Event).filter(Event.org_id == DEMO_ORG_ID)
            }

        first = calendar()
        again = seed_demo(client, reset=True)
        assert again.created
        assert db.query(Organization).filter(Organization.id == DEMO_ORG_ID).count() == 1
        assert calendar() == first
        assert db.query(Solution).filter(Solution.org_id == DEMO_ORG_ID).count() == 1

    def test_it_never_touches_another_organization(self, client, db):
        db.add(Organization(id="real-org", name="Real Org"))
        db.commit()
        seed_demo(client)
        seed_demo(client, reset=True)
        assert db.query(Organization).filter(Organization.id == "real-org").one().name == (
            "Real Org"
        )

    def test_it_refuses_a_production_environment(self, client, db, monkeypatch):
        """The demo password is published in the README."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        with pytest.raises(DemoSeedRefusedError):
            seed_demo(client)
        assert db.query(Organization).count() == 0

    def test_a_foreign_owner_of_the_admin_email_is_reported(self, client, db):
        client.post(
            "/api/v1/auth/signup",
            json={
                "org_id": "someone-else",
                "org_name": "Someone else",
                "region": "US",
                "name": "Someone",
                "email": DEMO_ADMIN_EMAIL,
                "password": "Different123!",
            },
        )
        with pytest.raises(DemoSeedConflictError):
            seed_demo(client)
        assert db.query(Organization).filter(Organization.id == DEMO_ORG_ID).count() == 0


@pytest.mark.no_mock_auth
def test_admin_can_run_the_solver_again_without_violations(client):
    """A coordinator's first click in the demo should not produce errors."""
    seed_demo(client)
    today = utcnow().date()
    response = client.post(
        "/api/v1/solver/solve",
        json={
            "org_id": DEMO_ORG_ID,
            "from_date": today.isoformat(),
            "to_date": (today + timedelta(weeks=6)).isoformat(),
            "change_min": True,
        },
        headers=_admin_token(client),
    )
    assert response.status_code == 200, response.text
    assert response.json()["metrics"]["hard_violations"] == 0
