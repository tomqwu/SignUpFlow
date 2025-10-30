"""Pydantic schemas for billing and subscription operations."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubscriptionResponse(BaseModel):
    """Response schema for subscription details."""

    id: int = Field(..., description="Subscription ID")
    org_id: str = Field(..., description="Organization ID")
    plan_tier: str = Field(..., description="Plan tier (free, starter, pro, enterprise)")
    billing_cycle: Optional[str] = Field(None, description="Billing cycle (monthly, annual)")
    status: str = Field(..., description="Subscription status (active, trialing, past_due, cancelled)")
    trial_end_date: Optional[datetime] = Field(None, description="Trial end date")
    current_period_start: Optional[datetime] = Field(None, description="Current billing period start")
    current_period_end: Optional[datetime] = Field(None, description="Current billing period end")
    cancel_at_period_end: bool = Field(False, description="Scheduled for cancellation")
    pending_downgrade: Optional[Dict[str, Any]] = Field(None, description="Scheduled downgrade details (new_plan_tier, effective_date, credit_amount_cents)")
    created_at: datetime = Field(..., description="Subscription created timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "org_id": "org_123",
                "plan_tier": "starter",
                "billing_cycle": "monthly",
                "status": "trialing",
                "trial_end_date": "2025-11-06T12:00:00",
                "current_period_start": "2025-10-23T12:00:00",
                "current_period_end": "2025-11-23T12:00:00",
                "cancel_at_period_end": False,
                "created_at": "2025-10-23T12:00:00",
                "updated_at": "2025-10-23T12:00:00"
            }
        }
    )


class UpgradeRequest(BaseModel):
    """Request schema for upgrading to paid plan."""

    org_id: str = Field(..., description="Organization ID")
    plan_tier: str = Field(..., description="Plan tier (starter, pro, enterprise)")
    billing_cycle: str = Field(..., description="Billing cycle (monthly, annual)")
    payment_method_id: Optional[str] = Field(None, description="Stripe payment method ID")
    trial_days: Optional[int] = Field(14, description="Number of trial days (default: 14)")

    @field_validator("plan_tier")
    @classmethod
    def validate_plan_tier(cls, v: str) -> str:
        """Validate plan tier is one of the paid tiers."""
        if v not in ["starter", "pro", "enterprise"]:
            raise ValueError("Plan tier must be starter, pro, or enterprise")
        return v

    @field_validator("billing_cycle")
    @classmethod
    def validate_billing_cycle(cls, v: str) -> str:
        """Validate billing cycle."""
        if v not in ["monthly", "annual"]:
            raise ValueError("Billing cycle must be monthly or annual")
        return v

    @field_validator("trial_days")
    @classmethod
    def validate_trial_days(cls, v: Optional[int]) -> Optional[int]:
        """Validate trial days."""
        if v is not None and (v < 0 or v > 30):
            raise ValueError("Trial days must be between 0 and 30")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "org_id": "org_123",
                "plan_tier": "starter",
                "billing_cycle": "monthly",
                "payment_method_id": "pm_xxx",
                "trial_days": 14
            }
        }
    )


class DowngradeRequest(BaseModel):
    """Request schema for downgrading plan."""

    org_id: str = Field(..., description="Organization ID")
    new_plan_tier: str = Field(..., description="New plan tier (free, starter, pro)")
    reason: Optional[str] = Field(None, description="Reason for downgrade")

    @field_validator("new_plan_tier")
    @classmethod
    def validate_new_plan_tier(cls, v: str) -> str:
        """Validate new plan tier."""
        if v not in ["free", "starter", "pro"]:
            raise ValueError("New plan tier must be free, starter, or pro")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "org_id": "org_123",
                "new_plan_tier": "free",
                "reason": "Cost reduction"
            }
        }
    )


class ChangePlanRequest(BaseModel):
    """Request schema for changing plan (upgrade or downgrade)."""

    org_id: str = Field(..., description="Organization ID")
    new_plan_tier: str = Field(..., description="New plan tier")
    new_billing_cycle: Optional[str] = Field(None, description="New billing cycle (monthly, annual)")

    @field_validator("new_plan_tier")
    @classmethod
    def validate_new_plan_tier(cls, v: str) -> str:
        """Validate new plan tier."""
        if v not in ["free", "starter", "pro", "enterprise"]:
            raise ValueError("Plan tier must be free, starter, pro, or enterprise")
        return v

    @field_validator("new_billing_cycle")
    @classmethod
    def validate_new_billing_cycle(cls, v: Optional[str]) -> Optional[str]:
        """Validate new billing cycle."""
        if v is not None and v not in ["monthly", "annual"]:
            raise ValueError("Billing cycle must be monthly or annual")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "org_id": "org_123",
                "new_plan_tier": "pro",
                "new_billing_cycle": "annual"
            }
        }
    )


class TrialRequest(BaseModel):
    """Request schema for starting trial."""

    org_id: str = Field(..., description="Organization ID")
    plan_tier: str = Field(..., description="Plan tier to trial (starter, pro, enterprise)")
    billing_cycle: str = Field("monthly", description="Billing cycle after trial")
    trial_days: int = Field(14, description="Number of trial days")

    @field_validator("plan_tier")
    @classmethod
    def validate_plan_tier(cls, v: str) -> str:
        """Validate plan tier."""
        if v not in ["starter", "pro", "enterprise"]:
            raise ValueError("Trial plan must be starter, pro, or enterprise")
        return v

    @field_validator("trial_days")
    @classmethod
    def validate_trial_days(cls, v: int) -> int:
        """Validate trial days."""
        if v < 1 or v > 30:
            raise ValueError("Trial days must be between 1 and 30")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "org_id": "org_123",
                "plan_tier": "starter",
                "billing_cycle": "monthly",
                "trial_days": 14
            }
        }
    )


class CancelRequest(BaseModel):
    """Request schema for cancelling subscription."""

    org_id: str = Field(..., description="Organization ID")
    immediately: bool = Field(False, description="Cancel immediately (True) or at period end (False)")
    reason: Optional[str] = Field(None, description="Reason for cancellation")
    feedback: Optional[str] = Field(None, description="Additional feedback")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "org_id": "org_123",
                "immediately": False,
                "reason": "No longer needed",
                "feedback": "Great service but we don't need it anymore"
            }
        }
    )


class WebhookEvent(BaseModel):
    """Schema for Stripe webhook event."""

    id: str = Field(..., description="Stripe event ID")
    type: str = Field(..., description="Event type (e.g., customer.subscription.updated)")
    data: Dict[str, Any] = Field(..., description="Event data")
    created: int = Field(..., description="Event creation timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "evt_xxx",
                "type": "customer.subscription.updated",
                "data": {
                    "object": {
                        "id": "sub_xxx",
                        "status": "active"
                    }
                },
                "created": 1698091200
            }
        }
    )


class UsageMetricsResponse(BaseModel):
    """Response schema for usage metrics."""

    metric_type: str = Field(..., description="Type of metric")
    current_value: int = Field(..., description="Current usage value")
    plan_limit: Optional[int] = Field(None, description="Plan limit (None = unlimited)")
    percentage_used: float = Field(..., description="Percentage of limit used")
    last_updated: datetime = Field(..., description="Last updated timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "metric_type": "volunteers_count",
                "current_value": 25,
                "plan_limit": 50,
                "percentage_used": 50.0,
                "last_updated": "2025-10-23T12:00:00"
            }
        }
    )


class UsageSummaryResponse(BaseModel):
    """Response schema for complete usage summary."""

    plan_tier: str = Field(..., description="Current plan tier")
    limits: Dict[str, Optional[int]] = Field(..., description="Plan limits")
    usage: Dict[str, Any] = Field(..., description="Current usage by metric type")
    warnings: List[str] = Field(default_factory=list, description="List of approaching limits")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "plan_tier": "starter",
                "limits": {
                    "volunteers": 50,
                    "events_per_month": 200,
                    "storage_mb": 1000,
                    "api_calls_per_day": 10000
                },
                "usage": {
                    "volunteers_count": {
                        "current": 45,
                        "limit": 50,
                        "percentage": 90.0
                    }
                },
                "warnings": [
                    "volunteers_count: 45/50 (90% used)"
                ]
            }
        }
    )


class BillingHistoryResponse(BaseModel):
    """Response schema for billing history record."""

    id: int = Field(..., description="Record ID")
    event_type: str = Field(..., description="Event type (charge, refund, etc.)")
    amount_cents: int = Field(..., description="Amount in cents")
    currency: str = Field(..., description="Currency code (e.g., usd)")
    payment_status: str = Field(..., description="Payment status (succeeded, failed, pending)")
    description: Optional[str] = Field(None, description="Event description")
    event_timestamp: datetime = Field(..., description="Event timestamp")
    invoice_pdf_url: Optional[str] = Field(None, description="Invoice PDF URL")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "event_type": "charge",
                "amount_cents": 2900,
                "currency": "usd",
                "payment_status": "succeeded",
                "description": "Payment for starter plan",
                "event_timestamp": "2025-10-23T12:00:00",
                "invoice_pdf_url": "https://stripe.com/invoice.pdf"
            }
        }
    )


class PaymentMethodResponse(BaseModel):
    """Response schema for payment method."""

    id: int = Field(..., description="Payment method ID")
    card_brand: Optional[str] = Field(None, description="Card brand (visa, mastercard, etc.)")
    card_last4: Optional[str] = Field(None, description="Last 4 digits of card")
    exp_month: Optional[int] = Field(None, description="Expiration month")
    exp_year: Optional[int] = Field(None, description="Expiration year")
    is_primary: bool = Field(..., description="Is primary payment method")
    is_active: bool = Field(..., description="Is active")
    added_at: datetime = Field(..., description="When payment method was added")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "card_brand": "visa",
                "card_last4": "4242",
                "exp_month": 12,
                "exp_year": 2025,
                "is_primary": True,
                "is_active": True,
                "added_at": "2025-10-23T12:00:00"
            }
        }
    )
