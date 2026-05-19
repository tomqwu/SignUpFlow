"""Reusable e2e flow steps (signup, invite, seeding) — distilled from
the marathon's throwaway drivers so every committed flow shares one
hardened implementation."""

from __future__ import annotations

import sqlite3
import uuid


def rid() -> str:
    return uuid.uuid4().hex[:8]


def signup_admin(
    page, base_url, *, org="Hope Chapel", name="Admin Dana", email=None, password="HopePass123!"
):
    """Create an org + first admin via the signup form; lands on the
    admin dashboard. Returns the admin email."""
    email = email or f"admin+{rid()}@hope.e2e"
    page.goto(f"{base_url}/auth/signup")
    page.fill("#org_name", org)
    page.fill("#name", name)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type=submit]")
    page.wait_for_url("**/a/dashboard")
    return email


def invite_token(db_path, email):
    """Read the invitation token straight from the DB (email delivery is
    disabled in the sandbox)."""
    con = sqlite3.connect(db_path)
    try:
        row = con.execute(
            "SELECT token FROM invitations WHERE email=? ORDER BY created_at DESC LIMIT 1",
            (email,),
        ).fetchone()
        return row[0] if row else None
    finally:
        con.close()


def accept_invitation(context, base_url, token, *, password="VolPass123!"):
    """Accept an invite in a fresh (logged-out) page; lands authed."""
    pg = context.new_page()
    pg.goto(f"{base_url}/auth/invitation/{token}")
    pg.wait_for_selector("text=You're invited")
    pg.fill("#password", password)
    pg.click("button[type=submit]")
    pg.wait_for_url("**/v/schedule")
    return pg


def no_js_errors(page):
    """Assert the page accumulated no uncaught JS errors (regression
    guard for the CSP/Alpine-dead class of bug)."""
    assert not getattr(page, "test_errors", []), f"JS errors: {page.test_errors}"
