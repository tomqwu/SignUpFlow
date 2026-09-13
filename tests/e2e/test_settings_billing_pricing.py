"""Overnight C5 — e2e backfill: CSV import, settings, billing, pricing, dark mode.

Regression guards for existing settings/admin/public surfaces.
"""

from __future__ import annotations

import pytest

from tests.e2e._helpers import no_js_errors, rid, signup_admin

pytestmark = pytest.mark.e2e


def test_csv_import(live_server, page):
    base = live_server
    signup_admin(page, base)
    page.goto(f"{base}/a/people")
    page.click("button:text-is('Import CSV')")
    page.fill("#csv_text", f"Casey Imp,casey+{rid()}@hope.e2e,volunteer")
    page.click("button:text-is('Import')")
    page.wait_for_selector("#import-result:has-text('Imported 1')")
    no_js_errors(page)


def test_org_settings_save(live_server, page):
    base = live_server
    signup_admin(page, base)
    page.goto(f"{base}/a/settings")
    page.wait_for_selector(".page-title:has-text('Settings')")
    page.fill("#org_name", "Hope Chapel Renamed")
    page.click("#settings-form button:has-text('Save settings')")
    page.wait_for_selector("#settings-form:has-text('Settings saved.')")
    no_js_errors(page)


def test_password_change(live_server, page):
    base = live_server
    signup_admin(page, base)
    page.goto(f"{base}/a/settings")
    page.wait_for_selector("#password-form")
    page.fill("#pw_current", "HopePass123!")
    page.fill("#pw_new", "NewHopePass456!")
    page.fill("#pw_confirm", "NewHopePass456!")
    page.click("#password-form button:has-text('Change password')")
    page.wait_for_selector("#password-form .form-notice[role='status']")
    no_js_errors(page)


def test_commercial_surfaces_are_disabled(live_server, page):
    base = live_server
    signup_admin(page, base)
    page.goto(f"{base}/a/dashboard")
    assert page.locator('a[href="/a/billing"]').count() == 0

    billing = page.goto(f"{base}/a/billing")
    assert billing is not None and billing.status == 404
    pricing = page.goto(f"{base}/pricing")
    assert pricing is not None and pricing.status == 404
    no_js_errors(page)


def test_dark_mode_toggle_persists(live_server, page):
    base = live_server
    signup_admin(page, base)
    page.goto(f"{base}/v/profile")
    page.wait_for_selector("text=Appearance")

    page.click("button:has-text('Dark')")
    assert page.evaluate("document.documentElement.getAttribute('data-theme')") == "dark"

    page.reload()  # persisted via localStorage → no-flash script re-applies
    assert page.evaluate("document.documentElement.getAttribute('data-theme')") == "dark"

    page.click("button:has-text('Light')")
    assert page.evaluate("document.documentElement.getAttribute('data-theme')") == "light"
    no_js_errors(page)
