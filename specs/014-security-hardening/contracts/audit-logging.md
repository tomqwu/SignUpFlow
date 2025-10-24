# Audit Logging API Contract

**Feature**: Security Hardening - Audit Logging
**Purpose**: Comprehensive audit trail for compliance (SOC 2, HIPAA, GDPR) and security incident investigation
**Status**: Contract Definition

---

## Overview

Audit logging service captures all security-relevant actions (admin operations, permission changes, data access, authentication events) in an immutable, append-only log for compliance and forensic analysis.

**Key Features**:
- Append-only storage (tamper-evident, no updates/deletes)
- Structured JSON format with consistent schema
- Organization-scoped queries (multi-tenant isolation)
- 90-day retention (compliance requirement)
- Performance: <10ms write overhead per action

---

## Audit Log Schema

### Database Model

```python
# api/models.py
class AuditLog(Base):
    """Immutable audit log entry (append-only)."""
    __tablename__ = "audit_logs"

    # Primary key
    id = Column(String, primary_key=True)  # Format: "audit_{timestamp}_{uuid}"

    # Temporal
    timestamp = Column(DateTime, nullable=False, index=True)  # UTC

    # Multi-tenant isolation
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)

    # Actor (who performed the action)
    user_id = Column(String, ForeignKey("people.id"), nullable=False, index=True)
    user_email = Column(String, nullable=False)  # Denormalized for audit reports
    user_roles = Column(JSON, nullable=False)  # Roles at time of action (snapshot)

    # Action details
    action = Column(String, nullable=False, index=True)  # Format: "{resource}.{operation}"
    resource_type = Column(String, nullable=False, index=True)  # "event", "person", "team", "organization"
    resource_id = Column(String, nullable=False, index=True)  # ID of affected resource
    resource_name = Column(String, nullable=True)  # Human-readable name (denormalized)

    # Change tracking (before/after values)
    changes = Column(JSON, nullable=True)  # {"field": {"old": value, "new": value}}

    # Request metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    request_id = Column(String, nullable=True)  # For correlating with application logs

    # Result
    status = Column(String, nullable=False)  # "success", "failure", "partial"
    error_message = Column(String, nullable=True)  # If status=failure

    # Indexes for common queries
    __table_args__ = (
        # Org-scoped time-range queries (most common)
        Index('idx_audit_org_timestamp', 'org_id', 'timestamp'),

        # Action-specific queries ("show all user deletions")
        Index('idx_audit_action', 'action'),

        # Resource-specific queries ("show all changes to Event X")
        Index('idx_audit_resource', 'resource_type', 'resource_id'),

        # User activity queries ("show all actions by admin@example.com")
        Index('idx_audit_user', 'user_id', 'timestamp'),
    )
```

### Action Naming Convention

**Format**: `{resource}.{operation}`

| Action | Description | Example |
|--------|-------------|---------|
| `auth.login` | User logged in | `auth.login` |
| `auth.logout` | User logged out | `auth.logout` |
| `auth.login_failed` | Failed login attempt | `auth.login_failed` |
| `auth.password_changed` | User changed password | `auth.password_changed` |
| `auth.password_reset` | User reset password via email | `auth.password_reset` |
| `auth.2fa_enabled` | User enabled 2FA | `auth.2fa_enabled` |
| `auth.2fa_disabled` | User disabled 2FA | `auth.2fa_disabled` |
| `person.create` | Admin created user account | `person.create` |
| `person.update` | Admin updated user profile | `person.update` |
| `person.delete` | Admin deleted user account | `person.delete` |
| `person.roles_changed` | Admin changed user roles | `person.roles_changed` |
| `event.create` | Admin created event | `event.create` |
| `event.update` | Admin updated event | `event.update` |
| `event.delete` | Admin deleted event | `event.delete` |
| `team.create` | Admin created team | `team.create` |
| `team.update` | Admin updated team | `team.update` |
| `team.delete` | Admin deleted team | `team.delete` |
| `team.member_added` | Admin added member to team | `team.member_added` |
| `team.member_removed` | Admin removed member from team | `team.member_removed` |
| `organization.update` | Admin updated org settings | `organization.update` |
| `invitation.sent` | Admin sent invitation | `invitation.sent` |
| `invitation.accepted` | User accepted invitation | `invitation.accepted` |
| `solver.run` | Admin ran schedule solver | `solver.run` |

---

## Audit Logger Service API

