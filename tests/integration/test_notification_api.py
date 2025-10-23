"""Integration tests for Notification API endpoints.

Tests the notification API with real database and authentication.

Coverage target: 100% for api/routers/notifications.py endpoints
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.main import app
from api.models import Person, Organization, Notification, EmailPreference, NotificationType, NotificationStatus
from api.security import create_access_token
import uuid


class TestNotificationEndpoints:
    """Integration tests for notification API endpoints."""

    def test_get_notifications_as_volunteer(self, client: TestClient, test_db: Session, auth_headers_volunteer: dict):
        """Test GET /api/notifications/ as volunteer (see only own notifications)."""
        # Arrange: Create test data
        volunteer_id = "volunteer_123"
        org_id = "org_123"

        # Create notification for volunteer
        notification = Notification(
            org_id=org_id,
            recipient_id=volunteer_id,
            type=NotificationType.ASSIGNMENT,
            status=NotificationStatus.SENT,
            template_data={"event_title": "Sunday Service"}
        )
        test_db.add(notification)
        test_db.commit()

        # Act
        response = client.get(f"/api/notifications/?org_id={org_id}", headers=auth_headers_volunteer)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) >= 1
        assert data["notifications"][0]["recipient_id"] == volunteer_id

    def test_get_notifications_as_admin_sees_all(self, client: TestClient, test_db: Session, auth_headers_admin: dict):
        """Test GET /api/notifications/ as admin (see all org notifications)."""
        # Arrange
        org_id = "org_123"

        # Create notifications for different volunteers
        notif1 = Notification(org_id=org_id, recipient_id="vol_1", type=NotificationType.ASSIGNMENT, status=NotificationStatus.SENT)
        notif2 = Notification(org_id=org_id, recipient_id="vol_2", type=NotificationType.ASSIGNMENT, status=NotificationStatus.SENT)
        test_db.add_all([notif1, notif2])
        test_db.commit()

        # Act
        response = client.get(f"/api/notifications/?org_id={org_id}", headers=auth_headers_admin)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) >= 2  # Admin sees all

    def test_get_single_notification(self, client: TestClient, test_db: Session, auth_headers_volunteer: dict):
        """Test GET /api/notifications/{notification_id}."""
        # Arrange
        volunteer_id = "volunteer_123"
        org_id = "org_123"

        notification = Notification(
            org_id=org_id,
            recipient_id=volunteer_id,
            type=NotificationType.REMINDER,
            status=NotificationStatus.DELIVERED,
            template_data={"event_title": "Bible Study"}
        )
        test_db.add(notification)
        test_db.commit()
        test_db.refresh(notification)  # Get auto-generated ID
        notification_id = notification.id

        # Act
        response = client.get(f"/api/notifications/{notification_id}", headers=auth_headers_volunteer)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == notification_id
        assert data["type"] == "reminder"
        assert data["status"] == "delivered"

    def test_get_email_preferences(self, client: TestClient, test_db: Session, auth_headers_volunteer: dict):
        """Test GET /api/notifications/preferences/me."""
        # Arrange
        volunteer_id = "volunteer_123"
        org_id = "org_123"

        # Create preferences
        pref = EmailPreference(
            person_id=volunteer_id,
            org_id=org_id,
            frequency="immediate",
            enabled_types=["assignment", "reminder"],
            unsubscribe_token=str(uuid.uuid4())
        )
        test_db.add(pref)
        test_db.commit()

        # Act
        response = client.get("/api/notifications/preferences/me", headers=auth_headers_volunteer)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["person_id"] == volunteer_id
        assert data["frequency"] == "immediate"
        assert "assignment" in data["enabled_types"]

    def test_update_email_preferences(self, client: TestClient, test_db: Session, auth_headers_volunteer: dict):
        """Test PUT /api/notifications/preferences/me."""
        # Arrange
        volunteer_id = "volunteer_123"
        org_id = "org_123"

        # Create existing preferences
        pref = EmailPreference(
            person_id=volunteer_id,
            org_id=org_id,
            frequency="immediate",
            enabled_types=["assignment"],
            unsubscribe_token=str(uuid.uuid4())
        )
        test_db.add(pref)
        test_db.commit()

        # Act: Update to daily digest
        update_data = {
            "frequency": "daily",
            "enabled_types": ["assignment", "reminder", "update"],
            "digest_hour": 8
        }
        response = client.put("/api/notifications/preferences/me", json=update_data, headers=auth_headers_volunteer)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] == "daily"
        assert data["digest_hour"] == 8
        assert len(data["enabled_types"]) == 3

    def test_get_org_stats_as_admin(self, client: TestClient, test_db: Session, auth_headers_admin: dict):
        """Test GET /api/notifications/stats/organization (admin-only)."""
        # Arrange
        org_id = "org_123"

        # Create various notifications with different statuses
        notifications = [
            Notification(org_id=org_id, recipient_id=f"vol_{i}", type=NotificationType.ASSIGNMENT, status=NotificationStatus.SENT)
            for i in range(5)
        ]
        notifications[0].status = NotificationStatus.DELIVERED
        notifications[1].status = NotificationStatus.OPENED
        test_db.add_all(notifications)
        test_db.commit()

        # Act
        response = client.get(f"/api/notifications/stats/organization?org_id={org_id}", headers=auth_headers_admin)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_sent" in data
        assert "total_delivered" in data
        assert "total_opened" in data
        assert data["total_sent"] >= 5

    def test_get_org_stats_as_volunteer_forbidden(self, client: TestClient, auth_headers_volunteer: dict):
        """Test that volunteers cannot access org stats (admin-only)."""
        # Arrange
        org_id = "org_123"

        # Act
        response = client.get(f"/api/notifications/stats/organization?org_id={org_id}", headers=auth_headers_volunteer)

        # Assert
        assert response.status_code == 403  # Forbidden

    def test_post_test_notification_as_admin(self, client: TestClient, test_db: Session, auth_headers_admin: dict):
        """Test POST /api/notifications/test/send (admin-only, for testing)."""
        # Arrange
        test_data = {
            "recipient_email": "test@example.com",
            "notification_type": "assignment",
            "template_data": {
                "event_title": "Test Event",
                "role": "Test Role"
            }
        }

        # Act
        with patch('api.tasks.notifications.send_email_task') as mock_task:
            response = client.post("/api/notifications/test/send", json=test_data, headers=auth_headers_admin)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_notifications_multi_tenant_isolation(self, client: TestClient, test_db: Session):
        """Test that volunteers can only see notifications from their own org."""
        # Arrange: Create 2 orgs with notifications
        org1_id = "org_1"
        org2_id = "org_2"
        volunteer_id = "volunteer_in_org1"

        # Notification in org1 (volunteer's org)
        notif1 = Notification(org_id=org1_id, recipient_id=volunteer_id, type=NotificationType.ASSIGNMENT, status=NotificationStatus.SENT)
        # Notification in org2 (different org)
        notif2 = Notification(org_id=org2_id, recipient_id="other_vol", type=NotificationType.ASSIGNMENT, status=NotificationStatus.SENT)
        test_db.add_all([notif1, notif2])
        test_db.commit()
        test_db.refresh(notif1)
        test_db.refresh(notif2)
        notif1_id = notif1.id
        notif2_id = notif2.id

        # Create token for volunteer in org1
        token = create_access_token({"sub": volunteer_id, "org_id": org1_id})
        headers = {"Authorization": f"Bearer {token}"}

        # Act: Request notifications for org1
        response = client.get(f"/api/notifications/?org_id={org1_id}", headers=headers)

        # Assert: Should only see org1 notifications
        assert response.status_code == 200
        data = response.json()
        notification_ids = [n["id"] for n in data["notifications"]]
        assert notif1_id in notification_ids
        assert notif2_id not in notification_ids  # Org2 notification NOT visible


# Pytest fixtures
@pytest.fixture
def test_org(test_db: Session):
    """Create test organization."""
    org = Organization(id="org_123", name="Test Organization", region="US", config={})
    test_db.add(org)
    test_db.commit()
    test_db.refresh(org)
    return org


@pytest.fixture
def volunteer_user(test_db: Session, test_org):
    """Create volunteer user in database."""
    from api.security import hash_password

    user = Person(
        id="volunteer_123",
        org_id="org_123",
        name="Volunteer User",
        email="volunteer@example.com",
        password_hash=hash_password("password"),
        roles=["volunteer"]
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_user(test_db: Session, test_org):
    """Create admin user in database."""
    from api.security import hash_password

    user = Person(
        id="admin_123",
        org_id="org_123",
        name="Admin User",
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        roles=["admin"]
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers_volunteer(volunteer_user):
    """Headers with JWT token for volunteer user."""
    token = create_access_token({"sub": "volunteer_123", "org_id": "org_123", "roles": ["volunteer"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(admin_user):
    """Headers with JWT token for admin user."""
    token = create_access_token({"sub": "admin_123", "org_id": "org_123", "roles": ["admin"]})
    return {"Authorization": f"Bearer {token}"}


# Run tests with: poetry run pytest tests/integration/test_notification_api.py -v
