"""Stripe integration service for subscription management.

This service handles all Stripe API interactions for billing operations.
It coordinates between Stripe and the local database.

Example Usage:
    from api.services.stripe_service import StripeService

    stripe_service = StripeService(db)
    result = stripe_service.upgrade_to_paid(
        org_id="org_123",
        price_id="price_starter_monthly",
        trial_days=14
    )
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from api.models import Organization, Subscription, PaymentMethod
from api.utils.stripe_client import StripeClient
from api.logging_config import logger


class StripeService:
    """Service for Stripe-specific billing operations."""

    def __init__(self, db: Session):
        """
        Initialize Stripe service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.stripe_client = StripeClient()

    def upgrade_to_paid(
        self,
        org_id: str,
        price_id: str,
        trial_days: Optional[int] = 14
    ) -> Dict[str, Any]:
        """
        Upgrade organization from free to paid plan.

        This creates a Stripe customer and subscription, then updates local database.

        Args:
            org_id: Organization ID
            price_id: Stripe price ID (price_xxx)
            trial_days: Number of trial days (default: 14)

        Returns:
            dict: Result with success status and subscription details
                {
                    "success": bool,
                    "subscription": Subscription object,
                    "message": str,
                    "stripe_subscription_id": str
                }

        Example:
            result = stripe_service.upgrade_to_paid(
                org_id="org_123",
                price_id="price_starter_monthly",
                trial_days=14
            )
            if result["success"]:
                print(f"Subscription ID: {result['stripe_subscription_id']}")
        """
        try:
            # Get organization and current subscription
            org = self.db.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                return {"success": False, "message": "Organization not found"}

            subscription = self.db.query(Subscription).filter(
                Subscription.org_id == org_id
            ).first()

            if not subscription:
                return {"success": False, "message": "No subscription record found"}

            # Create or retrieve Stripe customer
            if not subscription.stripe_customer_id:
                admin = next((p for p in org.people if "admin" in (p.roles or [])), None)
                customer_email = admin.email if admin else f"{org_id}@signupflow.io"

                customer = self.stripe_client.create_customer(
                    org_id=org_id,
                    email=customer_email,
                    name=org.name
                )

                if not customer:
                    return {"success": False, "message": "Failed to create Stripe customer"}

                subscription.stripe_customer_id = customer["id"]

            # Create Stripe subscription
            stripe_subscription = self.stripe_client.create_subscription(
                customer_id=subscription.stripe_customer_id,
                price_id=price_id,
                trial_days=trial_days,
                metadata={"org_id": org_id}
            )

            if not stripe_subscription:
                return {"success": False, "message": "Failed to create Stripe subscription"}

            # Determine plan tier from price_id
            plan_tier = self._get_tier_from_price_id(price_id)
            billing_cycle = "monthly" if "monthly" in price_id else "annual"

            # Update local subscription record
            subscription.stripe_subscription_id = stripe_subscription["id"]
            subscription.plan_tier = plan_tier
            subscription.billing_cycle = billing_cycle
            subscription.status = stripe_subscription["status"]  # "trialing" or "active"
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_subscription["current_period_start"]
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_subscription["current_period_end"]
            )

            if stripe_subscription.get("trial_end"):
                subscription.trial_end_date = datetime.fromtimestamp(
                    stripe_subscription["trial_end"]
                )

            self.db.commit()
            self.db.refresh(subscription)

            logger.info(
                f"Upgraded org {org_id} to {plan_tier} plan "
                f"(Stripe subscription: {stripe_subscription['id']})"
            )

            return {
                "success": True,
                "subscription": subscription,
                "stripe_subscription_id": stripe_subscription["id"],
                "message": f"Successfully upgraded to {plan_tier} plan"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error upgrading org {org_id} to paid plan: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }

    def change_plan(
        self,
        org_id: str,
        new_price_id: str
    ) -> Dict[str, Any]:
        """
        Change organization's subscription plan (upgrade or downgrade).

        Args:
            org_id: Organization ID
            new_price_id: New Stripe price ID

        Returns:
            dict: Result with success status and details
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.org_id == org_id
            ).first()

            if not subscription or not subscription.stripe_subscription_id:
                return {"success": False, "message": "No active paid subscription found"}

            # Update Stripe subscription
            updated_stripe_sub = self.stripe_client.update_subscription(
                subscription_id=subscription.stripe_subscription_id,
                price_id=new_price_id
            )

            if not updated_stripe_sub:
                return {"success": False, "message": "Failed to update Stripe subscription"}

            # Update local database
            previous_plan = subscription.plan_tier
            new_plan = self._get_tier_from_price_id(new_price_id)
            billing_cycle = "monthly" if "monthly" in new_price_id else "annual"

            subscription.plan_tier = new_plan
            subscription.billing_cycle = billing_cycle
            subscription.status = updated_stripe_sub["status"]

            self.db.commit()
            self.db.refresh(subscription)

            logger.info(f"Changed plan for org {org_id} from {previous_plan} to {new_plan}")

            return {
                "success": True,
                "subscription": subscription,
                "message": f"Plan changed from {previous_plan} to {new_plan}"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error changing plan for org {org_id}: {e}")
            return {"success": False, "message": str(e)}

    def cancel_subscription(
        self,
        org_id: str,
        at_period_end: bool = True
    ) -> Dict[str, Any]:
        """
        Cancel organization's subscription.

        Args:
            org_id: Organization ID
            at_period_end: Cancel at period end (True) or immediately (False)

        Returns:
            dict: Result with success status
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.org_id == org_id
            ).first()

            if not subscription or not subscription.stripe_subscription_id:
                return {"success": False, "message": "No active subscription found"}

            # Cancel in Stripe
            cancelled = self.stripe_client.cancel_subscription(
                subscription_id=subscription.stripe_subscription_id,
                at_period_end=at_period_end
            )

            if not cancelled:
                return {"success": False, "message": "Failed to cancel in Stripe"}

            # Update local database
            if at_period_end:
                subscription.cancel_at_period_end = True
                message = "Subscription will cancel at period end"
            else:
                subscription.status = "cancelled"
                subscription.plan_tier = "free"
                message = "Subscription cancelled immediately"

            self.db.commit()
            self.db.refresh(subscription)

            logger.info(f"Cancelled subscription for org {org_id} (at_period_end={at_period_end})")

            return {
                "success": True,
                "subscription": subscription,
                "message": message
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cancelling subscription for org {org_id}: {e}")
            return {"success": False, "message": str(e)}

    def save_payment_method(
        self,
        org_id: str,
        payment_method_id: str,
        card_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save payment method for organization.

        Args:
            org_id: Organization ID
            payment_method_id: Stripe payment method ID
            card_details: Card details from Stripe (brand, last4, exp_month, exp_year)

        Returns:
            dict: Result with success status
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.org_id == org_id
            ).first()

            if not subscription or not subscription.stripe_customer_id:
                return {"success": False, "message": "No Stripe customer found"}

            # Attach payment method in Stripe
            attached = self.stripe_client.attach_payment_method(
                customer_id=subscription.stripe_customer_id,
                payment_method_id=payment_method_id,
                set_as_default=True
            )

            if not attached:
                return {"success": False, "message": "Failed to attach payment method"}

            # Save to local database
            payment_method = PaymentMethod(
                org_id=org_id,
                stripe_payment_method_id=payment_method_id,
                card_brand=card_details.get("brand"),
                card_last4=card_details.get("last4"),
                exp_month=card_details.get("exp_month"),
                exp_year=card_details.get("exp_year"),
                is_primary=True
            )

            # Set other payment methods as non-primary
            self.db.query(PaymentMethod).filter(
                PaymentMethod.org_id == org_id,
                PaymentMethod.is_primary == True
            ).update({"is_primary": False})

            self.db.add(payment_method)
            self.db.commit()

            logger.info(f"Saved payment method for org {org_id}")

            return {
                "success": True,
                "payment_method": payment_method,
                "message": "Payment method saved successfully"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving payment method for org {org_id}: {e}")
            return {"success": False, "message": str(e)}

    def _get_tier_from_price_id(self, price_id: str) -> str:
        """
        Extract plan tier from Stripe price ID.

        Args:
            price_id: Stripe price ID (e.g., "price_starter_monthly")

        Returns:
            str: Plan tier (starter, pro, enterprise)
        """
        price_lower = price_id.lower()

        if "starter" in price_lower:
            return "starter"
        elif "pro" in price_lower:
            return "pro"
        elif "enterprise" in price_lower:
            return "enterprise"
        else:
            logger.warning(f"Unknown price ID format: {price_id}, defaulting to starter")
            return "starter"
