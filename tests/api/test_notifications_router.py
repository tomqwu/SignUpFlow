"""Smoke tests for the /notifications router (Sprint 8 PR 8.4).

The router was already implemented (api/routers/notifications.py) but never
registered in api/main.py. This PR registers it and adds two endpoints
mobile Inbox needs (mark-read, unread-count).
"""

import pytest

from api.models import Notification, NotificationStatus, NotificationType
from api.timeutils import utcnow
from tests.api.conftest import auth_headers, seed_org, seed_user


@pytest.mark.no_mock_auth
class TestNotificationsRouterRegistered:
    def test_list_notifications_route_is_registered(self, client):
        org_id = "n-reg"
        seed_org(client, org_id)
        seed_user(client, org_id, email="u@n-reg.org", name="U", password="UPass123!")
        hdrs = auth_headers(client, email="u@n-reg.org", password="UPass123!")

        # Pre-PR-8.4 this returned 404 (router not in app). Now 200.
        resp = client.get(f"/api/v1/notifications/?org_id={org_id}", headers=hdrs)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["notifications"] == []
        assert body["total"] == 0

    def test_list_returns_only_recipients_notifications_for_volunteer(self, client, db):
        org_id = "n-rbac"
        seed_org(client, org_id)
        # First user becomes admin.
        admin_resp = seed_user(
            client, org_id, email="admin@n-rbac.org", name="A", password="APass123!"
        )
        vol_resp = seed_user(client, org_id, email="vol@n-rbac.org", name="V", password="VPass123!")
        admin_hdrs = auth_headers(client, email="admin@n-rbac.org", password="APass123!")
        vol_hdrs = auth_headers(client, email="vol@n-rbac.org", password="VPass123!")

        # Seed one notification for each user directly in the DB.
        db.add(
            Notification(
                org_id=org_id,
                recipient_id=admin_resp["person_id"],
                type=NotificationType.ASSIGNMENT,
                status=NotificationStatus.SENT,
            )
        )
        db.add(
            Notification(
                org_id=org_id,
                recipient_id=vol_resp["person_id"],
                type=NotificationType.REMINDER,
                status=NotificationStatus.SENT,
            )
        )
        db.commit()

        # Volunteer sees only their own.
        v_list = client.get(f"/api/v1/notifications/?org_id={org_id}", headers=vol_hdrs)
        assert v_list.status_code == 200
        assert v_list.json()["total"] == 1
        assert v_list.json()["notifications"][0]["type"] == NotificationType.REMINDER

        # Admin sees both org-wide.
        a_list = client.get(f"/api/v1/notifications/?org_id={org_id}", headers=admin_hdrs)
        assert a_list.status_code == 200
        assert a_list.json()["total"] == 2


@pytest.mark.no_mock_auth
class TestNotificationsUnreadAndRead:
    def test_unread_count_excludes_opened_and_clicked(self, client, db):
        org_id = "n-unread"
        seed_org(client, org_id)
        user_resp = seed_user(
            client, org_id, email="u@n-unread.org", name="U", password="UPass123!"
        )
        hdrs = auth_headers(client, email="u@n-unread.org", password="UPass123!")
        person_id = user_resp["person_id"]

        # 2 unread + 1 opened + 1 clicked.
        db.add(
            Notification(
                org_id=org_id,
                recipient_id=person_id,
                type=NotificationType.ASSIGNMENT,
                status=NotificationStatus.SENT,
            )
        )
        db.add(
            Notification(
                org_id=org_id,
                recipient_id=person_id,
                type=NotificationType.ASSIGNMENT,
                status=NotificationStatus.SENT,
            )
        )
        db.add(
            Notification(
                org_id=org_id,
                recipient_id=person_id,
                type=NotificationType.ASSIGNMENT,
                status=NotificationStatus.OPENED,
                opened_at=utcnow(),
            )
        )
        db.add(
            Notification(
                org_id=org_id,
                recipient_id=person_id,
                type=NotificationType.ASSIGNMENT,
                status=NotificationStatus.CLICKED,
                clicked_at=utcnow(),
            )
        )
        db.commit()

        resp = client.get("/api/v1/notifications/unread/count", headers=hdrs)
        assert resp.status_code == 200, resp.text
        assert resp.json() == {"unread": 2}

    def test_mark_read_sets_opened_at_idempotently(self, client, db):
        org_id = "n-read"
        seed_org(client, org_id)
        user_resp = seed_user(client, org_id, email="u@n-read.org", name="U", password="UPass123!")
        hdrs = auth_headers(client, email="u@n-read.org", password="UPass123!")
        person_id = user_resp["person_id"]

        notif = Notification(
            org_id=org_id,
            recipient_id=person_id,
            type=NotificationType.ASSIGNMENT,
            status=NotificationStatus.SENT,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        first = client.post(f"/api/v1/notifications/{notif.id}/read", headers=hdrs)
        assert first.status_code == 200, first.text
        body1 = first.json()
        assert body1["status"] == NotificationStatus.OPENED
        assert body1["opened_at"] is not None
        first_opened = body1["opened_at"]

        # Idempotent: opened_at does not get overwritten on second call.
        second = client.post(f"/api/v1/notifications/{notif.id}/read", headers=hdrs)
        assert second.status_code == 200
        assert second.json()["opened_at"] == first_opened

    def test_mark_read_for_other_users_notification_returns_403(self, client, db):
        org_id = "n-rbac-read"
        seed_org(client, org_id)
        owner_resp = seed_user(client, org_id, email="owner@n.org", name="O", password="OPass123!")
        seed_user(client, org_id, email="intruder@n.org", name="I", password="IPass123!")
        intruder_hdrs = auth_headers(client, email="intruder@n.org", password="IPass123!")

        notif = Notification(
            org_id=org_id,
            recipient_id=owner_resp["person_id"],
            type=NotificationType.ASSIGNMENT,
            status=NotificationStatus.SENT,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        resp = client.post(f"/api/v1/notifications/{notif.id}/read", headers=intruder_hdrs)
        assert resp.status_code == 403

    def test_mark_read_nonexistent_returns_404(self, client):
        org_id = "n-read-404"
        seed_org(client, org_id)
        seed_user(client, org_id, email="u@n.org", name="U", password="UPass123!")
        hdrs = auth_headers(client, email="u@n.org", password="UPass123!")
        resp = client.post("/api/v1/notifications/999999/read", headers=hdrs)
        assert resp.status_code == 404
