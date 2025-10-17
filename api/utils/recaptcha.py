"""
reCAPTCHA v3 verification utility.

Provides server-side verification of reCAPTCHA v3 tokens with score-based bot detection.
"""

import os
import httpx
from typing import Optional, Tuple


RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

# Minimum score threshold (0.0 = bot, 1.0 = human)
# Google recommends 0.5 as default
# Lower threshold = more permissive (may allow some bots)
# Higher threshold = more restrictive (may block some humans)
DEFAULT_SCORE_THRESHOLD = float(os.getenv("RECAPTCHA_MIN_SCORE", "0.5"))


async def verify_recaptcha(
    token: str,
    remote_ip: Optional[str] = None,
    expected_action: Optional[str] = None,
    min_score: float = DEFAULT_SCORE_THRESHOLD
) -> Tuple[bool, float]:
    """
    Verify a reCAPTCHA v3 token with Google's API.

    Args:
        token: The reCAPTCHA response token from the client
        remote_ip: The user's IP address (optional but recommended)
        expected_action: The expected action name (e.g., 'login', 'signup')
        min_score: Minimum score threshold (0.0-1.0, default 0.5)

    Returns:
        Tuple of (is_valid, score)
        - is_valid: True if verification succeeds and score >= min_score
        - score: The score from 0.0 (bot) to 1.0 (human)

    Note:
        - Returns (True, 1.0) during testing mode (when TESTING=true)
        - Returns (False, 0.0) if RECAPTCHA_SECRET_KEY is not configured
    """
    # Skip verification during testing
    if os.getenv("TESTING") == "true":
        return (True, 1.0)

    secret_key = os.getenv("RECAPTCHA_SECRET_KEY")

    # If no secret key configured, fail closed (deny)
    if not secret_key:
        print("⚠️  WARNING: RECAPTCHA_SECRET_KEY not configured. Denying request.")
        return (False, 0.0)

    # If no token provided, deny
    if not token:
        return (False, 0.0)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RECAPTCHA_VERIFY_URL,
                data={
                    "secret": secret_key,
                    "response": token,
                    "remoteip": remote_ip or ""
                },
                timeout=5.0
            )

            if response.status_code != 200:
                print(f"⚠️  reCAPTCHA API error: HTTP {response.status_code}")
                return (False, 0.0)

            result = response.json()

            # Check if verification succeeded
            if not result.get("success"):
                error_codes = result.get("error-codes", [])
                print(f"⚠️  reCAPTCHA verification failed: {error_codes}")
                print(f"⚠️  Token (first 50 chars): {token[:50] if token else 'None'}")
                print(f"⚠️  Full response: {result}")
                return (False, 0.0)

            # Get score (v3 specific)
            score = result.get("score", 0.0)

            # Verify action matches (v3 specific)
            if expected_action:
                actual_action = result.get("action", "")
                if actual_action != expected_action:
                    print(f"⚠️  reCAPTCHA action mismatch: expected '{expected_action}', got '{actual_action}'")
                    return (False, score)

            # Check score threshold
            is_valid = score >= min_score

            if not is_valid:
                print(f"⚠️  reCAPTCHA score too low: {score} < {min_score}")

            return (is_valid, score)

    except httpx.TimeoutException:
        print("⚠️  reCAPTCHA verification timeout")
        # Fail open on timeout to avoid blocking legitimate users
        # In high-security scenarios, you might want to fail closed instead
        return (True, 0.5)

    except Exception as e:
        print(f"⚠️  reCAPTCHA verification error: {e}")
        # Fail open on unexpected errors
        return (True, 0.5)


def get_recaptcha_site_key() -> Optional[str]:
    """
    Get the reCAPTCHA site key for frontend use.

    Returns:
        The site key, or None if not configured
    """
    return os.getenv("RECAPTCHA_SITE_KEY")
