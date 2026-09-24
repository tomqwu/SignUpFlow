"""Cancelling an event must tell the people who were scheduled for it.

Rescheduling an event already notifies its assignees. Cancelling one used to
delete the event and its assignments silently, so a volunteer who had accepted
a shift learned about the cancellation only by noticing it had vanished.

The notice has to outlive the event row: `Event.notifications` cascades with
`delete-orphan`, so a cancellation notice that still pointed at the event would
be deleted in the same transaction. These tests pin the surviving notice and
the self-contained snapshot the renderer needs once the event is gone.
"""

from datetime import timedelta

import pytest

from api.models import (
    Assignment,
    Event,
    Notification,
    NotificationStatus,
    NotificationType,
    Solution,
)
from api.timeutils import utcnow
from tests.api.conftest import (
    accept_invitation,
    auth_headers,
    seed_event,
    seed_invitation,
    seed_org,
    seed_user,
)

ORG = "cancel-notice-org"
ADMIN_EMAIL = "admin@cancel-notice.org"
ADMIN_PW = "AdminPass123!"
VOL_EMAIL = "sarah@cancel-notice.org"
VOL_PW = "VolPass123!"


def _org_with_assigned_volunteer(client, *, event_id="evt-cancel", days_from_now=14):
    """Admin, one volunteer, one event, and the volunteer assigned to it."""
    seed_org(client, ORG)
    seed_user(client, ORG, ADMIN_EMAIL, "Admin", ADMIN_PW)
    hdrs = auth_headers(client, ADMIN_EMAIL, ADMIN_PW)

    invitation = seed_invitation(client, hdrs, ORG, VOL_EMAIL, "Sarah", roles=["usher"])
    volunteer = accept_invitation(client, invitation["token"], password=VOL_PW)

    event = seed_event(
        client,
        hdrs,
        ORG,
        event_id,
        event_type="Sunday Worship",
        days_from_now=days_from_now,
        role_counts={"usher": 1},
    )
    assigned = client.post(
        f"/api/v1/events/{event['id']}/assignments",
        json={"person_id": volunteer["person_id"], "action": "assign", "role": "usher"},
        headers=hdrs,
    )
    assert assigned.status_code == 200, assigned.text
    return hdrs, volunteer, event


def _solution(org_id: str, *, is_published: bool) -> Solution:
    """A solution row with the score columns the schema requires."""
    return Solution(
        org_id=org_id,
        is_published=is_published,
        hard_violations=0,
        soft_score=0.0,
        health_score=100.0,
    )


def _cancellations_for(db, person_id):
    return (
        db.query(Notification)
        .filter(
            Notification.org_id == ORG,
            Notification.recipient_id == person_id,
            Notification.type == NotificationType.CANCELLATION,
        )
        .all()
    )


@pytest.mark.no_mock_auth
class TestEventCancellationNotice:
    def test_cancelling_an_event_notifies_its_assignees(self, client, db):
        """A volunteer holding the shift gets a cancellation notice."""
        hdrs, volunteer, event = _org_with_assigned_volunteer(client)

        deleted = client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)
        assert deleted.status_code == 204, deleted.text

        notices = _cancellations_for(db, volunteer["person_id"])
        assert len(notices) == 1, "the assignee was not told the event was cancelled"
        assert notices[0].org_id == ORG
        assert notices[0].status == NotificationStatus.PENDING

    def test_cancellation_notice_survives_the_deleted_event(self, client, db):
        """The notice must not be cascade-deleted with the event row."""
        hdrs, volunteer, event = _org_with_assigned_volunteer(client)

        client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)

        notice = _cancellations_for(db, volunteer["person_id"])[0]
        # event_id must be NULL, otherwise Event.notifications' delete-orphan
        # cascade removes this row along with the event.
        assert notice.event_id is None
        assert db.query(Assignment).filter(Assignment.event_id == event["id"]).count() == 0

    def test_notice_carries_a_self_contained_event_snapshot(self, client, db):
        """The renderer cannot re-read a deleted event, so the notice holds the detail."""
        hdrs, volunteer, event = _org_with_assigned_volunteer(client)

        client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)

        data = _cancellations_for(db, volunteer["person_id"])[0].template_data or {}
        assert data.get("event_title") == "Sunday Worship"
        assert data.get("role") == "usher"
        assert data.get("event_datetime"), "cancellation email needs the original date and time"
        assert data.get("event_id") == event["id"]

    def test_cancellation_appears_in_the_volunteer_inbox(self, client, db):
        """The volunteer sees it in their own inbox, scoped to them."""
        hdrs, volunteer, event = _org_with_assigned_volunteer(client)
        client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)

        vol_hdrs = auth_headers(client, VOL_EMAIL, VOL_PW)
        listed = client.get(f"/api/v1/notifications/?org_id={ORG}", headers=vol_hdrs)
        assert listed.status_code == 200, listed.text
        types = [row["type"] for row in listed.json()["notifications"]]
        assert NotificationType.CANCELLATION in types

    def test_deleting_a_past_event_does_not_mail_its_volunteers(self, client, db):
        """Tidying up an event that already happened is not a cancellation.

        Without this, clearing out last month's events would email everyone who
        served at them that their shift had been cancelled.
        """
        hdrs, volunteer, event = _org_with_assigned_volunteer(client)
        row = db.query(Event).filter(Event.id == event["id"], Event.org_id == ORG).one()
        row.start_time = utcnow() - timedelta(days=7)
        row.end_time = row.start_time + timedelta(hours=2)
        db.commit()

        deleted = client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)
        assert deleted.status_code == 204, deleted.text

        assert _cancellations_for(db, volunteer["person_id"]) == []

    def test_cancelling_an_unstaffed_event_notifies_nobody(self, client, db):
        """No assignees means no notices, not an empty broadcast."""
        seed_org(client, ORG)
        seed_user(client, ORG, ADMIN_EMAIL, "Admin", ADMIN_PW)
        hdrs = auth_headers(client, ADMIN_EMAIL, ADMIN_PW)
        event = seed_event(client, hdrs, ORG, "evt-empty", role_counts={"usher": 1})

        client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)

        assert (
            db.query(Notification)
            .filter(
                Notification.org_id == ORG,
                Notification.type == NotificationType.CANCELLATION,
            )
            .count()
            == 0
        )

    def test_one_notice_per_person_rests_on_an_enforced_invariant(self, client, db):
        """A person cannot hold two roles at one event, so one notice is one person.

        This replaces a test that assigned a second role without checking the
        response. The API refuses that assignment, so the test's stated case
        never occurred and its assertion held for the wrong reason. What is
        actually true is asserted here instead: the refusal, and the single
        notice that follows from it.
        """
        seed_org(client, ORG)
        seed_user(client, ORG, ADMIN_EMAIL, "Admin", ADMIN_PW)
        hdrs = auth_headers(client, ADMIN_EMAIL, ADMIN_PW)
        invitation = seed_invitation(
            client, hdrs, ORG, VOL_EMAIL, "Sarah", roles=["usher", "greeter"]
        )
        volunteer = accept_invitation(client, invitation["token"], password=VOL_PW)
        event = seed_event(
            client, hdrs, ORG, "evt-two-roles", role_counts={"usher": 1, "greeter": 1}
        )

        first = client.post(
            f"/api/v1/events/{event['id']}/assignments",
            json={"person_id": volunteer["person_id"], "action": "assign", "role": "usher"},
            headers=hdrs,
        )
        assert first.status_code == 200, first.text
        second = client.post(
            f"/api/v1/events/{event['id']}/assignments",
            json={"person_id": volunteer["person_id"], "action": "assign", "role": "greeter"},
            headers=hdrs,
        )
        assert second.status_code >= 400, "a person held two roles at one event"
        assert db.query(Assignment).filter(Assignment.event_id == event["id"]).count() == 1

        client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)

        assert len(_cancellations_for(db, volunteer["person_id"])) == 1


