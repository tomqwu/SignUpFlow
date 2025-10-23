"""
Unit tests for NotificationService.

Tests the core business logic of the notification service including:
- Creating assignment notifications
- Checking email preferences inline
- Default preference creation inline
- Multi-tenant isolation

Coverage target: >90% for api/services/notification_service.py
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from api.services.notification_service import (
    create_assignment_notifications,
    create_notification,
    get_pending_notifications_for_digest
)
from api.models import (
    Notification,
    NotificationType,
    NotificationStatus,
    EmailPreference,
    EmailFrequency,
    Assignment,
    Event,
    Person
)


class TestCreateAssignmentNotifications:
    """Test suite for create_assignment_notifications function."""

    @patch('api.services.notification_service.send_email_task')
    def test_creates_notification_for_single_assignment(self, mock_task):
        """Test that a notification is created for a single assignment."""
        # Arrange
        mock_db = Mock(spec=Session)
        assignment_id = 1

        mock_assignment = Mock(spec=Assignment)
        mock_assignment.id = assignment_id
        mock_assignment.person_id = 1
        mock_assignment.event_id = 1
        mock_assignment.role = "Usher"

        mock_person = Mock(spec=Person)
        mock_person.id = 1
        mock_person.org_id = "org_123"
        mock_person.email = "volunteer@example.com"
        mock_person.name = "John Doe"
        mock_person.language = "en"
        mock_person.timezone = "America/Toronto"

        mock_event = Mock(spec=Event)
        mock_event.id = 1
        mock_event.org_id = "org_123"
        mock_event.title = "Sunday Service"
        mock_event.datetime = "2025-11-01T10:00:00"

        mock_assignment.person = mock_person
        mock_assignment.event = mock_event

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assignment:
                mock_query.filter.return_value.first.return_value = mock_assignment
            elif model == Person:
                mock_query.filter.return_value.first.return_value = mock_person
            elif model == EmailPreference:
                mock_pref = Mock(spec=EmailPreference)
                mock_pref.frequency = EmailFrequency.IMMEDIATE
                mock_pref.enabled_types = [NotificationType.ASSIGNMENT]
                mock_query.filter.return_value.first.return_value = mock_pref
            return mock_query

        mock_db.query.side_effect = query_side_effect

        # Act
        result = create_assignment_notifications([assignment_id], mock_db, send_immediately=True)

        # Assert
        assert result['created'] >= 1
        mock_db.add.assert_called()
        mock_db.commit.assert_called()

    @patch('api.services.notification_service.send_email_task')
    def test_respects_email_preferences_disabled(self, mock_task):
        """Test that notifications are skipped if assignment type disabled."""
        # Arrange
        mock_db = Mock(spec=Session)
        assignment_id = 1

        mock_assignment = Mock(spec=Assignment)
        mock_assignment.id = assignment_id
        mock_assignment.person_id = 1
        mock_assignment.event_id = 1

        mock_person = Mock(spec=Person)
        mock_person.id = 1
        mock_person.org_id = "org_123"

        mock_event = Mock(spec=Event)
        mock_event.id = 1
        mock_event.org_id = "org_123"

        mock_assignment.person = mock_person
        mock_assignment.event = mock_event

        def query_side_effect(model):
            mock_query = Mock()
            if model == Assignment:
                mock_query.filter.return_value.first.return_value = mock_assignment
            elif model == Person:
                mock_query.filter.return_value.first.return_value = mock_person
            elif model == EmailPreference:
                mock_pref = Mock(spec=EmailPreference)
                mock_pref.frequency = EmailFrequency.IMMEDIATE
                mock_pref.enabled_types = []  # Assignment disabled
                mock_query.filter.return_value.first.return_value = mock_pref
            return mock_query

        mock_db.query.side_effect = query_side_effect

        # Act
        result = create_assignment_notifications([assignment_id], mock_db, send_immediately=True)

        # Assert - should be skipped
        assert result['skipped'] >= 1

    def test_handles_missing_assignment_gracefully(self):
        """Test that missing assignment is handled gracefully."""
        # Arrange
        mock_db = Mock(spec=Session)
        assignment_id = 999

        def query_side_effect(model):
            mock_query = Mock()
            mock_query.filter.return_value.first.return_value = None
            return mock_query

        mock_db.query.side_effect = query_side_effect

        # Act
        result = create_assignment_notifications([assignment_id], mock_db, send_immediately=True)

        # Assert
        assert result['skipped'] >= 1
        assert result['created'] == 0


class TestCreateNotification:
    """Test suite for create_notification function."""

    @patch('api.services.notification_service.send_email_task')
    def test_creates_notification_with_valid_data(self, mock_task):
        """Test creating a notification with valid data."""
        # Arrange
        mock_db = Mock(spec=Session)

        # Mock email preference query
        mock_pref = Mock(spec=EmailPreference)
        mock_pref.frequency = EmailFrequency.IMMEDIATE
        mock_pref.enabled_types = [NotificationType.ASSIGNMENT]

        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_pref
        mock_db.query.return_value = mock_query

        template_data = {
            "event_title": "Sunday Service",
            "role": "Usher"
        }

        # Act
        notification = create_notification(
            recipient_id="person_123",
            org_id="org_123",
            notification_type=NotificationType.ASSIGNMENT,
            template_data=template_data,
            db=mock_db,
            send_immediately=True
        )

        # Assert
        assert notification is not None
        assert notification.org_id == "org_123"
        assert notification.recipient_id == "person_123"
        assert notification.type == NotificationType.ASSIGNMENT
        assert notification.status == NotificationStatus.PENDING
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called()


class TestGetPendingNotificationsForDigest:
    """Test suite for get_pending_notifications_for_digest function."""

    def test_returns_pending_digest_notifications(self):
        """Test retrieving pending notifications for digest."""
        # Arrange
        mock_db = Mock(spec=Session)
        person_id = "person_123"
        frequency = EmailFrequency.DAILY

        mock_notification = Mock(spec=Notification)
        mock_notification.id = 1
        mock_notification.type = NotificationType.ASSIGNMENT
        mock_notification.status = NotificationStatus.PENDING

        # Mock query chain: query().filter().all()
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [mock_notification]

        mock_db.query.return_value = mock_query

        # Act
        result = get_pending_notifications_for_digest(
            person_id=person_id,
            frequency=frequency,
            db=mock_db
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        mock_db.query.assert_called_once()


# Run tests with: poetry run pytest tests/unit/test_notification_service.py -v
