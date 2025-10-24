"""Billing and subscription management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from api.database import get_db
from api.dependencies import get_current_user, verify_org_member
from api.models import Person, Organization
from api.services.billing_service import BillingService
from api.services.usage_service import UsageService
from api.schemas.billing import SubscriptionResponse, UsageSummaryResponse

router = APIRouter(tags=["billing"])


@router.get("/billing/subscription")
def get_subscription(
    org_id: str = Query(..., description="Organization ID"),
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current subscription details for organization.

    Returns subscription tier, usage metrics, and billing information.

    Requires:
        - User must be member of the organization

    Returns:
        dict: Subscription details with usage metrics
        {
            "subscription": SubscriptionResponse,
            "usage": UsageSummaryResponse,
            "next_invoice": Optional[dict]
        }
    """
    # Verify user belongs to organization
    verify_org_member(current_user, org_id)

    # Get subscription
    billing_service = BillingService(db)
    subscription = billing_service.get_subscription(org_id)

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="No subscription found for organization"
        )

    # Get usage summary
    usage_service = UsageService(db)
    usage_summary = usage_service.get_usage_summary(org_id)

    # Get billing history for next invoice (if on paid plan)
    next_invoice = None
    if subscription.plan_tier != "free" and subscription.current_period_end:
        next_invoice = {
            "due_date": subscription.current_period_end.isoformat(),
            "amount": "Based on plan tier",  # Placeholder
            "status": subscription.status
        }

    return {
        "subscription": SubscriptionResponse.from_orm(subscription),
        "usage": usage_summary,
        "next_invoice": next_invoice
    }