### Class Interface

```python
# api/services/audit_logger.py
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

class AuditLogger:
    """Service for writing immutable audit logs."""

    def log_action(
        self,
        db: Session,
        org_id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        changes: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        Log an audit event (append-only).

        Args:
            db: Database session
            org_id: Organization ID
            user_id: User who performed action
            action: Action name (format: "{resource}.{operation}")
            resource_type: Type of resource affected
            resource_id: ID of affected resource
            changes: Before/after values (optional)
            status: "success" | "failure" | "partial"
            error_message: Error details if status=failure
            request: FastAPI Request object (for IP, user agent)

        Returns:
            Created AuditLog entry

        Example:
            >>> logger.log_action(
            ...     db=db,
            ...     org_id="org_church_123",
            ...     user_id="person_admin_456",
            ...     action="person.delete",
            ...     resource_type="person",
            ...     resource_id="person_volunteer_789",
            ...     changes={"email": {"old": "old@example.com", "new": None}},
            ...     status="success",
            ...     request=request
            ... )
        """
        pass

    def log_auth_event(
        self,
        db: Session,
        action: str,
        user_email: str,
        status: str,
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        Log authentication event (login, logout, password change).

        Special handling for auth events:
        - May not have org_id (pre-authentication)
        - May not have user_id (failed login)

        Args:
            db: Database session
            action: "auth.login", "auth.logout", "auth.login_failed", etc.
            user_email: Email address (may not correspond to existing user)
            status: "success" | "failure"
            error_message: Error details if status=failure
            request: FastAPI Request object

        Example:
            >>> logger.log_auth_event(
            ...     db=db,
            ...     action="auth.login_failed",
            ...     user_email="attacker@example.com",
            ...     status="failure",
            ...     error_message="Invalid credentials",
            ...     request=request
            ... )
        """
        pass

    def query_logs(
        self,
        db: Session,
        org_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Query audit logs with filters.

        Args:
            db: Database session
            org_id: Organization ID (required for multi-tenant isolation)
            start_date: Start of time range (inclusive)
            end_date: End of time range (inclusive)
            action: Filter by action (e.g., "person.delete")
            user_id: Filter by user who performed action
            resource_type: Filter by resource type (e.g., "event")
            resource_id: Filter by specific resource
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            List of AuditLog entries (newest first)

        Example:
            >>> # Show all admin actions in last 24 hours
            >>> logs = logger.query_logs(
            ...     db=db,
            ...     org_id="org_church_123",
            ...     start_date=datetime.utcnow() - timedelta(days=1),
            ...     limit=100
            ... )

            >>> # Show all changes to specific event
            >>> logs = logger.query_logs(
            ...     db=db,
            ...     org_id="org_church_123",
            ...     resource_type="event",
            ...     resource_id="event_sunday_service_456"
            ... )
        """
        pass

    def export_logs_csv(
        self,
        db: Session,
        org_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """
        Export audit logs to CSV format (for compliance reports).

        CSV Columns:
            timestamp, user_email, action, resource_type, resource_id,
            changes, status, ip_address

        Args:
            db: Database session
            org_id: Organization ID
            start_date: Start of export range
            end_date: End of export range

        Returns:
            CSV content as string

        Example:
            >>> csv_content = logger.export_logs_csv(
            ...     db=db,
            ...     org_id="org_church_123",
            ...     start_date=datetime(2025, 10, 1),
            ...     end_date=datetime(2025, 10, 31)
            ... )
            >>> # Save to file or send via email
        """
        pass
```

---

## Integration with Endpoints

### Decorator Pattern (Automatic Logging)

```python
# api/utils/audit_decorators.py
from functools import wraps
from fastapi import Request

def audit_log(
    action: str,
    resource_type: str,
    get_resource_id: callable = None
):
    """
    Decorator for automatic audit logging.

    Args:
        action: Action name (e.g., "person.delete")
        resource_type: Resource type (e.g., "person")
        get_resource_id: Function to extract resource ID from args

    Example:
        @audit_log(action="person.delete", resource_type="person")
        @router.delete("/api/people/{person_id}")
        def delete_person(person_id: str, ...):
            # ... delete logic
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies
            request = kwargs.get('request')
            current_user = kwargs.get('current_user') or kwargs.get('admin')
            db = kwargs.get('db')

            # Execute action
            result = await func(*args, **kwargs)

            # Log after successful execution
            resource_id = get_resource_id(kwargs) if get_resource_id else kwargs.get('person_id') or kwargs.get('event_id')

            audit_logger.log_action(
                db=db,
                org_id=current_user.org_id,
                user_id=current_user.id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                status="success",
                request=request
            )

            return result
        return wrapper
    return decorator
```

