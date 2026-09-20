"""Cancelling an event must tell the people who were scheduled for it.

Rescheduling an event already notifies its assignees. Cancelling one used to
delete the event and its assignments silently, so a volunteer who had accepted
a shift learned about the cancellation only by noticing it had vanished.

The notice has to outlive the event row: `Event.notifications` cascades with
`delete-orphan`, so a cancellation notice that still pointed at the event would
be deleted in the same transaction. These tests pin the surviving notice and
the self-contained snapshot the renderer needs once the event is gone.
"""

import pytest

from api.models import Assignment, Notification, NotificationStatus, NotificationType
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

    def test_cancellation_notice_is_not_duplicated_per_assignment(self, client, db):
        """One notice per person, even when they hold two roles at the event."""
        hdrs, volunteer, event = _org_with_assigned_volunteer(client)
        # Same person, second role at the same event.
        client.post(
            f"/api/v1/events/{event['id']}/assignments",
            json={"person_id": volunteer["person_id"], "action": "assign", "role": "greeter"},
            headers=hdrs,
        )

        client.delete(f"/api/v1/events/{event['id']}", headers=hdrs)

        assert len(_cancellations_for(db, volunteer["person_id"])) == 1
