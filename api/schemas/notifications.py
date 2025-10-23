"""Notification schemas for API requests and responses."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Notification Schemas
# ============================================================================

class NotificationBase(BaseModel):
    """Base notification schema."""

    type: str = Field(..., description="Notification type (assignment, reminder, update, cancellation)")
    status: str = Field(..., description="Notification status (pending, sent, delivered, etc.)")
    event_id: Optional[str] = Field(None, description="Related event ID")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Template rendering data")


class NotificationResponse(NotificationBase):
    """Schema for notification response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: str
    recipient_id: str
    retry_count: int
    sendgrid_message_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list."""

    notifications: List[NotificationResponse]
    total: int
    limit: int
    offset: int


# ============================================================================
# Email Preference Schemas
# ============================================================================

class EmailPreferenceBase(BaseModel):
    """Base email preference schema."""

    frequency: str = Field(
        default="immediate",
        description="Email frequency (immediate, daily, weekly, disabled)"
    )
    enabled_types: List[str] = Field(
        default_factory=lambda: ["assignment", "reminder", "update", "cancellation"],
        description="List of enabled notification types"
    )
    language: str = Field(default="en", description="Email language preference (ISO 639-1 code)")
    timezone: str = Field(default="UTC", description="Timezone for digest scheduling")
    digest_hour: int = Field(
        default=8,
        ge=0,
        le=23,
        description="Hour to send digests (0-23)"
    )


class EmailPreferenceResponse(EmailPreferenceBase):
    """Schema for email preference response."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    person_id: str
    org_id: str
    unsubscribe_token: Optional[str] = None
    updated_at: Optional[datetime] = None


class EmailPreferenceUpdate(BaseModel):
    """Schema for updating email preferences."""

    frequency: Optional[str] = Field(
        None,
        description="Email frequency (immediate, daily, weekly, disabled)"
    )
    enabled_types: Optional[List[str]] = Field(
        None,
        description="List of enabled notification types"
    )
    language: Optional[str] = Field(None, description="Email language preference")
    timezone: Optional[str] = Field(None, description="Timezone for digest scheduling")
    digest_hour: Optional[int] = Field(
        None,
        ge=0,
        le=23,
        description="Hour to send digests (0-23)"
    )


# ============================================================================
# Notification Statistics Schemas
# ============================================================================

class NotificationStatsResponse(BaseModel):
    """Schema for organization notification statistics."""

    org_id: str
    days_analyzed: int
    total_notifications: int
    delivered_notifications: int
    success_rate: float = Field(description="Delivery success rate percentage")
    status_breakdown: Dict[str, int] = Field(
        description="Count of notifications by status"
    )
    type_breakdown: Dict[str, int] = Field(
        description="Count of notifications by type"
    )
    recent_failures: List[NotificationResponse] = Field(
        description="Recent failed notifications"
    )


# ============================================================================
# Delivery Log Schemas
# ============================================================================

class DeliveryLogResponse(BaseModel):
    """Schema for delivery log entry (SendGrid webhook event)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    notification_id: int
    event_type: str = Field(description="SendGrid event type (delivered, bounced, opened, etc.)")
    sendgrid_message_id: str
    timestamp: datetime
    reason: Optional[str] = Field(None, description="Bounce reason or error message")
    raw_event: Optional[Dict[str, Any]] = Field(None, description="Full SendGrid webhook payload")
    created_at: datetime