### Manual Logging (For Complex Changes)

```python
# api/routers/people.py
@router.put("/api/people/{person_id}/roles")
def update_roles(
    person_id: str,
    request: RoleUpdate,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Update user roles with audit logging."""
    person = db.query(Person).filter(Person.id == person_id).first()

    if not person:
        raise HTTPException(404, "User not found")

    # Capture before state
    old_roles = person.roles.copy()

    # Update roles
    person.roles = request.roles
    db.commit()

    # Log with before/after values
    audit_logger.log_action(
        db=db,
        org_id=admin.org_id,
        user_id=admin.id,
        action="person.roles_changed",
        resource_type="person",
        resource_id=person_id,
        changes={
            "roles": {
                "old": old_roles,
                "new": request.roles
            }
        },
        status="success",
        request=request
    )

    return {"message": "Roles updated"}
```

---

## Audit Log Query API

### REST Endpoint

```python
# api/routers/audit.py
@router.get("/api/audit/logs")
def get_audit_logs(
    org_id: str = Query(...),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    action: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """
    Query audit logs (admin-only).

    Query Parameters:
        org_id: Organization ID (required)
        start_date: Start of time range (ISO 8601)
        end_date: End of time range (ISO 8601)
        action: Filter by action (e.g., "person.delete")
        user_id: Filter by user
        resource_type: Filter by resource type
        limit: Max results (default 100, max 1000)
        offset: Pagination offset

    Response:
        {
            "logs": [...],
            "total": 1523,
            "limit": 100,
            "offset": 0
        }
    """
    # Verify admin belongs to org
    verify_org_member(admin, org_id)

    # Query logs
    logs = audit_logger.query_logs(
        db=db,
        org_id=org_id,
        start_date=start_date,
        end_date=end_date,
        action=action,
        user_id=user_id,
        resource_type=resource_type,
        limit=limit,
        offset=offset
    )

    # Get total count
    total = db.query(AuditLog).filter(AuditLog.org_id == org_id).count()

    return {
        "logs": [log.to_dict() for log in logs],
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/api/audit/export")
def export_audit_logs(
    org_id: str = Query(...),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """
    Export audit logs to CSV (admin-only).

    Query Parameters:
        org_id: Organization ID (required)
        start_date: Start of export range (ISO 8601)
        end_date: End of export range (ISO 8601)

    Response:
        Content-Type: text/csv
        Content-Disposition: attachment; filename="audit_logs_2025-10-23.csv"
    """
    verify_org_member(admin, org_id)

    # Generate CSV
    csv_content = audit_logger.export_logs_csv(
        db=db,
        org_id=org_id,
        start_date=start_date,
        end_date=end_date
    )

    # Return as downloadable file
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=audit_logs_{start_date.date()}_to_{end_date.date()}.csv"
        }
    )
```

---

## Change Tracking Format

### Before/After Structure

```python
# Changes format: {"field": {"old": value, "new": value}}

# Example 1: User profile update
changes = {
    "name": {
        "old": "John Smith",
        "new": "John Doe"
    },
    "email": {
        "old": "john@old.com",
        "new": "john@new.com"
    }
}

# Example 2: Role change
changes = {
    "roles": {
        "old": ["volunteer"],
        "new": ["volunteer", "admin"]
    }
}

# Example 3: Deletion
changes = {
    "deleted": {
        "old": {"id": "person_123", "name": "John Doe", "email": "john@example.com"},
        "new": null
    }
}

# Example 4: Creation
changes = {
    "created": {
        "old": null,
        "new": {"id": "event_456", "title": "Sunday Service", "datetime": "2025-11-01T10:00:00"}
    }
}
```

### Sensitive Field Redaction

