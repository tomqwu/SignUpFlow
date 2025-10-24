"""Billing and subscription management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from api.database import get_db
from api.dependencies import get_current_user, verify_org_member, verify_admin_access
from api.models import Person, Organization
from api.services.billing_service import BillingService
from api.services.usage_service import UsageService
from api.services.stripe_service import StripeService
from api.schemas.billing import (
    SubscriptionResponse,
    UsageSummaryResponse,
    UpgradeRequest,
    TrialRequest
)

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


@router.post("/billing/subscription/upgrade")
def upgrade_subscription(
    request: UpgradeRequest,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upgrade organization to paid plan.

    This endpoint:
    1. Creates Stripe checkout session for payment collection
    2. Upgrades subscription when payment succeeds
    3. Records billing history and audit trail
    4. Updates usage limits to new plan tier
    5. Sends confirmation email (future)

    Requires:
        - User must be admin
        - User must belong to the organization
        - Organization must have active free plan

    Request Body:
        {
            "org_id": "org_123",
            "plan_tier": "starter",
            "billing_cycle": "monthly",
            "payment_method_id": "pm_xxx",
            "trial_days": 14
        }

    Returns:
        dict: Checkout session URL for payment
        {
            "success": true,
            "checkout_url": "https://checkout.stripe.com/...",
            "session_id": "cs_xxx",
            "message": "Checkout session created"
        }
    """
    # Verify admin belongs to organization
    verify_org_member(admin, request.org_id)

    # Get current subscription
    billing_service = BillingService(db)
    subscription = billing_service.get_subscription(request.org_id)

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="No subscription found for organization"
        )

    # Only allow upgrading from free tier for now
    if subscription.plan_tier != "free":
        raise HTTPException(
            status_code=400,
            detail=f"Organization already has {subscription.plan_tier} plan. Use change plan endpoint to switch plans."
        )

    # Construct Stripe price ID from plan tier and billing cycle
    price_id = f"price_{request.plan_tier}_{request.billing_cycle}"

    # Create Stripe checkout session
    stripe_service = StripeService(db)
    result = stripe_service.create_checkout_session(
        org_id=request.org_id,
        price_id=price_id,
        success_url=f"https://signupflow.io/app/billing?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"https://signupflow.io/app/billing?cancelled=true",
        trial_days=request.trial_days
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result["message"]
        )

    return result


@router.post("/billing/subscription/checkout-success")
def handle_checkout_success(
    session_id: str = Query(..., description="Stripe checkout session ID"),
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Handle successful checkout completion.

    This is called when user returns from Stripe checkout page after successful payment.
    The actual subscription update happens via webhook, but this endpoint can be used
    to retrieve updated subscription status.

    Requires:
        - User must be admin
        - Valid Stripe session ID

    Returns:
        dict: Updated subscription details
    """
    # In production, we would verify the session_id with Stripe
    # and ensure it matches the user's organization
    # For now, just return the current subscription

    # Get organization from session (this would come from Stripe session metadata)
    # For now, use admin's org_id
    org_id = admin.org_id

    billing_service = BillingService(db)
    subscription = billing_service.get_subscription(org_id)

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="No subscription found"
        )

    usage_service = UsageService(db)
    usage_summary = usage_service.get_usage_summary(org_id)

    return {
        "success": True,
        "subscription": SubscriptionResponse.from_orm(subscription),
        "usage": usage_summary,
        "message": "Subscription updated successfully"
    }


@router.post("/billing/subscription/trial")
def start_trial(
    request: TrialRequest,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start a 14-day trial of a paid plan.

    This endpoint:
    1. Validates organization is on free plan
    2. Updates subscription to trial status
    3. Sets trial_end_date to 14 days from now
    4. Updates usage limits to trial plan tier
    5. Records subscription event for audit trail
    6. Sends trial welcome email (future)

    Requires:
        - User must be admin
        - User must belong to the organization
        - Organization must have active free plan

    Request Body:
        {
            "org_id": "org_123",
            "plan_tier": "starter",
            "trial_days": 14
        }

    Returns:
        dict: Trial subscription details
        {
            "success": true,
            "subscription": SubscriptionResponse,
            "trial_end_date": "2025-11-06T...",
            "message": "Started 14-day trial of starter plan"
        }
    """
    # Verify admin belongs to organization
    verify_org_member(admin, request.org_id)

    # Start trial via BillingService
    billing_service = BillingService(db)
    result = billing_service.start_trial(
        org_id=request.org_id,
        plan_tier=request.plan_tier,
        trial_days=request.trial_days,
        admin_id=admin.id
    )

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    # Get updated usage summary
    usage_service = UsageService(db)
    usage_summary = usage_service.get_usage_summary(request.org_id)

    return {
        "success": True,
        "subscription": SubscriptionResponse.from_orm(result["subscription"]),
        "usage": usage_summary,
        "trial_end_date": result["trial_end_date"].isoformat(),
        "message": result["message"]
    }
