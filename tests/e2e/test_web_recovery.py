"""Browser-level usability and recovery contracts for every HTMX surface."""

from __future__ import annotations

import sqlite3

import pytest
from playwright.sync_api import expect

from tests.e2e._helpers import next_sunday_iso, no_js_errors, rid, signup_admin
from web.deps import SESSION_COOKIE

pytestmark = pytest.mark.e2e


def _open_import(page, base):
    page.goto(f"{base}/a/people")
    page.get_by_role("button", name="Import CSV").click()
    expect(page.locator("#csv_text")).to_be_visible()


def _create_solution(page, base):
    event_date = next_sunday_iso()
    page.goto(f"{base}/a/people")
    qualification = page.locator("form.qualification-form").first
    qualification.locator('input[name="qualifications"]').fill("reconnect_role")
    qualification.get_by_role("button", name="Save").click()
    expect(page.locator("#people-list")).to_contain_text("Qualifications saved")

    page.goto(f"{base}/a/events")
    page.get_by_role("button", name="New event").click()
    page.fill("#ev_type", "Reconnect rehearsal")
    page.fill("#ev_date", event_date)
    page.fill("#ev_start", "10:00")
    page.fill("#ev_end", "11:00")
    page.fill('input[name="role_name"]', "reconnect_role")
    page.fill('input[name="role_count"]', "1")
    page.get_by_role("button", name="Create event").click()
    expect(page.locator("#events-list")).to_contain_text("Reconnect rehearsal")

    page.goto(f"{base}/a/solver")
    page.fill("#from_date", event_date)
    page.fill("#to_date", event_date)
    page.get_by_role("button", name="Run solver").click()
    page.get_by_role("link", name="Review solution").click()
    page.wait_for_url("**/a/solution/**")
    expect(page.locator("#solution-assignments")).to_contain_text("Admin Dana")
    return int(page.url.rstrip("/").rsplit("/", 1)[1])


def test_invalid_htmx_submission_preserves_input_and_shows_error(live_server, page):
    signup_admin(page, live_server)
    _open_import(page, live_server)
    safe_input = "name,email,roles"
    page.fill("#csv_text", safe_input)
    page.get_by_role("button", name="Import", exact=True).click()

    expect(page.locator("#import-result [role=alert]")).to_contain_text("No data rows found")
    assert page.input_value("#csv_text") == safe_input
    assert page.locator("#import-result [role=status]").count() == 0
    no_js_errors(page)


def test_network_failure_is_retryable_without_losing_input(live_server, page):
    signup_admin(page, live_server)
    _open_import(page, live_server)
    csv_text = f"Network Retry,network-{rid()}@example.com,volunteer"
    page.fill("#csv_text", csv_text)
    failed = False

    def fail_once(route):
        nonlocal failed
        if not failed:
            failed = True
            route.abort()
        else:
            route.continue_()

    page.route("**/a/people/import", fail_once)
    page.get_by_role("button", name="Import", exact=True).click()
    expect(page.locator("#request-status")).to_contain_text("Check your connection")
    assert page.input_value("#csv_text") == csv_text

    page.get_by_role("button", name="Import", exact=True).click()
    expect(page.locator("#import-result [role=status]")).to_contain_text("Imported 1")
    expect(page.locator("#request-status")).to_be_hidden()
    no_js_errors(page)


def test_rapid_duplicate_submission_sends_one_request(live_server, page):
    signup_admin(page, live_server)
    _open_import(page, live_server)
    email = f"one-request-{rid()}@example.com"
    page.fill("#csv_text", f"One Request,{email},volunteer")
    requests = []
    page.on(
        "request",
        lambda request: requests.append(request)
        if request.method == "POST" and request.url.endswith("/a/people/import")
        else None,
    )

    page.locator("button", has_text="Import").last.evaluate(
        "button => { button.click(); button.click(); }"
    )
    expect(page.locator("#import-result [role=status]")).to_contain_text("Imported 1")
    assert len(requests) == 1
    no_js_errors(page)


def test_long_labels_remain_separate_and_keyboard_reachable(live_server, page):
    signup_admin(page, live_server)
    _open_import(page, live_server)
    long_name = "Alexandria Montgomery-Worthington Community Coordinator"
    long_role = "weekend_hospitality_accessibility_coordinator"
    page.fill("#csv_text", f"{long_name},long-{rid()}@example.com,{long_role}")
    page.get_by_role("button", name="Import", exact=True).click()
    expect(page.locator("#import-result [role=status]")).to_contain_text("Imported 1")
    page.reload()
    page.set_viewport_size({"width": 360, "height": 800})

    row = page.locator("#people-list .row", has_text=long_name).first
    title = row.locator(".row-main")
    metadata = row.locator(".person-meta")
    expect(title).to_be_visible()
    expect(metadata).to_contain_text(long_role)
    title_box = title.bounding_box()
    metadata_box = metadata.bounding_box()
    assert title_box is not None and metadata_box is not None
    assert title_box["x"] + title_box["width"] <= metadata_box["x"] + 1

    page.evaluate("document.documentElement.style.zoom = '150%'")
    expect(row).to_be_visible()
    assert row.evaluate("element => element.scrollWidth <= element.clientWidth")

    search = page.locator("#q")
    search.focus()
    page.keyboard.press("Tab")
    assert page.locator(":focus").get_attribute("name") == "qualifications"
    page.keyboard.press("Tab")
    assert page.locator(":focus").inner_text().casefold() == "save"
    no_js_errors(page)


def test_expired_session_navigates_instead_of_swapping_login_fragment(live_server, page):
    signup_admin(page, live_server)
    _open_import(page, live_server)
    page.fill("#csv_text", "Expired Session,expired@example.com,volunteer")
    page.context.clear_cookies(name=SESSION_COOKIE)
    page.get_by_role("button", name="Import", exact=True).click()

    page.wait_for_url("**/auth/login")
    expect(page.locator("#email")).to_be_visible()
    assert page.locator("#import-result").count() == 0
    no_js_errors(page)


def test_sse_reconnect_refetches_authoritative_solution_state(live_server, page, db_path):
    signup_admin(page, live_server)
    solution_id = _create_solution(page, live_server)

    with sqlite3.connect(db_path) as connection:
        person_id = connection.execute(
            "SELECT person_id FROM assignments WHERE solution_id = ? LIMIT 1", (solution_id,)
        ).fetchone()[0]
        connection.execute(
            "UPDATE people SET name = ? WHERE id = ?", ("Recovered Authoritative Name", person_id)
        )
        connection.commit()

    page.evaluate(
        """() => {
          const root = document.querySelector('[sse-connect]')
          const source = root['htmx-internal-data'].sseEventSource
          source.close()
          source.onerror(new Event('error'))
        }"""
    )

    expect(page.locator("#solution-assignments")).to_contain_text(
        "Recovered Authoritative Name", timeout=7000
    )
    no_js_errors(page)
