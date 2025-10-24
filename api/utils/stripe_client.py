"""Stripe API client wrapper for billing operations.

This module provides a simplified interface to Stripe's API for subscription management.
All methods handle errors gracefully and return structured responses.

Environment Variables Required:
    STRIPE_SECRET_KEY: Stripe API secret key (sk_test_* or sk_live_*)
    STRIPE_WEBHOOK_SECRET: Stripe webhook signing secret (whsec_*)

Example Usage:
    from api.utils.stripe_client import StripeClient

    client = StripeClient()
    customer = client.create_customer(
        org_id="org_123",
        email="admin@example.com",
        name="Example Organization"
    )
"""

import os
import stripe
from typing import Optional, Dict, Any
from api.logging_config import logger
from api.utils.stripe_error_handler import handle_stripe_error, log_stripe_error

# Initialize Stripe with API key from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class StripeClient:
    """Wrapper for Stripe API operations with error handling."""

    def __init__(self):
        """Initialize Stripe client with API key from environment."""
        self.api_key = os.getenv("STRIPE_SECRET_KEY")
        if not self.api_key:
            logger.warning("STRIPE_SECRET_KEY not set - Stripe operations will fail")

    def create_customer(
        self,
        org_id: str,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Stripe customer for an organization.

        Args:
            org_id: Organization ID (stored in metadata)
            email: Customer email address
            name: Organization name (optional)
            metadata: Additional metadata (optional)

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "customer": Stripe customer object (if successful),
                    "customer_id": str (if successful),
                    "message": str,
                    "error_code": str (if failed)
                }

        Example:
            result = client.create_customer(
                org_id="org_123",
                email="admin@church.org",
                name="First Baptist Church"
            )
            if result["success"]:
                print(f"Customer ID: {result['customer_id']}")
            else:
                print(f"Error: {result['message']}")
        """
        try:
            customer_metadata = metadata or {}
            customer_metadata["org_id"] = org_id

            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=customer_metadata
            )

            logger.info(f"Created Stripe customer {customer.id} for org {org_id}")
            return {
                "success": True,
                "customer": customer,
                "customer_id": customer.id,
                "message": "Customer created successfully"
            }

        except Exception as e:
            log_stripe_error(e, "create_customer", {"org_id": org_id, "email": email})
            error_info = handle_stripe_error(e)
            return {
                "success": False,
                "message": error_info["user_message"],
                "error_code": error_info["error_code"],
                "error_type": error_info["error_type"]
            }

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new subscription for a customer.

        Args:
            customer_id: Stripe customer ID (cus_xxx)
            price_id: Stripe price ID (price_xxx)
            trial_days: Number of trial days (optional, default: None)
            metadata: Additional metadata (optional)

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "subscription": Stripe subscription object (if successful),
                    "subscription_id": str (if successful),
                    "message": str,
                    "error_code": str (if failed)
                }

        Example:
            result = client.create_subscription(
                customer_id="cus_xxx",
                price_id="price_starter_monthly",
                trial_days=14
            )
            if result["success"]:
                print(f"Subscription ID: {result['subscription_id']}")
        """
        try:
            subscription_params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "metadata": metadata or {}
            }

            # Add trial period if specified
            if trial_days is not None:
                subscription_params["trial_period_days"] = trial_days

            subscription = stripe.Subscription.create(**subscription_params)

            logger.info(
                f"Created subscription {subscription.id} for customer {customer_id} "
                f"with price {price_id} (trial: {trial_days} days)"
            )
            return {
                "success": True,
                "subscription": subscription,
                "subscription_id": subscription.id,
                "message": "Subscription created successfully"
            }

        except Exception as e:
            log_stripe_error(e, "create_subscription", {
                "customer_id": customer_id,
                "price_id": price_id,
                "trial_days": trial_days
            })
            error_info = handle_stripe_error(e)
            return {
                "success": False,
                "message": error_info["user_message"],
                "error_code": error_info["error_code"],
                "error_type": error_info["error_type"]
            }

    def update_subscription(
        self,
        subscription_id: str,
        price_id: str,
        proration_behavior: str = "create_prorations"
    ) -> Dict[str, Any]:
        """
        Update an existing subscription (upgrade or downgrade).

        Args:
            subscription_id: Stripe subscription ID (sub_xxx)
            price_id: New Stripe price ID (price_xxx)
            proration_behavior: How to handle prorations (default: "create_prorations")
                Options: "create_prorations", "none", "always_invoice"

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "subscription": Updated Stripe subscription object (if successful),
                    "message": str,
                    "error_code": str (if failed)
                }

        Example:
            # Upgrade from Starter to Pro
            result = client.update_subscription(
                subscription_id="sub_xxx",
                price_id="price_pro_monthly"
            )
            if result["success"]:
                print(f"Subscription updated: {result['subscription']['id']}")
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            # Update the subscription item with new price
            stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": price_id
                }],
                proration_behavior=proration_behavior
            )

            updated_subscription = stripe.Subscription.retrieve(subscription_id)

            logger.info(
                f"Updated subscription {subscription_id} to price {price_id} "
                f"(proration: {proration_behavior})"
            )
            return {
                "success": True,
                "subscription": updated_subscription,
                "message": "Subscription updated successfully"
            }

        except Exception as e:
            log_stripe_error(e, "update_subscription", {
                "subscription_id": subscription_id,
                "price_id": price_id,
                "proration_behavior": proration_behavior
            })
            error_info = handle_stripe_error(e)
            return {
                "success": False,
                "message": error_info["user_message"],
                "error_code": error_info["error_code"],
                "error_type": error_info["error_type"]
            }

    def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True
    ) -> Dict[str, Any]:
        """
        Cancel a subscription immediately or at period end.

        Args:
            subscription_id: Stripe subscription ID (sub_xxx)
            at_period_end: If True, cancel at end of billing period (default: True)
                          If False, cancel immediately

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "subscription": Cancelled/updated Stripe subscription object (if successful),
                    "message": str,
                    "error_code": str (if failed)
                }

        Example:
            # Cancel at period end (graceful)
            result = client.cancel_subscription(
                subscription_id="sub_xxx",
                at_period_end=True
            )

            # Cancel immediately
            result = client.cancel_subscription(
                subscription_id="sub_xxx",
                at_period_end=False
            )
        """
        try:
            if at_period_end:
                # Schedule cancellation at period end
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                logger.info(f"Scheduled cancellation for subscription {subscription_id} at period end")
                message = "Subscription will be cancelled at the end of the current billing period"
            else:
                # Cancel immediately
                subscription = stripe.Subscription.delete(subscription_id)
                logger.info(f"Cancelled subscription {subscription_id} immediately")
                message = "Subscription cancelled immediately"

            return {
                "success": True,
                "subscription": subscription,
                "message": message
            }

        except Exception as e:
            log_stripe_error(e, "cancel_subscription", {
                "subscription_id": subscription_id,
                "at_period_end": at_period_end
            })
            error_info = handle_stripe_error(e)
            return {
                "success": False,
                "message": error_info["user_message"],
                "error_code": error_info["error_code"],
                "error_type": error_info["error_type"]
            }

    def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
        set_as_default: bool = True
    ) -> Dict[str, Any]:
        """
        Attach a payment method to a customer.

        Args:
            customer_id: Stripe customer ID (cus_xxx)
            payment_method_id: Stripe payment method ID (pm_xxx)
            set_as_default: Set as default payment method (default: True)

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "payment_method": Stripe payment method object (if successful),
                    "message": str,
                    "error_code": str (if failed)
                }

        Example:
            result = client.attach_payment_method(
                customer_id="cus_xxx",
                payment_method_id="pm_xxx",
                set_as_default=True
            )
            if result["success"]:
                print(f"Payment method attached: {result['payment_method']['id']}")
        """
        try:
            # Attach payment method to customer
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )

            # Set as default payment method if requested
            if set_as_default:
                stripe.Customer.modify(
                    customer_id,
                    invoice_settings={"default_payment_method": payment_method_id}
                )
                logger.info(
                    f"Attached payment method {payment_method_id} to customer {customer_id} "
                    f"and set as default"
                )
                message = "Payment method attached and set as default successfully"
            else:
                logger.info(
                    f"Attached payment method {payment_method_id} to customer {customer_id}"
                )
                message = "Payment method attached successfully"

            return {
                "success": True,
                "payment_method": payment_method,
                "message": message
            }

        except Exception as e:
            log_stripe_error(e, "attach_payment_method", {
                "customer_id": customer_id,
                "payment_method_id": payment_method_id,
                "set_as_default": set_as_default
            })
            error_info = handle_stripe_error(e)
            return {
                "success": False,
                "message": error_info["user_message"],
                "error_code": error_info["error_code"],
                "error_type": error_info["error_type"]
            }

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature and parse event.

        Args:
            payload: Raw request body (bytes)
            signature: Stripe-Signature header value

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "event": Parsed Stripe event object (if successful),
                    "message": str,
                    "error_code": str (if failed)
                }

        Example:
            result = client.verify_webhook_signature(
                payload=request.body(),
                signature=request.headers["Stripe-Signature"]
            )
            if result["success"]:
                print(f"Event type: {result['event']['type']}")
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if not webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET not configured")
            return {
                "success": False,
                "message": "Webhook secret not configured. Please contact support.",
                "error_code": "webhook_secret_missing",
                "error_type": "configuration_error"
            }

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            logger.info(f"Verified webhook event: {event['type']}")
            return {
                "success": True,
                "event": event,
                "message": "Webhook signature verified successfully"
            }

        except Exception as e:
            log_stripe_error(e, "verify_webhook_signature", {
                "signature_present": bool(signature)
            })
            error_info = handle_stripe_error(e)
            return {
                "success": False,
                "message": error_info["user_message"],
                "error_code": error_info["error_code"],
                "error_type": error_info["error_type"]
            }

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Retrieve a subscription by ID.

        Args:
            subscription_id: Stripe subscription ID (sub_xxx)

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "subscription": Stripe subscription object (if successful),
                    "message": str,
                    "error_code": str (if failed)
                }

        Example:
            result = client.get_subscription("sub_xxx")
            if result["success"]:
                print(f"Status: {result['subscription']['status']}")
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "success": True,
                "subscription": subscription,
                "message": "Subscription retrieved successfully"
            }
        except Exception as e:
            log_stripe_error(e, "get_subscription", {"subscription_id": subscription_id})
            error_info = handle_stripe_error(e)
            return {
                "success": False,
                "message": error_info["user_message"],
                "error_code": error_info["error_code"],
                "error_type": error_info["error_type"]
            }

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve a customer by ID.

        Args:
            customer_id: Stripe customer ID (cus_xxx)

        Returns:
            dict: Result with success status
                {
                    "success": bool,
                    "customer": Stripe customer object (if successful),
                    "message": str,
                    "error_code": str (if failed)
                }

        Example:
            result = client.get_customer("cus_xxx")
            if result["success"]:
                print(f"Email: {result['customer']['email']}")
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {
                "success": True,
                "customer": customer,
                "message": "Customer retrieved successfully"
            }
        except Exception as e:
            log_stripe_error(e, "get_customer", {"customer_id": customer_id})
            error_info = handle_stripe_error(e)
            return {
                "success": False,
                "message": error_info["user_message"],
                "error_code": error_info["error_code"],
                "error_type": error_info["error_type"]
            }