```python
# Redact sensitive fields in audit logs
REDACTED_FIELDS = ['password', 'hashed_password', 'totp_secret', 'recovery_codes']

def sanitize_changes(changes: dict) -> dict:
    """Redact sensitive fields from change tracking."""
    sanitized = {}
    for field, value in changes.items():
        if field in REDACTED_FIELDS:
            sanitized[field] = {
                "old": "[REDACTED]",
                "new": "[REDACTED]"
            }
        else:
            sanitized[field] = value
    return sanitized

# Example:
changes = {
    "password": {"old": "old_hash", "new": "new_hash"},
    "email": {"old": "old@example.com", "new": "new@example.com"}
}

# After sanitization:
{
    "password": {"old": "[REDACTED]", "new": "[REDACTED]"},
    "email": {"old": "old@example.com", "new": "new@example.com"}
}
```

---

## Retention and Cleanup

### Retention Policy

- **Default**: 90 days for all logs
- **Compliance**: 7 years for specific actions (user deletion, permission changes, data access)
- **Storage estimate**: 90 days × 1000 actions/day × 1KB/log = ~90MB

### Automated Cleanup

```python
# scripts/cleanup_audit_logs.py
from datetime import datetime, timedelta
from api.database import SessionLocal
from api.models import AuditLog

def cleanup_audit_logs():
    """Delete audit logs older than 90 days (except compliance-required)."""
    db = SessionLocal()

    # Define compliance-required actions (7-year retention)
    COMPLIANCE_ACTIONS = [
        'person.delete',
        'person.roles_changed',
        'auth.password_changed',
        'organization.update'
    ]

    # Delete non-compliance logs older than 90 days
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    deleted = db.query(AuditLog).filter(
        AuditLog.timestamp < cutoff_date,
        AuditLog.action.notin_(COMPLIANCE_ACTIONS)
    ).delete()

    db.commit()
    print(f"Deleted {deleted} audit logs older than 90 days")

    # Delete compliance logs older than 7 years
    compliance_cutoff = datetime.utcnow() - timedelta(days=7*365)

    deleted_compliance = db.query(AuditLog).filter(
        AuditLog.timestamp < compliance_cutoff,
        AuditLog.action.in_(COMPLIANCE_ACTIONS)
    ).delete()

    db.commit()
    print(f"Deleted {deleted_compliance} compliance audit logs older than 7 years")

# Run daily via cron
# 0 2 * * * /usr/bin/python /path/to/scripts/cleanup_audit_logs.py
```

---

## Performance Optimization

### Write Performance

```python
# Batch inserts for multiple audit logs
def log_batch_actions(db: Session, logs: list[dict]) -> None:
    """Insert multiple audit logs in single transaction."""
    audit_logs = [AuditLog(**log_data) for log_data in logs]
    db.bulk_save_objects(audit_logs)
    db.commit()

# Example: Bulk user import
users_created = []
for user_data in import_data:
    user = create_user(user_data)
    users_created.append({
        "org_id": org_id,
        "user_id": admin.id,
        "action": "person.create",
        "resource_type": "person",
        "resource_id": user.id,
        # ...
    })

# Single batch insert
log_batch_actions(db, users_created)
```

### Query Performance

```python
# Use composite index for common queries
# Index: idx_audit_org_timestamp on (org_id, timestamp)

# Optimized query (uses index)
logs = db.query(AuditLog).filter(
    AuditLog.org_id == "org_church_123",
    AuditLog.timestamp >= start_date,
    AuditLog.timestamp <= end_date
).order_by(AuditLog.timestamp.desc()).limit(100).all()

# Query plan: Index Scan using idx_audit_org_timestamp
```

### Partition Strategy (Future)

```sql
-- Partition audit_logs table by month (when exceeds 1 million records)
CREATE TABLE audit_logs_2025_10 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE audit_logs_2025_11 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- Automatic partition creation via monthly cron job
```

---

## Compliance Reports

### SOC 2 Audit Report

```python
# Generate SOC 2 compliance report
def generate_soc2_report(org_id: str, start_date: datetime, end_date: datetime) -> dict:
    """Generate SOC 2 compliance report showing all admin actions."""
    db = SessionLocal()

    # Query all admin actions in period
    logs = db.query(AuditLog).filter(
        AuditLog.org_id == org_id,
        AuditLog.timestamp >= start_date,
        AuditLog.timestamp <= end_date,
        AuditLog.action.in_([
            'person.create',
            'person.update',
            'person.delete',
            'person.roles_changed',
            'organization.update',
            'auth.password_changed'
        ])
    ).order_by(AuditLog.timestamp).all()

    # Group by action type
    report = {
        "organization": org_id,
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "total_actions": len(logs),
        "by_action": {},
        "by_user": {}
    }

    for log in logs:
        # Count by action
        report["by_action"][log.action] = report["by_action"].get(log.action, 0) + 1

        # Count by user
        report["by_user"][log.user_email] = report["by_user"].get(log.user_email, 0) + 1

    return report
```

