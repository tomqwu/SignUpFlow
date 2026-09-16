"""Build browser invitation links from the configured public app origin."""

from __future__ import annotations

import os


def manual_invitation_link(token: str) -> str:
    path = f"/auth/invitation/{token}"
    public_url = os.getenv("FRONTEND_URL") or os.getenv("APP_URL")
    return f"{public_url.rstrip('/')}{path}" if public_url else path
