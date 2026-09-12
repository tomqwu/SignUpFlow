"""Domain browser acceptance: role forms, six weeks, publication and member response.

Only bulk people and five repeated weeks are seeded by API. The first event,
solve, review, publish and acceptance use the real browser with isolated actors.
"""

from datetime import timedelta

import httpx
import pytest
from playwright.sync_api import expect

from tests.e2e._helpers import no_js_errors
from tests.playbooks.runtime import Playbook

pytestmark = pytest.mark.e2e


def _login(page, base, email, password, landing):
    page.goto(f"{base}/auth/login")
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type=submit]")
    page.wait_for_url(f"**{landing}")


def _fits(page):
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize("width", [360, 1440])
def test_domain_browser_workflow(live_server, page, new_context, tmp_path, playbook_spec, width):
    base = live_server
    domain = playbook_spec.id
    page.set_viewport_size({"width": width, "height": 900})
    with httpx.Client(base_url=base, timeout=30) as client:
        p = Playbook(client, playbook_spec)
        for week in range(1, 6):
            p.event(week)
        _login(page, base, p.email, p.password, "/a/dashboard")
        page.goto(f"{base}/a/onboarding")
        _fits(page)
        page.screenshot(path=str(tmp_path / f"{domain}-{width}-onboarding.png"), full_page=True)

        title = f"{p.spec['event']} W1 main"
        page.goto(f"{base}/a/events")
        page.get_by_role("button", name="New event", exact=True).click()
        page.fill("#ev_type", title)
        page.fill("#ev_date", p.start.isoformat())
        page.fill("#ev_start", "10:00")
        page.fill("#ev_end", "12:00")
        for index, (role, count) in enumerate(p.spec["roles"].items()):
            if index:
                page.get_by_role("button", name="Add another role").click()
            page.locator("input[name=role_name]").nth(index).fill(role)
            page.locator("input[name=role_count]").nth(index).fill(str(count))
        _fits(page)
        page.get_by_role("button", name="Create event", exact=True).click()
        expect(page.locator("#events-list")).to_contain_text(title)
        events = p.request("GET", f"/events/?org_id={p.org}")["items"]
        created = next(event for event in events if event["type"] == title)
        assert created["extra_data"]["role_counts"] == p.spec["roles"]
        p.events[created["id"]] = created

        page.goto(f"{base}/a/solver")
        page.fill("#from_date", p.start.isoformat())
        page.fill("#to_date", (p.start + timedelta(weeks=6)).isoformat())
        page.get_by_role("button", name="Run solver").click()
        page.locator("#solver-result").get_by_role("link", name="Review solution").click()
        page.wait_for_url("**/a/solution/**")
        solution_id = int(page.url.rstrip("/").rsplit("/", 1)[1])
        p.assert_complete(solution_id)
        _fits(page)

        # The draft is invisible to its assignee until the administrator publishes.
        first = next(e for e in p.assignments(solution_id) if e["event_id"] == created["id"])
        person = p.people[first["assignees"][0]["person_id"]]
        member = new_context().new_page()
        member.set_viewport_size({"width": width, "height": 900})
        errors = []
        member.on("pageerror", lambda error: errors.append(str(error)))
        _login(member, base, person["email"], p.password, "/v/schedule")
        expect(member.get_by_role("link", name=title, exact=False)).to_have_count(0)
        page.get_by_role("button", name="Publish this solution").click()
        expect(page.locator("#publish-state")).to_contain_text("Unpublish")
        member.reload()
        member.get_by_role("link", name=title, exact=False).click()
        member.get_by_role("button", name="Accept", exact=True).click()
        expect(member.locator("#assignment-card .status-text.confirmed")).to_be_visible()
        _fits(member)
        member.screenshot(path=str(tmp_path / f"{domain}-{width}-accepted.png"), full_page=True)
        # A qualified reserve covers the actual published slot, preserving its role.
        role = first["assignees"][0]["role"]
        assigned_ids = {a["person_id"] for a in first["assignees"]}
        reserve = next(
            person
            for pid, person in p.people.items()
            if pid not in assigned_ids and role in person["roles"]
        )
        member.get_by_role("button", name="Request swap").click()
        expect(member.locator("#assignment-card .status-text.swap_requested")).to_be_visible()
        cover = new_context().new_page()
        cover.on("pageerror", lambda error: errors.append(str(error)))
        _login(cover, base, reserve["email"], p.password, "/v/schedule")
        cover.goto(f"{base}/v/swaps")
        expect(cover.locator("#swaps-open-list")).to_contain_text(title)
        cover.get_by_role("button", name="Cover this shift").click()
        expect(cover.locator("#swaps-open-list")).to_contain_text("No swap requests to cover")
        cover.goto(f"{base}/v/schedule")
        expect(cover.get_by_role("link", name=title)).to_have_count(1)
        member.goto(f"{base}/v/schedule")
        expect(member.get_by_role("link", name=title)).to_have_count(0)
        p.assert_complete(solution_id)
        page.goto(f"{base}/a/onboarding")
        expect(page.locator("#onboarding-progress")).to_have_text("4 of 4 done")
        _fits(page)
        assert not errors
        no_js_errors(page)
