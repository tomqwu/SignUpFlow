"""Time helper utilities.

Python 3.13 deprecates datetime.utcnow(); use timezone-aware now() instead.

We keep storing naive UTC datetimes in the DB for now (existing schema / code
assumes naive), so we generate an aware UTC timestamp then drop tzinfo.
"""

from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return naive UTC datetime (tzinfo stripped) without using datetime.utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
