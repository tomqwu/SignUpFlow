"""
Unit tests for audit logging service.

Tests the audit_logger module which provides functions to log
security-sensitive operations to the audit log database.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Request

from api.utils.audit_logger import (
    log_audit_event,
    log_audit_from_request,
    log_login_attempt,
    log_permission_change,
    log_data_export,
)
from api.models import AuditLog, AuditAction


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = Mock(spec=Session)
    db.add = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    return db


@pytest.fixture
def mock_request():
    """Create a mock FastAPI Request object."""
    request = Mock(spec=Request)
    request.client = Mock()
    request.client.host = "192.168.1.100"
    request.headers = {
        "user-agent": "Mozilla/5.0 (Test Browser)",
    }
    return request


@pytest.fixture
def mock_request_with_proxy():
    """Create a mock FastAPI Request with proxy headers."""
    request = Mock(spec=Request)
    request.client = Mock()
    request.client.host = "10.0.0.1"  # Internal proxy IP
    request.headers = {
        "user-agent": "Mozilla/5.0 (Test Browser)",
        "x-forwarded-for": "203.0.113.42, 10.0.0.1",  # Client IP, Proxy IP
        "x-real-ip": "203.0.113.42",
    }
    return request


class TestLogAuditEvent:
    """Test log_audit_event function."""

    def test_log_basic_event(self, mock_db):
        """Test logging a basic audit event."""
        result = log_audit_event(
            db=mock_db,
            action=AuditAction.USER_CREATED,
            user_id="user_123",
            user_email="test@example.com",
            organization_id="org_456",
        )

        # Verify database calls
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        # Verify audit log was created
        created_log = mock_db.add.call_args[0][0]
        assert isinstance(created_log, AuditLog)
        assert created_log.action == AuditAction.USER_CREATED
        assert created_log.user_id == "user_123"
        assert created_log.user_email == "test@example.com"
        assert created_log.organization_id == "org_456"
        assert created_log.status == "success"

    def test_log_event_with_resource(self, mock_db):
        """Test logging an event with resource information."""
        result = log_audit_event(
            db=mock_db,
            action=AuditAction.USER_DELETED,
            user_id="admin_123",
            user_email="admin@example.com",
            resource_type="person",
            resource_id="person_789",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.resource_type == "person"
        assert created_log.resource_id == "person_789"

    def test_log_event_with_details(self, mock_db):
        """Test logging an event with additional details."""
        details = {
            "old_value": "volunteer",
            "new_value": "admin",
            "changed_by": "super_admin",
        }

        result = log_audit_event(
            db=mock_db,
            action=AuditAction.ROLE_ASSIGNED,
            user_id="admin_123",
            details=details,
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.details == details

    def test_log_event_with_ip_and_user_agent(self, mock_db):
        """Test logging an event with IP address and user agent."""
        result = log_audit_event(
            db=mock_db,
            action=AuditAction.DATA_EXPORTED,
            user_id="user_123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.ip_address == "192.168.1.100"
        assert created_log.user_agent == "Mozilla/5.0"

    def test_log_failure_event(self, mock_db):
        """Test logging a failure event with error message."""
        result = log_audit_event(
            db=mock_db,
            action=AuditAction.LOGIN_FAILURE,
            user_email="test@example.com",
            status="failure",
            error_message="Invalid credentials",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.status == "failure"
        assert created_log.error_message == "Invalid credentials"

    def test_log_denied_event(self, mock_db):
        """Test logging a denied permission event."""
        result = log_audit_event(
            db=mock_db,
            action=AuditAction.PERMISSION_DENIED,
            user_id="user_123",
            user_email="test@example.com",
            status="denied",
            error_message="Insufficient permissions",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.status == "denied"

    def test_log_event_without_user(self, mock_db):
        """Test logging a system event without user information."""
        result = log_audit_event(
            db=mock_db,
            action=AuditAction.DATABASE_BACKUP,
            user_id=None,
            user_email=None,
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.user_id is None
        assert created_log.user_email is None

    def test_log_event_generates_unique_id(self, mock_db):
        """Test that each audit log has a unique ID."""
        result1 = log_audit_event(
            db=mock_db,
            action=AuditAction.USER_CREATED,
        )

        result2 = log_audit_event(
            db=mock_db,
            action=AuditAction.USER_CREATED,
        )

        log1 = mock_db.add.call_args_list[0][0][0]
        log2 = mock_db.add.call_args_list[1][0][0]

        assert log1.id != log2.id
        assert log1.id.startswith("audit_")
        assert log2.id.startswith("audit_")


class TestLogAuditFromRequest:
    """Test log_audit_from_request function."""

    def test_extract_ip_from_request(self, mock_db, mock_request):
        """Test that IP address is extracted from request."""
        result = log_audit_from_request(
            db=mock_db,
            request=mock_request,
            action=AuditAction.DATA_EXPORTED,
            user_id="user_123",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.ip_address == "192.168.1.100"

    def test_extract_user_agent_from_request(self, mock_db, mock_request):
        """Test that user agent is extracted from request."""
        result = log_audit_from_request(
            db=mock_db,
            request=mock_request,
            action=AuditAction.DATA_EXPORTED,
            user_id="user_123",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.user_agent == "Mozilla/5.0 (Test Browser)"

    def test_extract_ip_from_x_forwarded_for(self, mock_db, mock_request_with_proxy):
        """Test that client IP is extracted from X-Forwarded-For header."""
        result = log_audit_from_request(
            db=mock_db,
            request=mock_request_with_proxy,
            action=AuditAction.DATA_EXPORTED,
            user_id="user_123",
        )

        created_log = mock_db.add.call_args[0][0]
        # Should use first IP in X-Forwarded-For (client IP)
        assert created_log.ip_address == "203.0.113.42"

    def test_extract_ip_from_x_real_ip(self, mock_db):
        """Test that client IP is extracted from X-Real-IP header."""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "10.0.0.1"
        request.headers = {
            "user-agent": "Mozilla/5.0",
            "x-real-ip": "203.0.113.99",
        }

        result = log_audit_from_request(
            db=mock_db,
            request=request,
            action=AuditAction.DATA_EXPORTED,
            user_id="user_123",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.ip_address == "203.0.113.99"

    def test_handle_missing_client_ip(self, mock_db):
        """Test handling when request has no client IP."""
        request = Mock(spec=Request)
        request.client = None
        request.headers = {"user-agent": "Mozilla/5.0"}

        result = log_audit_from_request(
            db=mock_db,
            request=request,
            action=AuditAction.DATA_EXPORTED,
            user_id="user_123",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.ip_address is None


class TestLogLoginAttempt:
    """Test log_login_attempt function."""

    def test_log_successful_login(self, mock_db, mock_request):
        """Test logging a successful login attempt."""
        result = log_login_attempt(
            db=mock_db,
            request=mock_request,
            email="test@example.com",
            success=True,
            user_id="user_123",
            organization_id="org_456",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.action == AuditAction.LOGIN_SUCCESS
        assert created_log.status == "success"
        assert created_log.user_id == "user_123"
        assert created_log.user_email == "test@example.com"
        assert created_log.organization_id == "org_456"

    def test_log_failed_login(self, mock_db, mock_request):
        """Test logging a failed login attempt."""
        result = log_login_attempt(
            db=mock_db,
            request=mock_request,
            email="test@example.com",
            success=False,
            error_message="Invalid credentials",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.action == AuditAction.LOGIN_FAILURE
        assert created_log.status == "failure"
        assert created_log.user_email == "test@example.com"
        assert created_log.error_message == "Invalid credentials"


class TestLogPermissionChange:
    """Test log_permission_change function."""

    def test_log_role_assignment(self, mock_db, mock_request):
        """Test logging a role assignment (adding roles)."""
        result = log_permission_change(
            db=mock_db,
            request=mock_request,
            admin_user_id="admin_123",
            admin_email="admin@example.com",
            target_user_id="user_456",
            target_email="user@example.com",
            organization_id="org_789",
            old_roles=["volunteer"],
            new_roles=["volunteer", "admin"],
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.action == AuditAction.ROLE_ASSIGNED
        assert created_log.user_id == "admin_123"
        assert created_log.user_email == "admin@example.com"
        assert created_log.resource_id == "user_456"
        assert created_log.details["target_user_id"] == "user_456"
        assert created_log.details["added_roles"] == ["admin"]
        assert created_log.details["removed_roles"] == []

    def test_log_role_removal(self, mock_db, mock_request):
        """Test logging a role removal (removing roles)."""
        result = log_permission_change(
            db=mock_db,
            request=mock_request,
            admin_user_id="admin_123",
            admin_email="admin@example.com",
            target_user_id="user_456",
            target_email="user@example.com",
            organization_id="org_789",
            old_roles=["volunteer", "admin"],
            new_roles=["volunteer"],
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.action == AuditAction.ROLE_REMOVED
        assert created_log.details["added_roles"] == []
        assert created_log.details["removed_roles"] == ["admin"]

    def test_log_role_change_multiple(self, mock_db, mock_request):
        """Test logging complex role changes (both add and remove)."""
        result = log_permission_change(
            db=mock_db,
            request=mock_request,
            admin_user_id="admin_123",
            admin_email="admin@example.com",
            target_user_id="user_456",
            target_email="user@example.com",
            organization_id="org_789",
            old_roles=["volunteer", "coordinator"],
            new_roles=["volunteer", "admin"],
        )

        created_log = mock_db.add.call_args[0][0]
        # When both added and removed, should use ROLE_ASSIGNED
        assert created_log.action == AuditAction.ROLE_ASSIGNED
        assert set(created_log.details["added_roles"]) == {"admin"}
        assert set(created_log.details["removed_roles"]) == {"coordinator"}


class TestLogDataExport:
    """Test log_data_export function."""

    def test_log_calendar_export(self, mock_db, mock_request):
        """Test logging a calendar export operation."""
        result = log_data_export(
            db=mock_db,
            request=mock_request,
            user_id="user_123",
            user_email="test@example.com",
            organization_id="org_456",
            export_type="calendar",
            resource_type="events",
            resource_count=25,
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.action == AuditAction.CALENDAR_EXPORTED
        assert created_log.user_id == "user_123"
        assert created_log.details["export_type"] == "calendar"
        assert created_log.details["resource_type"] == "events"
        assert created_log.details["resource_count"] == 25

    def test_log_csv_export(self, mock_db, mock_request):
        """Test logging a CSV data export."""
        result = log_data_export(
            db=mock_db,
            request=mock_request,
            user_id="user_123",
            user_email="test@example.com",
            organization_id="org_456",
            export_type="csv",
            resource_type="people",
            resource_count=150,
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.action == AuditAction.DATA_EXPORTED
        assert created_log.details["export_type"] == "csv"
        assert created_log.details["resource_type"] == "people"

    def test_log_report_export(self, mock_db, mock_request):
        """Test logging a report generation."""
        result = log_data_export(
            db=mock_db,
            request=mock_request,
            user_id="admin_123",
            user_email="admin@example.com",
            organization_id="org_456",
            export_type="report",
            resource_type="analytics",
        )

        created_log = mock_db.add.call_args[0][0]
        assert created_log.action == AuditAction.DATA_EXPORTED
        assert created_log.details["export_type"] == "report"


class TestAuditActionConstants:
    """Test that AuditAction constants are defined correctly."""

    def test_authentication_actions(self):
        """Test authentication-related action constants."""
        assert AuditAction.LOGIN_SUCCESS == "auth.login.success"
        assert AuditAction.LOGIN_FAILURE == "auth.login.failure"
        assert AuditAction.LOGOUT == "auth.logout"

    def test_user_management_actions(self):
        """Test user management action constants."""
        assert AuditAction.USER_CREATED == "user.created"
        assert AuditAction.USER_UPDATED == "user.updated"
        assert AuditAction.USER_DELETED == "user.deleted"

    def test_permission_actions(self):
        """Test permission-related action constants."""
        assert AuditAction.ROLE_ASSIGNED == "permission.role.assigned"
        assert AuditAction.ROLE_REMOVED == "permission.role.removed"
        assert AuditAction.PERMISSION_DENIED == "permission.denied"

    def test_data_access_actions(self):
        """Test data access action constants."""
        assert AuditAction.DATA_EXPORTED == "data.exported"
        assert AuditAction.CALENDAR_EXPORTED == "data.calendar.exported"
