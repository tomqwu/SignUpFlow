"""Time helper utilities.

Python 3.13 deprecates datetime.utcnow(); use timezone-aware now() instead.

We keep storing naive UTC datetimes in the DB for now (existing schema / code
assumes naive), so we generate an aware UTC timestamp then drop tzinfo.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime


def utcnow() -> datetime:
    """Return naive UTC datetime (tzinfo stripped) without using datetime.utcnow()."""
    if os.getenv("SIGNUPFLOW_ALLOW_TEST_CLOCK") == "true":
        value = os.getenv("SIGNUPFLOW_TEST_NOW")
        if value:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.astimezone(UTC).replace(tzinfo=None)
    return datetime.now(UTC).replace(tzinfo=None)
