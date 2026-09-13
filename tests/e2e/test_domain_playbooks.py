"""Domain browser acceptance: role forms, six weeks, publication and member response.

Five repeated weeks are seeded by API. Member qualification, invitation acceptance,
the first event, solve, review, publish and response use real browser interactions.
"""

from datetime import timedelta

import httpx
import pytest
from playwright.sync_api import expect

from tests.e2e._helpers import invite_token, no_js_errors
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


def _onboard_qualified_members(page, new_context, base, db_path, playbook, width):
    page.goto(f"{base}/a/people")
    page.get_by_role("button", name="Invite person").click()
    invitee = new_context().new_page()
    invitee.set_viewport_size({"width": width, "height": 900})
    for role, count in playbook.spec["roles"].items():
        for index in range(count * 2):
            name = f"{role} {index + 1}"
            email = f"person{len(playbook.people)}@{playbook.org}.example"
            page.fill("#inv_name", name)
            page.fill("#inv_email", email)
            page.select_option("#inv_role", "volunteer")
            page.fill("#inv_qualifications", role)
            page.get_by_role("button", name="Send invite").click()
            expect(page.locator("#invite-result")).to_contain_text(f"Invitation sent to {email}")

            token = invite_token(db_path, email)
            assert token is not None
            invitee.context.clear_cookies()
            invitee.goto(f"{base}/auth/invitation/{token}")
            invitee.fill("#password", playbook.password)
            invitee.get_by_role("button", name="Accept & continue").click()
            invitee.wait_for_url("**/v/schedule")
            people = playbook.request("GET", f"/people/?org_id={playbook.org}&q={email}")["items"]
            assert len(people) == 1
            member = people[0]
            assert member["roles"] == ["volunteer", role]
            playbook.people[member["id"]] = {
                "name": name,
                "roles": [role],
                "email": email,
            }
    page.reload()
    first_id, first_member = next(iter(playbook.people.items()))
    qualifications_form = page.locator(f'form[action="/a/people/{first_id}/qualifications"]')
    qualifications_form.locator('input[name="qualifications"]').fill(first_member["roles"][0])
    qualifications_form.get_by_role("button", name="Save").click()
    expect(page.locator("#people-list")).to_contain_text(
        f"Qualifications saved for {first_member['name']}"
    )
    assert page.get_by_text("ADMIN", exact=True).count() == 1
    if width <= 480:
        assert (
            qualifications_form.evaluate("element => getComputedStyle(element).flexDirection")
            == "column"
        )
        qualification_box = qualifications_form.locator(
            'input[name="qualifications"]'
        ).bounding_box()
        assert qualification_box is not None and qualification_box["width"] >= 250
    _fits(page)


@pytest.mark.parametrize("width", [360, 1440])
def test_domain_browser_workflow(
    live_server, page, new_context, tmp_path, db_path, playbook_spec, width
):
    base = live_server
    domain = playbook_spec.id
    page.set_viewport_size({"width": width, "height": 900})
    with httpx.Client(base_url=base, timeout=30) as client:
        p = Playbook(client, playbook_spec, seed_people=False)
        for week in range(1, 6):
            p.event(week)
        _login(page, base, p.email, p.password, "/a/dashboard")
        page.goto(f"{base}/a/onboarding")
        _fits(page)
        page.screenshot(path=str(tmp_path / f"{domain}-{width}-onboarding.png"), full_page=True)

        _onboard_qualified_members(page, new_context, base, db_path, p, width)
        page.screenshot(path=str(tmp_path / f"{domain}-{width}-qualified.png"), full_page=True)

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
