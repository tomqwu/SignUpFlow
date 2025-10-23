"""
Notifications API router.

Endpoints for listing, viewing, and managing email notifications.
Volunteers can view their own notifications, admins can view organization-wide stats.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from api.database import get_db
from api.dependencies import get_current_user, get_current_admin_user, verify_org_member
from api.models import (
    Person, Notification, NotificationType, NotificationStatus,
    EmailPreference, EmailFrequency, DeliveryLog
)
from api.schemas.notifications import (
    NotificationResponse, NotificationListResponse,
    EmailPreferenceResponse, EmailPreferenceUpdate,
    NotificationStatsResponse
)

router = APIRouter(tags=["notifications"])


# ============================================================================
# VOLUNTEER ENDPOINTS - View own notifications and manage preferences
# ============================================================================

@router.get("/notifications/", response_model=NotificationListResponse)
def list_notifications(
    org_id: str = Query(..., description="Organization ID"),
    status: Optional[str] = Query(None, description="Filter by status (pending, sent, delivered, etc.)"),
    type: Optional[str] = Query(None, description="Filter by type (assignment, reminder, update, cancellation)"),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List notifications for current user.

    Volunteers see only their own notifications.
    Admins see their own notifications (not organization-wide).

    **RBAC**: Authenticated user (volunteer or admin)
    **Multi-tenant**: Filtered by org_id and current user
    """
    # Verify user belongs to organization
    verify_org_member(current_user, org_id)

    # Build query - ALWAYS filter by recipient_id (user can only see own notifications)
    query = db.query(Notification).filter(
        Notification.org_id == org_id,
        Notification.recipient_id == current_user.id
    )

    # Apply filters
    if status:
        query = query.filter(Notification.status == status)
    if type:
        query = query.filter(Notification.type == type)

    # Get total count
    total = query.count()

    # Get paginated results
    notifications = query.order_by(desc(Notification.created_at))\
        .offset(offset)\
        .limit(limit)\
        .all()

    return {
        "notifications": notifications,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get single notification details.

    Users can only view their own notifications.

    **RBAC**: Authenticated user (must be notification recipient)
    **Multi-tenant**: Verified by recipient_id
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Verify user is the recipient
    if notification.recipient_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You can only view your own notifications"
        )

    return notification


