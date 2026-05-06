"""Notification schemas for API requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# Notification Schemas
# ============================================================================


class NotificationBase(BaseModel):
    """Base notification schema."""

    type: str = Field(
        ..., description="Notification type (assignment, reminder, update, cancellation)"
    )
    status: str = Field(..., description="Notification status (pending, sent, delivered, etc.)")
    event_id: str | None = Field(None, description="Related event ID")
    template_data: dict[str, Any] | None = Field(None, description="Template rendering data")


class NotificationResponse(NotificationBase):
    """Schema for notification response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: str
    recipient_id: str
    retry_count: int
    sendgrid_message_id: str | None = None
    error_message: str | None = None
    created_at: datetime
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    opened_at: datetime | None = None
    clicked_at: datetime | None = None


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list."""

    notifications: list[NotificationResponse]
    total: int
    limit: int
    offset: int


# ============================================================================
# Email Preference Schemas
# ============================================================================


class EmailPreferenceBase(BaseModel):
    """Base email preference schema."""

    frequency: str = Field(
        default="immediate", description="Email frequency (immediate, daily, weekly, disabled)"
    )
    enabled_types: list[str] = Field(
        default_factory=lambda: ["assignment", "reminder", "update", "cancellation"],
        description="List of enabled notification types",
    )
    language: str = Field(default="en", description="Email language preference (ISO 639-1 code)")
    timezone: str = Field(default="UTC", description="Timezone for digest scheduling")
    digest_hour: int = Field(default=8, ge=0, le=23, description="Hour to send digests (0-23)")


class EmailPreferenceResponse(EmailPreferenceBase):
    """Schema for email preference response."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    person_id: str
    org_id: str
    unsubscribe_token: str | None = None
    updated_at: datetime | None = None


class EmailPreferenceUpdate(BaseModel):
    """Schema for updating email preferences."""

    frequency: str | None = Field(
        None, description="Email frequency (immediate, daily, weekly, disabled)"
    )
    enabled_types: list[str] | None = Field(None, description="List of enabled notification types")
    language: str | None = Field(None, description="Email language preference")
    timezone: str | None = Field(None, description="Timezone for digest scheduling")
    digest_hour: int | None = Field(None, ge=0, le=23, description="Hour to send digests (0-23)")


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
    status_breakdown: dict[str, int] = Field(description="Count of notifications by status")
    type_breakdown: dict[str, int] = Field(description="Count of notifications by type")
    recent_failures: list[NotificationResponse] = Field(description="Recent failed notifications")


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
    reason: str | None = Field(None, description="Bounce reason or error message")
    raw_event: dict[str, Any] | None = Field(None, description="Full SendGrid webhook payload")
    created_at: datetime