### GDPR Data Access Report

```python
# Generate GDPR data access report (who accessed user's data)
def generate_gdpr_access_report(person_id: str, start_date: datetime, end_date: datetime) -> dict:
    """Show all access to specific user's data (GDPR Article 15)."""
    db = SessionLocal()

    logs = db.query(AuditLog).filter(
        AuditLog.resource_type == "person",
        AuditLog.resource_id == person_id,
        AuditLog.timestamp >= start_date,
        AuditLog.timestamp <= end_date
    ).order_by(AuditLog.timestamp).all()

    return {
        "person_id": person_id,
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "total_accesses": len(logs),
        "accesses": [
            {
                "timestamp": log.timestamp.isoformat(),
                "action": log.action,
                "accessed_by": log.user_email,
                "ip_address": log.ip_address
            }
            for log in logs
        ]
    }
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_audit_logger.py
def test_audit_log_creation():
    """Test audit log entry creation."""
    logger = AuditLogger()
    log = logger.log_action(
        db=db,
        org_id="org_test",
        user_id="user_test",
        action="person.delete",
        resource_type="person",
        resource_id="person_123",
        changes={"email": {"old": "test@example.com", "new": null}},
        status="success"
    )

    assert log.id is not None
    assert log.action == "person.delete"
    assert log.status == "success"
    assert log.changes["email"]["old"] == "test@example.com"

def test_audit_log_immutable():
    """Test that audit logs cannot be updated."""
    log = create_audit_log()

    # Attempt update should fail
    with pytest.raises(Exception):
        log.action = "different_action"
        db.commit()

def test_sensitive_field_redaction():
    """Test that passwords are redacted in audit logs."""
    changes = {
        "password": {"old": "old_hash", "new": "new_hash"},
        "email": {"old": "old@example.com", "new": "new@example.com"}
    }

    sanitized = sanitize_changes(changes)
    assert sanitized["password"]["old"] == "[REDACTED]"
    assert sanitized["email"]["old"] == "old@example.com"
```

### Integration Tests

```python
# tests/integration/test_audit_logging_db.py
def test_audit_log_query_performance(client, auth_headers):
    """Test audit log query performance with 10K records."""
    # Insert 10K audit logs
    for i in range(10000):
        create_audit_log(action=f"test.action_{i % 100}")

    # Query should complete in <100ms
    start = time.time()
    logs = audit_logger.query_logs(
        db=db,
        org_id="org_test",
        limit=100
    )
    duration = time.time() - start

    assert len(logs) == 100
    assert duration < 0.1  # <100ms

def test_audit_log_export_csv(client, auth_headers):
    """Test CSV export functionality."""
    response = client.get(
        "/api/audit/export",
        params={
            "org_id": "org_test",
            "start_date": "2025-10-01T00:00:00",
            "end_date": "2025-10-31T23:59:59"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    assert "Content-Disposition" in response.headers

    # Verify CSV format
    csv_content = response.content.decode()
    assert "timestamp,user_email,action" in csv_content
```

### E2E Tests

```python
# tests/e2e/test_audit_logging.py
def test_audit_trail_user_journey(page: Page):
    """Test that admin actions are logged and viewable."""
    # Login as admin
    page.goto("http://localhost:8000/login")
    page.locator('#email').fill("admin@example.com")
    page.locator('#password').fill("password123")
    page.locator('button[type="submit"]').click()

    # Navigate to admin console
    page.locator('[data-i18n="nav.admin"]').click()

    # Delete a user
    page.locator('button[data-action="delete-user"]').first.click()
    page.locator('button[data-i18n="common.buttons.confirm"]').click()

    # Navigate to audit logs
    page.locator('[data-i18n="admin.tabs.audit_logs"]').click()

    # Verify delete action logged
    expect(page.locator('table tbody tr').first).to_contain_text("person.delete")
    expect(page.locator('table tbody tr').first).to_contain_text("admin@example.com")
```

---

**Contract Status**: ✅ Complete
**Implementation Ready**: Yes
**Dependencies**: PostgreSQL 15+, FastAPI, multi-tenant isolation
**Estimated LOC**: ~600 lines (service: 300, endpoints: 150, decorators: 100, reports: 50)