@router.get("/notifications/preferences/me", response_model=EmailPreferenceResponse)
def get_my_email_preferences(
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's email notification preferences.

    Returns default preferences if none exist yet.

    **RBAC**: Authenticated user
    """
    email_pref = db.query(EmailPreference).filter(
        EmailPreference.person_id == current_user.id
    ).first()

    if not email_pref:
        # Return default preferences (not saved to database yet)
        return {
            "person_id": current_user.id,
            "org_id": current_user.org_id,
            "frequency": EmailFrequency.IMMEDIATE,
            "enabled_types": [
                NotificationType.ASSIGNMENT,
                NotificationType.REMINDER,
                NotificationType.UPDATE,
                NotificationType.CANCELLATION
            ],
            "language": getattr(current_user, 'language', 'en'),
            "timezone": getattr(current_user, 'timezone', 'UTC'),
            "digest_hour": 8
        }

    return email_pref


@router.put("/notifications/preferences/me", response_model=EmailPreferenceResponse)
def update_my_email_preferences(
    preferences: EmailPreferenceUpdate,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's email notification preferences.

    Allows users to:
    - Change notification frequency (immediate, daily, weekly, disabled)
    - Enable/disable specific notification types
    - Set language and timezone for emails
    - Set preferred digest delivery hour

    **RBAC**: Authenticated user
    """
    import secrets

    # Get or create email preferences
    email_pref = db.query(EmailPreference).filter(
        EmailPreference.person_id == current_user.id
    ).first()

    if not email_pref:
        # Create new preferences with unsubscribe token
        email_pref = EmailPreference(
            person_id=current_user.id,
            org_id=current_user.org_id,
            unsubscribe_token=secrets.token_urlsafe(32)
        )
        db.add(email_pref)

    # Update fields
    if preferences.frequency is not None:
        email_pref.frequency = preferences.frequency
    if preferences.enabled_types is not None:
        email_pref.enabled_types = preferences.enabled_types
    if preferences.language is not None:
        email_pref.language = preferences.language
    if preferences.timezone is not None:
        email_pref.timezone = preferences.timezone
    if preferences.digest_hour is not None:
        email_pref.digest_hour = preferences.digest_hour

    db.commit()
    db.refresh(email_pref)

    return email_pref


# ============================================================================
# ADMIN ENDPOINTS - Organization-wide notification statistics
# ============================================================================

@router.get("/notifications/stats/organization", response_model=NotificationStatsResponse)
def get_organization_notification_stats(
    org_id: str = Query(..., description="Organization ID"),
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get organization-wide notification statistics.

    Provides metrics for admins:
    - Total notifications sent by type
    - Delivery success rate
    - Open/click rates
    - Recent failures

    **RBAC**: Admin only
    **Multi-tenant**: Filtered by org_id
    """
    # Verify admin belongs to organization
    verify_org_member(admin, org_id)

    from datetime import datetime, timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Total notifications by status
    status_counts = db.query(
        Notification.status,
        func.count(Notification.id).label('count')
    ).filter(
        Notification.org_id == org_id,
        Notification.created_at >= cutoff_date
    ).group_by(Notification.status).all()

    # Total notifications by type
    type_counts = db.query(
        Notification.type,
        func.count(Notification.id).label('count')
    ).filter(
        Notification.org_id == org_id,
        Notification.created_at >= cutoff_date
    ).group_by(Notification.type).all()

    # Calculate success rate
    total_notifications = db.query(func.count(Notification.id)).filter(
        Notification.org_id == org_id,
        Notification.created_at >= cutoff_date
    ).scalar()

    delivered_notifications = db.query(func.count(Notification.id)).filter(
        Notification.org_id == org_id,
        Notification.created_at >= cutoff_date,
        Notification.status.in_([NotificationStatus.DELIVERED, NotificationStatus.OPENED, NotificationStatus.CLICKED])
    ).scalar()

    success_rate = (delivered_notifications / total_notifications * 100) if total_notifications > 0 else 0

    # Recent failures
    recent_failures = db.query(Notification).filter(
        Notification.org_id == org_id,
        Notification.status.in_([NotificationStatus.FAILED, NotificationStatus.BOUNCED]),
        Notification.created_at >= cutoff_date
    ).order_by(desc(Notification.created_at)).limit(10).all()

    return {
        "org_id": org_id,
        "days_analyzed": days,
        "total_notifications": total_notifications,
        "delivered_notifications": delivered_notifications,
        "success_rate": round(success_rate, 2),
        "status_breakdown": {status: count for status, count in status_counts},
        "type_breakdown": {type: count for type, count in type_counts},
        "recent_failures": recent_failures
    }


@router.post("/notifications/test/send")
def send_test_notification(
    recipient_email: str = Query(..., description="Email address to send test notification"),
    org_id: str = Query(..., description="Organization ID"),
    admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Send a test email notification to verify email configuration.

    Sends a test assignment notification to the specified email address.
    Useful for testing SendGrid configuration, SMTP settings, and template rendering.

    **RBAC**: Admin only
    **Multi-tenant**: Verified by admin's org_id
    """
    # Verify admin belongs to organization
    verify_org_member(admin, org_id)

    from api.services.notification_service import create_notification

    # Create test notification
    test_notification = create_notification(
        recipient_id=admin.id,  # Send to admin
        org_id=org_id,
        notification_type=NotificationType.ASSIGNMENT,
        template_data={
            "test_mode": True,
            "recipient_email": recipient_email
        },
        db=db,
        send_immediately=True
    )

    if not test_notification:
        raise HTTPException(
            status_code=500,
            detail="Failed to create test notification"
        )

    return {
        "message": f"Test notification sent to {recipient_email}",
        "notification_id": test_notification.id,
        "status": test_notification.status
    }