@pytest.mark.no_mock_auth
class TestCancellationNoticeScope:
    """Who is told is not simply "whoever has an assignment row".

    A draft solver assignment is not a commitment anyone has been shown, so
    cancelling it must not be the first a volunteer hears of it. Someone who
    already declined is not scheduled. And a row belonging to another tenant
    must never be mailed from this organization at all.
    """

    def test_declined_assignees_are_not_told_a_shift_they_refused_was_cancelled(self, client, db):
        hdrs, volunteer, event = _org_with_assigned_volunteer(client)
        assignment = db.query(Assignment).filter(Assignment.event_id == event["id"]).one()
        assignment.response_status = "declined"
        db.commit()

        client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)

        assert _cancellations_for(db, volunteer["person_id"]) == []

    def test_unpublished_solver_assignments_do_not_trigger_notices(self, client, db):
        """Nothing in a draft solution is visible, so nothing in it was promised."""
        hdrs, volunteer, event = _org_with_assigned_volunteer(client)
        draft = _solution(ORG, is_published=False)
        db.add(draft)
        db.flush()
        assignment = db.query(Assignment).filter(Assignment.event_id == event["id"]).one()
        assignment.solution_id = draft.id
        db.commit()

        client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)

        assert _cancellations_for(db, volunteer["person_id"]) == []

    def test_published_solver_assignments_still_trigger_notices(self, client, db):
        """The converse: publication is what makes the shift real, so it notifies."""
        hdrs, volunteer, event = _org_with_assigned_volunteer(client)
        published = _solution(ORG, is_published=True)
        db.add(published)
        db.flush()
        assignment = db.query(Assignment).filter(Assignment.event_id == event["id"]).one()
        assignment.solution_id = published.id
        db.commit()

        client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)

        assert len(_cancellations_for(db, volunteer["person_id"])) == 1

    def test_reusing_a_cancelled_event_id_still_notifies(self, client, db):
        """The dedupe key must not permanently burn an event id.

        Cancellation notices outlive their event by design, so a key derived
        only from the event id survives too. Recreating an event under the same
        id then looks like a duplicate, and the second cancellation is silently
        dropped.
        """
        hdrs, volunteer, event = _org_with_assigned_volunteer(client, event_id="evt-reused")
        client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)
        assert len(_cancellations_for(db, volunteer["person_id"])) == 1

        again = seed_event(
            client, hdrs, ORG, "evt-reused", days_from_now=21, role_counts={"usher": 1}
        )
        assigned = client.post(
            f"/api/v1/events/{again['id']}/assignments",
            json={"person_id": volunteer["person_id"], "action": "assign", "role": "usher"},
            headers=hdrs,
        )
        assert assigned.status_code == 200, assigned.text

        client.delete(f"/api/v1/events/{again['id']}", headers=hdrs)

        assert len(_cancellations_for(db, volunteer["person_id"])) == 2
