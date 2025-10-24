"""Stripe API error handling utilities.

Provides user-friendly error messages for common Stripe API failures.
Handles different Stripe exception types and returns consistent error responses.

Example Usage:
    from api.utils.stripe_error_handler import handle_stripe_error

    try:
        stripe.Customer.create(email=email)
    except Exception as e:
        error_info = handle_stripe_error(e)
        return {
            "success": False,
            "message": error_info["user_message"],
            "error_code": error_info["error_code"]
        }
"""

from typing import Dict, Any
from api.logging_config import logger


def handle_stripe_error(error: Exception) -> Dict[str, Any]:
    """
    Handle Stripe API errors and return user-friendly messages.

    Catches all Stripe exception types and returns consistent error information
    with user-friendly messages for common failure scenarios.

    Args:
        error: Exception raised by Stripe API

    Returns:
        dict: Error information
        {
            "user_message": str,  # User-friendly error message
            "error_code": str,    # Stripe error code or "unknown"
            "error_type": str,    # Error category
            "technical_details": str  # Full error for logging
        }

    Example:
        >>> try:
        ...     stripe.Charge.create(amount=100)
        ... except Exception as e:
        ...     error_info = handle_stripe_error(e)
        ...     print(error_info["user_message"])
        "Your card was declined. Please use a different payment method."
    """
    try:
        import stripe
    except ImportError:
        return {
            "user_message": "Payment system is not configured. Please contact support.",
            "error_code": "stripe_not_installed",
            "error_type": "system_error",
            "technical_details": str(error)
        }

    # Default error response
    error_response = {
        "user_message": "An unexpected error occurred. Please try again or contact support.",
        "error_code": "unknown",
        "error_type": "unknown",
        "technical_details": str(error)
    }

    # Handle Stripe-specific errors
    if isinstance(error, stripe.error.CardError):
        # Card was declined
        error_response.update({
            "user_message": "Your card was declined. Please check your card details or use a different payment method.",
            "error_code": error.code if hasattr(error, 'code') else "card_declined",
            "error_type": "card_error"
        })

        # More specific card error messages
        if hasattr(error, 'code'):
            if error.code == 'insufficient_funds':
                error_response["user_message"] = "Your card has insufficient funds. Please use a different payment method."
            elif error.code == 'expired_card':
                error_response["user_message"] = "Your card has expired. Please update your payment information."
            elif error.code == 'incorrect_cvc':
                error_response["user_message"] = "The CVC code is incorrect. Please check and try again."
            elif error.code == 'incorrect_number':
                error_response["user_message"] = "The card number is incorrect. Please check and try again."
            elif error.code == 'card_not_supported':
                error_response["user_message"] = "This card type is not supported. Please use a different card."

        logger.warning(f"Stripe card error: {error.code if hasattr(error, 'code') else 'unknown'} - {str(error)}")

    elif isinstance(error, stripe.error.RateLimitError):
        # Too many requests
        error_response.update({
            "user_message": "Our payment system is busy. Please wait a moment and try again.",
            "error_code": "rate_limit",
            "error_type": "rate_limit_error"
        })
        logger.error(f"Stripe rate limit error: {str(error)}")

    elif isinstance(error, stripe.error.InvalidRequestError):
        # Invalid parameters
        error_response.update({
            "user_message": "There was a problem with your request. Please check your information and try again.",
            "error_code": "invalid_request",
            "error_type": "invalid_request_error"
        })
        logger.error(f"Stripe invalid request error: {str(error)}")

    elif isinstance(error, stripe.error.AuthenticationError):
        # API key issues
        error_response.update({
            "user_message": "Payment system authentication failed. Please contact support.",
            "error_code": "authentication_error",
            "error_type": "authentication_error"
        })
        logger.critical(f"Stripe authentication error - check API keys: {str(error)}")

    elif isinstance(error, stripe.error.APIConnectionError):
        # Network communication failed
        error_response.update({
            "user_message": "Unable to connect to payment system. Please check your internet connection and try again.",
            "error_code": "connection_error",
            "error_type": "api_connection_error"
        })
        logger.error(f"Stripe API connection error: {str(error)}")

    elif isinstance(error, stripe.error.StripeError):
        # Generic Stripe error
        error_response.update({
            "user_message": "Payment processing failed. Please try again or contact support.",
            "error_code": error.code if hasattr(error, 'code') else "stripe_error",
            "error_type": "stripe_error"
        })
        logger.error(f"Stripe error: {str(error)}")

    else:
        # Non-Stripe error
        logger.error(f"Unexpected error in Stripe operation: {str(error)}", exc_info=True)

    return error_response


def format_stripe_error_for_user(error: Exception) -> str:
    """
    Get user-friendly error message from Stripe exception.

    Convenience function that returns just the user message string.

    Args:
        error: Exception raised by Stripe API

    Returns:
        str: User-friendly error message

    Example:
        >>> try:
        ...     stripe.PaymentIntent.create(amount=0)
        ... except Exception as e:
        ...     message = format_stripe_error_for_user(e)
        "There was a problem with your request. Please check your information and try again."
    """
    error_info = handle_stripe_error(error)
    return error_info["user_message"]


def log_stripe_error(error: Exception, operation: str, context: Dict[str, Any] = None):
    """
    Log Stripe error with context for debugging.

    Args:
        error: Exception raised by Stripe API
        operation: Description of operation that failed (e.g., "create_customer")
        context: Additional context (org_id, user_id, etc.)

    Example:
        >>> try:
        ...     stripe.Customer.create(email=email)
        ... except Exception as e:
        ...     log_stripe_error(e, "create_customer", {"org_id": org.id})
    """
    error_info = handle_stripe_error(error)

    context_str = ""
    if context:
        context_str = " | Context: " + ", ".join(f"{k}={v}" for k, v in context.items())

    logger.error(
        f"Stripe operation failed: {operation} | "
        f"Error type: {error_info['error_type']} | "
        f"Error code: {error_info['error_code']} | "
        f"Message: {error_info['user_message']}"
        f"{context_str}",
        exc_info=True
    )


# Common error messages for specific operations
ERROR_MESSAGES = {
    "subscription_creation_failed": "Unable to create subscription. Please check your payment method and try again.",
    "payment_method_required": "A valid payment method is required to upgrade. Please add a payment method first.",
    "customer_not_found": "Customer account not found. Please contact support.",
    "subscription_not_found": "Subscription not found. It may have been cancelled or deleted.",
    "invoice_not_found": "Invoice not found. Please contact support if you believe this is an error.",
    "payment_method_invalid": "The payment method is invalid or expired. Please update your payment information.",
    "plan_not_found": "The selected plan is not available. Please refresh and try again.",
    "downgrade_not_allowed": "Downgrades are scheduled for the end of your billing period to maximize your benefits.",
    "trial_already_used": "Trial period has already been used for this organization.",
    "webhook_signature_invalid": "Webhook signature verification failed. This request may not be from Stripe.",
    "org_limit_exceeded": "You've reached your volunteer limit. Please upgrade to add more volunteers.",
    "payment_failed": "Payment failed. Please check your payment method and try again.",
    "subscription_cancelled": "This subscription has been cancelled. Please create a new subscription to continue.",
}


def get_error_message(error_key: str) -> str:
    """
    Get predefined error message by key.

    Args:
        error_key: Error message key from ERROR_MESSAGES dict

    Returns:
        str: User-friendly error message

    Example:
        >>> get_error_message("trial_already_used")
        "Trial period has already been used for this organization."
    """
    return ERROR_MESSAGES.get(
        error_key,
        "An error occurred. Please try again or contact support."
    )
