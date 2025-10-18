"""
Audit log model for tracking sensitive operations.

Tracks:
- User creation/deletion
- Permission changes (role assignments)
- Data exports (calendar, reports)
- Login attempts (success/failure)
- Sensitive data access
"""

from sqlalchemy import Column, String, DateTime, JSON, Index
from sqlalchemy.sql import func
from api.database import Base


class AuditLog(Base):
    """
    Audit log for security-sensitive operations.

    Stores immutable records of who did what, when, and from where.
    """

    __tablename__ = "audit_logs"

    # Primary key
    id = Column(String, primary_key=True)

    # Who
    user_id = Column(String, nullable=True, index=True)  # Nullable for system events
    user_email = Column(String, nullable=True)  # Denormalized for easy lookup
    organization_id = Column(String, nullable=True, index=True)

    # What
    action = Column(String, nullable=False, index=True)  # e.g., "user.created", "role.changed", "data.exported"
    resource_type = Column(String, nullable=True)  # e.g., "person", "event", "organization"
    resource_id = Column(String, nullable=True)  # ID of affected resource

    # Details
    details = Column(JSON, nullable=True)  # Additional context (before/after values, etc.)

    # When
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    # Where
    ip_address = Column(String, nullable=True)  # Client IP address
    user_agent = Column(String, nullable=True)  # Browser/client info

    # Outcome
    status = Column(String, nullable=False, default="success")  # "success", "failure", "denied"
    error_message = Column(String, nullable=True)  # If status = "failure"

    # Indexes for common queries
    __table_args__ = (
        Index("idx_audit_user_timestamp", "user_id", "timestamp"),
        Index("idx_audit_org_timestamp", "organization_id", "timestamp"),
        Index("idx_audit_action_timestamp", "action", "timestamp"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_email} at {self.timestamp}>"


# Audit action constants
class AuditAction:
    """Standard audit action names."""

    # Authentication
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    PASSWORD_RESET_REQUESTED = "auth.password_reset.requested"
    PASSWORD_RESET_COMPLETED = "auth.password_reset.completed"

    # User management
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_INVITED = "user.invited"
    USER_INVITATION_ACCEPTED = "user.invitation.accepted"

    # Permissions
    ROLE_ASSIGNED = "permission.role.assigned"
    ROLE_REMOVED = "permission.role.removed"
    PERMISSION_DENIED = "permission.denied"

    # Data access
    DATA_EXPORTED = "data.exported"
    CALENDAR_EXPORTED = "data.calendar.exported"
    REPORT_GENERATED = "data.report.generated"

    # Organization
    ORG_CREATED = "org.created"
    ORG_UPDATED = "org.updated"
    ORG_SETTINGS_CHANGED = "org.settings.changed"

    # Sensitive operations
    BULK_DELETE = "data.bulk_delete"
    DATABASE_BACKUP = "system.database.backup"
    CONFIG_CHANGED = "system.config.changed"
