"""What happens to a volunteer's scheduled work when they leave the organization.

Departure was an untested hole. The only coverage was a delete of a person who
held no assignments, which asserted a 404 and nothing else, so the fate of a
departing volunteer's shifts was undefined by the test suite.

There are two ways a person could plausibly leave: a soft deactivation
(`Person.status` carries "active"/"inactive"/"invited", and `get_current_user`
already refuses anything but "active") and a hard `DELETE /api/v1/people/{id}`.
Only the hard delete is reachable — no route ever writes `status`, and
`PersonUpdate` has no `status` field — so departure is always a row delete.

That delete runs through `Person.assignments`, declared
`cascade="all, delete-orphan"`, which removes *every* assignment the person
held: future and past, manual and solver-generated, published and draft, and
without regard to tenant. Compare `replace_person_roles`
(`api/services/qualification_service.py`), which reopens only future live work,
keeps past work as completed history, leaves draft candidates alone so
publication validation can reject them explicitly, and scopes itself to one
org. `tests/api/test_solution_publication_safety.py
::test_removing_qualification_reopens_only_future_live_work` pins that contract.

These tests pin what departure ACTUALLY does today, including the places where
it contradicts that precedent. They are deliberately written against real
behavior, not desired behavior.
"""

from datetime import timedelta

import pytest

from api.models import (
    Assignment,
    AuditLog,
    Constraint,
    Event,
    Notification,
    Organization,
    Person,
    Solution,
)
from api.services.publication_service import capture_solution_scope
from api.timeutils import utcnow
from tests.api.conftest import (
    accept_invitation,
    auth_headers,
    seed_event,
    seed_invitation,
    seed_org,
    seed_user,
)

ORG = "departure-org"
ADMIN_EMAIL = "admin@departure.org"
ADMIN_PW = "AdminPass123!"
VOL_EMAIL = "sarah@departure.org"
VOL_PW = "VolPass123!"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _admin(client, org_id=ORG, email=ADMIN_EMAIL, password=ADMIN_PW):
    """Bootstrap an organization and its first admin, returning auth headers."""
    seed_org(client, org_id)
    seed_user(client, org_id, email, "Admin", password)
    return auth_headers(client, email, password)


def _volunteer(client, headers, org_id=ORG, email=VOL_EMAIL, name="Sarah", password=VOL_PW):
    """Add a volunteer the supported way: admin invitation, then acceptance."""
    invitation = seed_invitation(client, headers, org_id, email, name, roles=["usher"])
    return accept_invitation(client, invitation["token"], password=password)


def _past_event(db, org_id, event_id, days_ago=7, roles=None):
    """Seed a finished event directly.

    The API would accept one too: ``validate_time_range`` only requires
    ``end > start``, never that the start is in the future. Seeding the row
    keeps this helper independent of that, since what these tests need is a
    past event, not a test of how past events are created.
    """
    start = utcnow() - timedelta(days=days_ago)
    row = Event(
        id=event_id,
        org_id=org_id,
        type="Sunday Service",
        start_time=start,
        end_time=start + timedelta(hours=2),
        extra_data={"role_counts": roles or {"usher": 1}},
    )
    db.add(row)
    db.commit()
    return row


def _published_solution(db, org_id, events, assignments):
    """A published solution holding the given (event_id, person_id, role) work."""
    constraints = db.query(Constraint).filter(Constraint.org_id == org_id).all()
    scope = capture_solution_scope(
        events,
        range_start=min(e.start_time.date() for e in events),
        range_end=max(e.start_time.date() for e in events),
        constraints=constraints,
    )
    solution = Solution(
        org_id=org_id,
        solve_ms=1.0,
        hard_violations=0,
        soft_score=1.0,
        health_score=100.0,
        metrics={},
        scope_start=scope.range_start,
        scope_end=scope.range_end,
        scope_event_ids=scope.event_ids,
        scope_fingerprint=scope.fingerprint,
        is_published=True,
        published_at=utcnow(),
    )
    db.add(solution)
    db.flush()
    for event_id, person_id, role in assignments:
        db.add(
            Assignment(
                solution_id=solution.id,
                event_id=event_id,
                person_id=person_id,
                role=role,
            )
        )
    db.commit()
    db.refresh(solution)
    return solution


def _event_row(db, org_id, event_id):
    return db.query(Event).filter(Event.org_id == org_id, Event.id == event_id).one()


def _assignments_in_org(db, org_id):
    """Assignment carries no org_id, so reach the tenant through its event."""
    return (
        db.query(Assignment)
        .join(Event, Event.id == Assignment.event_id)
        .filter(Event.org_id == org_id)
        .all()
    )


