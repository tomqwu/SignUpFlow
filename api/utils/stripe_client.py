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
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new Stripe customer for an organization.

        Args:
            org_id: Organization ID (stored in metadata)
            email: Customer email address
            name: Organization name (optional)
            metadata: Additional metadata (optional)

        Returns:
            dict: Stripe customer object with id, email, metadata
            None: If creation fails

        Example:
            customer = client.create_customer(
                org_id="org_123",
                email="admin@church.org",
                name="First Baptist Church"
            )
            # Returns: {"id": "cus_xxx", "email": "admin@church.org", ...}
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
            return customer

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer for org {org_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating customer for org {org_id}: {e}")
            return None

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new subscription for a customer.

        Args:
            customer_id: Stripe customer ID (cus_xxx)
            price_id: Stripe price ID (price_xxx)
            trial_days: Number of trial days (optional, default: None)
            metadata: Additional metadata (optional)

        Returns:
            dict: Stripe subscription object with id, status, trial_end, etc.
            None: If creation fails

        Example:
            subscription = client.create_subscription(
                customer_id="cus_xxx",
                price_id="price_starter_monthly",
                trial_days=14
            )
            # Returns: {"id": "sub_xxx", "status": "trialing", ...}
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
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating subscription: {e}")
            return None

    def update_subscription(
        self,
        subscription_id: str,
        price_id: str,
        proration_behavior: str = "create_prorations"
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing subscription (upgrade or downgrade).

        Args:
            subscription_id: Stripe subscription ID (sub_xxx)
            price_id: New Stripe price ID (price_xxx)
            proration_behavior: How to handle prorations (default: "create_prorations")
                Options: "create_prorations", "none", "always_invoice"

        Returns:
            dict: Updated Stripe subscription object
            None: If update fails

        Example:
            # Upgrade from Starter to Pro
            subscription = client.update_subscription(
                subscription_id="sub_xxx",
                price_id="price_pro_monthly"
            )
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
            return updated_subscription

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error updating subscription {subscription_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error updating subscription {subscription_id}: {e}")
            return None

    def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Cancel a subscription immediately or at period end.

        Args:
            subscription_id: Stripe subscription ID (sub_xxx)
            at_period_end: If True, cancel at end of billing period (default: True)
                          If False, cancel immediately

        Returns:
            dict: Cancelled/updated Stripe subscription object
            None: If cancellation fails

        Example:
            # Cancel at period end (graceful)
            subscription = client.cancel_subscription(
                subscription_id="sub_xxx",
                at_period_end=True
            )

            # Cancel immediately
            subscription = client.cancel_subscription(
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
            else:
                # Cancel immediately
                subscription = stripe.Subscription.delete(subscription_id)
                logger.info(f"Cancelled subscription {subscription_id} immediately")

            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling subscription {subscription_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error cancelling subscription {subscription_id}: {e}")
            return None

    def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
        set_as_default: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Attach a payment method to a customer.

        Args:
            customer_id: Stripe customer ID (cus_xxx)
            payment_method_id: Stripe payment method ID (pm_xxx)
            set_as_default: Set as default payment method (default: True)

        Returns:
            dict: Stripe payment method object
            None: If attachment fails

        Example:
            payment_method = client.attach_payment_method(
                customer_id="cus_xxx",
                payment_method_id="pm_xxx",
                set_as_default=True
            )
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
            else:
                logger.info(
                    f"Attached payment method {payment_method_id} to customer {customer_id}"
                )

            return payment_method

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error attaching payment method: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error attaching payment method: {e}")
            return None

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verify Stripe webhook signature and parse event.

        Args:
            payload: Raw request body (bytes)
            signature: Stripe-Signature header value

        Returns:
            dict: Parsed Stripe event object
            None: If verification fails

        Example:
            event = client.verify_webhook_signature(
                payload=request.body(),
                signature=request.headers["Stripe-Signature"]
            )
            if event:
                print(f"Event type: {event['type']}")
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if not webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET not configured")
            return None

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            logger.info(f"Verified webhook event: {event['type']}")
            return event

        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying webhook: {e}")
            return None

    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a subscription by ID.

        Args:
            subscription_id: Stripe subscription ID (sub_xxx)

        Returns:
            dict: Stripe subscription object
            None: If retrieval fails

        Example:
            subscription = client.get_subscription("sub_xxx")
            print(f"Status: {subscription['status']}")
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving subscription {subscription_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving subscription {subscription_id}: {e}")
            return None

    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a customer by ID.

        Args:
            customer_id: Stripe customer ID (cus_xxx)

        Returns:
            dict: Stripe customer object
            None: If retrieval fails

        Example:
            customer = client.get_customer("cus_xxx")
            print(f"Email: {customer['email']}")
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving customer {customer_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving customer {customer_id}: {e}")
            return None