@pytest.mark.no_mock_auth
class TestPersonDeparture:
    # -- future work on a published solution --------------------------------

    def test_future_published_assignment_is_deleted_with_the_person(self, client, db):
        """The departing volunteer's future shift vanishes from the live schedule."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        event = seed_event(client, headers, ORG, "departure-future", role_counts={"usher": 1})
        solution = _published_solution(
            db,
            ORG,
            [_event_row(db, ORG, event["id"])],
            [(event["id"], volunteer["person_id"], "usher")],
        )

        removed = client.delete(f"/api/v1/people/{volunteer['person_id']}", headers=headers)
        assert removed.status_code == 204, removed.text

        db.expire_all()
        assert (
            _assignments_in_org(db, ORG) == []
        ), "the future assignment outlived neither the person nor the published solution"
        # The solution row itself survives, still flagged published.
        assert db.query(Solution).filter(Solution.org_id == ORG).one().is_published is True
        assert solution.id is not None

    def test_published_roster_silently_shrinks(self, client, db):
        """The published solution still reads as published, just with nobody on it."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        event = seed_event(client, headers, ORG, "departure-roster", role_counts={"usher": 1})
        solution = _published_solution(
            db,
            ORG,
            [_event_row(db, ORG, event["id"])],
            [(event["id"], volunteer["person_id"], "usher")],
        )
        solution_id = solution.id

        before = client.get(f"/api/v1/solutions/{solution_id}/assignments", headers=headers)
        assert before.json()["total_assignments"] == 1

        client.delete(f"/api/v1/people/{volunteer['person_id']}", headers=headers)

        after = client.get(f"/api/v1/solutions/{solution_id}/assignments", headers=headers)
        assert after.status_code == 200, after.text
        assert after.json()["total_assignments"] == 0
        assert after.json()["events"] == [], "the event dropped out of the roster entirely"

        detail = client.get(f"/api/v1/solutions/{solution_id}", headers=headers)
        assert detail.json()["is_published"] is True
        assert detail.json()["assignment_count"] == 0

    def test_departure_is_recorded_in_the_audit_trail(self, client, db):
        """Erasing a member is destructive, so it must leave a trace."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        event = seed_event(client, headers, ORG, "departure-silent", role_counts={"usher": 1})
        _published_solution(
            db,
            ORG,
            [_event_row(db, ORG, event["id"])],
            [(event["id"], volunteer["person_id"], "usher")],
        )

        client.delete(f"/api/v1/people/{volunteer['person_id']}", headers=headers)

        db.expire_all()
        entries = (
            db.query(AuditLog)
            .filter(AuditLog.organization_id == ORG, AuditLog.resource_type == "person")
            .all()
        )
        assert [entry.action for entry in entries] == ["user.deleted"]
        assert entries[0].resource_id == volunteer["person_id"]
        # The assignees are not notified here: a hard delete removes the person
        # who would be told. Deactivation is the path that keeps them reachable.
        assert db.query(Notification).filter(Notification.org_id == ORG).count() == 0

    def test_short_staffing_only_shows_up_in_event_validation(self, client, db):
        """The one place the gap surfaces is the on-demand validation endpoint."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        event = seed_event(client, headers, ORG, "departure-validate", role_counts={"usher": 1})

        healthy = client.get(f"/api/v1/events/{event['id']}/validation", headers=headers)
        assert healthy.status_code == 200, healthy.text
        assert healthy.json()["is_valid"] is True

        client.delete(f"/api/v1/people/{volunteer['person_id']}", headers=headers)

        degraded = client.get(f"/api/v1/events/{event['id']}/validation", headers=headers)
        assert degraded.json()["is_valid"] is False
        kinds = [w["type"] for w in degraded.json()["warnings"]]
        assert "insufficient_people" in kinds
        # Note: this counts qualified people in the org, not unfilled assignments.
        # It fires whether or not the departed person was ever scheduled.

    # -- past work: the qualification-removal precedent ----------------------

    def test_past_assignment_is_destroyed_unlike_qualification_removal(self, client, db):
        """Completed history goes too — the opposite of removing a qualification."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        past = _past_event(db, ORG, "departure-past")
        future = seed_event(client, headers, ORG, "departure-next", role_counts={"usher": 1})
        _published_solution(
            db,
            ORG,
            [past, _event_row(db, ORG, future["id"])],
            [
                (past.id, volunteer["person_id"], "usher"),
                (future["id"], volunteer["person_id"], "usher"),
            ],
        )
        assert len(_assignments_in_org(db, ORG)) == 2

        client.delete(f"/api/v1/people/{volunteer['person_id']}", headers=headers)

        db.expire_all()
        # replace_person_roles keeps the past row and reopens only the future
        # one. Departure keeps neither.
        assert (
            _assignments_in_org(db, ORG) == []
        ), "past work was erased; qualification removal preserves it as history"
        assert _event_row(db, ORG, past.id) is not None, "the past event itself survives"

    def test_manual_and_draft_work_is_deleted_too(self, client, db):
        """Draft candidates survive qualification removal; they do not survive departure."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        event = seed_event(client, headers, ORG, "departure-draft", role_counts={"usher": 1})

        # Manual assignment through the supported endpoint.
        assigned = client.post(
            f"/api/v1/events/{event['id']}/assignments",
            json={"person_id": volunteer["person_id"], "action": "assign", "role": "usher"},
            headers=headers,
        )
        assert assigned.status_code == 200, assigned.text

        # An unpublished draft holding the same person.
        draft = Solution(
            org_id=ORG,
            solve_ms=1.0,
            hard_violations=0,
            soft_score=1.0,
            health_score=100.0,
            metrics={},
            is_published=False,
        )
        db.add(draft)
        db.flush()
        db.add(
            Assignment(
                solution_id=draft.id,
                event_id=event["id"],
                person_id=volunteer["person_id"],
                role="usher",
            )
        )
        db.commit()
        draft_id = draft.id
        assert len(_assignments_in_org(db, ORG)) == 2

        client.delete(f"/api/v1/people/{volunteer['person_id']}", headers=headers)

        db.expire_all()
        assert _assignments_in_org(db, ORG) == []
        # The draft solution row survives, now empty.
        assert db.query(Solution).filter(Solution.org_id == ORG, Solution.id == draft_id).one()

    # -- tenancy ------------------------------------------------------------

    def test_departure_does_not_touch_another_organizations_data(self, client, db):
        """One tenant's departure leaves the other tenant's roster untouched."""
        other_org = "departure-other-org"
        other_admin_email = "admin@departure-other.org"

        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        event = seed_event(client, headers, ORG, "departure-mine", role_counts={"usher": 1})
        _published_solution(
            db,
            ORG,
            [_event_row(db, ORG, event["id"])],
            [(event["id"], volunteer["person_id"], "usher")],
        )

        other_headers = _admin(client, other_org, other_admin_email)
        other_volunteer = _volunteer(
            client, other_headers, other_org, "vol@departure-other.org", "Ravi"
        )
        other_event = seed_event(
            client, other_headers, other_org, "departure-theirs", role_counts={"usher": 1}
        )
        _published_solution(
            db,
            other_org,
            [_event_row(db, other_org, other_event["id"])],
            [(other_event["id"], other_volunteer["person_id"], "usher")],
        )

        client.delete(f"/api/v1/people/{volunteer['person_id']}", headers=headers)

        db.expire_all()
        assert _assignments_in_org(db, ORG) == []
        surviving = _assignments_in_org(db, other_org)
        assert len(surviving) == 1
        assert surviving[0].person_id == other_volunteer["person_id"]
        assert (
            db.query(Person)
            .filter(Person.org_id == other_org, Person.id == other_volunteer["person_id"])
            .one()
            is not None
        )

    def test_admin_cannot_remove_someone_from_another_organization(self, client, db):
        """Cross-tenant delete is refused before any cascade runs."""
        other_org = "departure-foreign-org"
        headers = _admin(client)
        other_headers = _admin(client, other_org, "admin@departure-foreign.org")
        other_volunteer = _volunteer(
            client, other_headers, other_org, "vol@departure-foreign.org", "Mei"
        )

        refused = client.delete(f"/api/v1/people/{other_volunteer['person_id']}", headers=headers)
        assert refused.status_code == 403, refused.text
        assert (
            db.query(Person)
            .filter(Person.org_id == other_org, Person.id == other_volunteer["person_id"])
            .count()
            == 1
        )

    def test_cascade_reaches_the_persons_work_in_a_foreign_orgs_event(self, client, db):
        """The cascade is person-scoped, not org-scoped, unlike qualification removal.

        `replace_person_roles` filters on `Event.org_id == person.org_id`, so an
        assignment pointing at another tenant's event is left alone. The delete
        cascade has no such filter and takes it with everything else.
        """
        headers = _admin(client)
        volunteer = _volunteer(client, headers)

        foreign_org = Organization(id="departure-cascade-foreign", name="Foreign")
        start = utcnow() + timedelta(days=7)
        foreign_event = Event(
            id="departure-cascade-foreign-event",
            org_id=foreign_org.id,
            type="Foreign service",
            start_time=start,
            end_time=start + timedelta(hours=2),
            extra_data={"role_counts": {"usher": 1}},
        )
        foreign_assignment = Assignment(
            event_id=foreign_event.id,
            person_id=volunteer["person_id"],
            role="usher",
        )
        db.add_all([foreign_org, foreign_event, foreign_assignment])
        db.commit()
        foreign_assignment_id = foreign_assignment.id

        client.delete(f"/api/v1/people/{volunteer['person_id']}", headers=headers)

        db.expire_all()
        assert (
            db.query(Assignment)
            .join(Event, Event.id == Assignment.event_id)
            .filter(Event.org_id == foreign_org.id, Assignment.id == foreign_assignment_id)
            .first()
            is None
        ), "the cross-tenant assignment was cascaded away with the person"

    # -- access after departure ---------------------------------------------

    def test_departed_persons_token_is_rejected(self, client, db):
        """A token issued before departure stops working once the row is gone."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        vol_headers = auth_headers(client, VOL_EMAIL, VOL_PW)
        assert client.get("/api/v1/people/me", headers=vol_headers).status_code == 200

        client.delete(f"/api/v1/people/{volunteer['person_id']}", headers=headers)

        rejected = client.get("/api/v1/people/me", headers=vol_headers)
        assert rejected.status_code == 401, rejected.text

        relogin = client.post("/api/v1/auth/login", json={"email": VOL_EMAIL, "password": VOL_PW})
        assert relogin.status_code == 401, relogin.text

    def test_there_is_no_soft_deactivate_path(self, client, db):
        """`Person.status` is enforced at auth but no route can ever set it.

        `get_current_user` requires `Person.status == "active"`, so a soft
        departure would work if anything wrote the column. `PersonUpdate` has no
        `status` field, so the value is silently dropped and the person stays
        fully active.
        """
        headers = _admin(client)
        volunteer = _volunteer(client, headers)

        attempted = client.put(
            f"/api/v1/people/{volunteer['person_id']}",
            json={"status": "inactive"},
            headers=headers,
        )
        assert attempted.status_code == 200, attempted.text
        assert "status" not in attempted.json()

        db.expire_all()
        person = (
            db.query(Person).filter(Person.org_id == ORG, Person.id == volunteer["person_id"]).one()
        )
        assert person.status == "active", "there is no reachable deactivation path"
        assert (
            client.post(
                "/api/v1/auth/login", json={"email": VOL_EMAIL, "password": VOL_PW}
            ).status_code
            == 200
        )


@pytest.mark.no_mock_auth
class TestPersonDeactivation:
    """Deactivation is the departure path that keeps a member's history.

    A hard delete cascades through ``Person.assignments`` and erases completed
    work along with future work, silently rewriting a published record.
    Deactivating keeps the row, so past assignments survive, while future live
    work reopens exactly as a qualification removal would reopen it.
    """

    def test_deactivation_reopens_future_live_work(self, client, db):
        """The future shift is released so an admin can refill it."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        event = seed_event(client, headers, ORG, "deact-future", role_counts={"usher": 1})
        _published_solution(
            db,
            ORG,
            [_event_row(db, ORG, event["id"])],
            [(event["id"], volunteer["person_id"], "usher")],
        )

        resp = client.post(f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=headers)
        assert resp.status_code == 200, resp.text

        db.expire_all()
        assert (
            db.query(Assignment)
            .filter(Assignment.event_id == event["id"])
            .filter(Assignment.person_id == volunteer["person_id"])
            .count()
            == 0
        )

    def test_deactivation_preserves_past_work(self, client, db):
        """Completed history must survive, unlike under a hard delete."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        past = _past_event(db, ORG, "deact-past")
        _published_solution(db, ORG, [past], [(past.id, volunteer["person_id"], "usher")])

        client.post(f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=headers)

        db.expire_all()
        assert (
            db.query(Assignment)
            .join(Event, Assignment.event_id == Event.id)
            .filter(Event.org_id == ORG, Assignment.person_id == volunteer["person_id"])
            .count()
            == 1
        ), "deactivation must not erase completed history"

    def test_deactivated_person_keeps_their_row(self, client, db):
        """The person is retired, not erased, so the roster can still name them."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)

        client.post(f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=headers)

        db.expire_all()
        row = (
            db.query(Person)
            .filter(Person.org_id == ORG, Person.id == volunteer["person_id"])
            .first()
        )
        assert row is not None
        assert row.status == "inactive"

    def test_deactivated_person_cannot_log_in(self, client, db):
        """get_current_user already refuses a non-active person."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        vol_headers = auth_headers(client, VOL_EMAIL, VOL_PW)

        client.post(f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=headers)

        assert client.get("/api/v1/people/me", headers=vol_headers).status_code == 401
        login = client.post("/api/v1/auth/login", json={"email": VOL_EMAIL, "password": VOL_PW})
        assert login.status_code == 401

    def test_deactivation_is_recorded_in_the_audit_trail(self, client, db):
        """Retiring a member is an administrative act worth recording."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)

        client.post(f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=headers)

        db.expire_all()
        entries = (
            db.query(AuditLog)
            .filter(AuditLog.organization_id == ORG, AuditLog.resource_type == "person")
            .all()
        )
        assert [entry.action for entry in entries] == ["user.updated"]
        assert entries[0].details["change"] == "deactivated"

    def test_admin_cannot_deactivate_themselves(self, client, db):
        """Locking yourself out of your own organization is never intended."""
        headers = _admin(client)
        me = client.get("/api/v1/people/me", headers=headers).json()

        resp = client.post(f"/api/v1/people/{me['id']}/deactivate", headers=headers)

        assert resp.status_code == 400

    def test_deactivation_is_refused_across_tenants(self, client, db):
        """One organization's admin cannot retire another's member."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        other = _admin(
            client,
            org_id="departure-other",
            email="admin@departure-other.org",
            password="OtherPass123!",
        )

        resp = client.post(f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=other)

        assert resp.status_code == 403
        db.expire_all()
        row = (
            db.query(Person)
            .filter(Person.org_id == ORG, Person.id == volunteer["person_id"])
            .first()
        )
        assert row.status == "active"

    def test_volunteer_cannot_deactivate_anyone(self, client, db):
        """Deactivation is an admin action."""
        headers = _admin(client)
        _volunteer(client, headers)
        peer = _volunteer(
            client, headers, email="peer@departure.org", name="Peer", password="PeerPass123!"
        )
        vol_headers = auth_headers(client, VOL_EMAIL, VOL_PW)

        resp = client.post(f"/api/v1/people/{peer['person_id']}/deactivate", headers=vol_headers)

        assert resp.status_code == 403


@pytest.mark.no_mock_auth
class TestDeactivatedPeopleAreNotScheduled:
    """Deactivation must also stop future work being created for the person.

    Releasing their existing shifts is only half of leaving. The solver loaded
    every Person row in the organization, so the next solve handed the freed
    shift straight back to someone who can no longer sign in to see it, and the
    coordinator had no way to tell from the roster that it would never be
    served.
    """

    def test_solver_does_not_assign_work_to_a_deactivated_person(self, client, db):
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        event = seed_event(client, headers, ORG, "solve-after-deact", role_counts={"usher": 1})

        deactivated = client.post(
            f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=headers
        )
        assert deactivated.status_code == 200, deactivated.text

        start = (utcnow() + timedelta(days=13)).date()
        end = (utcnow() + timedelta(days=15)).date()
        solved = client.post(
            "/api/v1/solver/solve",
            json={
                "org_id": ORG,
                "from_date": start.isoformat(),
                "to_date": end.isoformat(),
            },
            headers=headers,
        )
        assert solved.status_code == 200, solved.text

        db.expire_all()
        assigned = (
            db.query(Assignment)
            .filter(
                Assignment.event_id == event["id"],
                Assignment.person_id == volunteer["person_id"],
            )
            .count()
        )
        assert assigned == 0, "the solver scheduled someone who cannot sign in"

    def test_solver_still_assigns_active_people(self, client, db):
        """The converse, so the filter cannot pass by excluding everyone."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        event = seed_event(client, headers, ORG, "solve-active", role_counts={"usher": 1})

        start = (utcnow() + timedelta(days=13)).date()
        end = (utcnow() + timedelta(days=15)).date()
        solved = client.post(
            "/api/v1/solver/solve",
            json={
                "org_id": ORG,
                "from_date": start.isoformat(),
                "to_date": end.isoformat(),
            },
            headers=headers,
        )
        assert solved.status_code == 200, solved.text

        db.expire_all()
        assert (
            db.query(Assignment)
            .filter(
                Assignment.event_id == event["id"],
                Assignment.person_id == volunteer["person_id"],
            )
            .count()
            == 1
        ), "an active, qualified volunteer was not scheduled"
