"""Domain browser acceptance: setup, availability, scheduling, and response.

The primary browser journey creates the organization, members, and full twelve-event
six-week plan through the UI before solving and publishing it. The per-role availability
test API-seeds its setup, then exercises every availability action through isolated
browser sessions.
"""

from collections import Counter
from datetime import datetime, timedelta

import httpx
import pytest
from playwright.sync_api import expect

from tests.e2e._helpers import invite_token, no_js_errors, signup_admin
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

    def invite_member(role, name):
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

    for role, count in playbook.spec["roles"].items():
        for index in range(count * 2):
            invite_member(role, f"{role} {index + 1}")

    critical_role = playbook.spec["critical_role"]
    invite_member(critical_role, f"{critical_role} replacement")
    assert len(playbook.people) == 15
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


def _create_event_in_browser(page, base, playbook, week, label, hour, day_offset):
    event_date = playbook.start + timedelta(weeks=week, days=day_offset)
    title = f"{playbook.spec['event']} W{week + 1} {label}"
    page.goto(f"{base}/a/events")
    page.get_by_role("button", name="New event", exact=True).click()
    page.fill("#ev_type", title)
    page.fill("#ev_date", event_date.isoformat())
    page.fill("#ev_start", f"{hour:02d}:00")
    page.fill("#ev_end", f"{hour + 2:02d}:00")
    for index, (role, count) in enumerate(playbook.spec["roles"].items()):
        if index:
            page.get_by_role("button", name="Add another role").click()
        page.locator("input[name=role_name]").nth(index).fill(role)
        page.locator("input[name=role_count]").nth(index).fill(str(count))
    _fits(page)
    page.get_by_role("button", name="Create event", exact=True).click()
    expect(page.locator("#events-list")).to_contain_text(title)

    events = playbook.request("GET", f"/events/?org_id={playbook.org}")["items"]
    created = next(event for event in events if event["type"] == title)
    assert created["extra_data"]["role_counts"] == playbook.spec["roles"]
    playbook.events[created["id"]] = created
    return created


@pytest.mark.parametrize("width", [360, 1440])
def test_every_domain_role_records_unavailability(
    live_server, new_context, tmp_path, playbook_spec, width
):
    base = live_server
    domain = playbook_spec.id
    with httpx.Client(base_url=base, timeout=30) as client:
        playbook = Playbook(client, playbook_spec)
        for week in range(6):
            playbook.event(week)
            playbook.event(
                week,
                playbook.spec["secondary_event"],
                hour=18,
                day_offset=3,
            )

        one_off = playbook.start + timedelta(days=3)
        unavailable_by_role = {}
        for role in playbook.spec["roles"]:
            person_id, person = next(
                (person_id, person)
                for person_id, person in playbook.people.items()
                if role in person["roles"]
            )
            unavailable_by_role[role] = person_id
            actor = new_context().new_page()
            actor.set_viewport_size({"width": width, "height": 900})
            _login(actor, base, person["email"], playbook.password, "/v/schedule")
            actor.goto(f"{base}/v/availability")
            actor.fill("#start_date", one_off.isoformat())
            actor.fill("#end_date", one_off.isoformat())
            actor.fill("#reason", f"{role} unavailable")
            actor.get_by_role("button", name="Add time-off").click()
            expect(actor.locator("#timeoff-list")).to_contain_text(f"{role} unavailable")
            actor.locator("#rrule-section").get_by_role("button", name="Every Sunday").click()
            expect(actor.locator("#rrule-section .mono-data")).to_have_text("FREQ=WEEKLY;BYDAY=SU")
            _fits(actor)
            actor.screenshot(
                path=str(tmp_path / f"{domain}-{width}-{role}-availability.png"),
                full_page=True,
            )
            no_js_errors(actor)
            playbook.blocked.add((person_id, one_off.isoformat()))

            target_headers = playbook.member_headers(person_id)
            peer_id, _ = next(
                (candidate_id, candidate)
                for candidate_id, candidate in playbook.people.items()
                if candidate_id != person_id and role in candidate["roles"]
            )
            peer_headers = playbook.member_headers(peer_id)
            timeoff_before = playbook.request(
                "GET", f"/availability/{person_id}/timeoff", headers=target_headers
            )
            rrule_before = playbook.request(
                "GET", f"/availability/{person_id}/rrule", headers=target_headers
            )
            rejected_date = (one_off + timedelta(days=1)).isoformat()
            playbook.request(
                "POST",
                f"/availability/{person_id}/timeoff",
                403,
                {
                    "start_date": rejected_date,
                    "end_date": rejected_date,
                    "reason": "Peer edit must fail",
                },
                headers=peer_headers,
            )
            playbook.request(
                "PUT",
                f"/availability/{person_id}/rrule",
                403,
                {"rrule": "FREQ=WEEKLY;BYDAY=MO"},
                headers=peer_headers,
            )
            assert (
                playbook.request(
                    "GET", f"/availability/{person_id}/timeoff", headers=target_headers
                )
                == timeoff_before
            )
            assert (
                playbook.request("GET", f"/availability/{person_id}/rrule", headers=target_headers)
                == rrule_before
            )

        solution = playbook.solve()
        assert solution["metrics"]["hard_violations"] == 0
        playbook.assert_complete(solution["solution_id"])
        assignments = playbook.assignments(solution["solution_id"])
        unavailable_ids = set(unavailable_by_role.values())
        for event in assignments:
            assigned_ids = {assignment["person_id"] for assignment in event["assignees"]}
            event_date = datetime.fromisoformat(event["event_start"]).date()
            if event_date.weekday() == 6:
                assert assigned_ids.isdisjoint(unavailable_ids)
            if event_date == one_off:
                assert assigned_ids.isdisjoint(unavailable_ids)


@pytest.mark.parametrize("width", [360, 1440])
def test_domain_browser_workflow(
    live_server, page, new_context, tmp_path, db_path, playbook_spec, width
):
    base = live_server
    domain = playbook_spec.id
    page.set_viewport_size({"width": width, "height": 900})
    with httpx.Client(base_url=base, timeout=30) as client:
        p = Playbook(client, playbook_spec, seed_people=False, bootstrap_admin=False)
        signup_admin(
            page,
            base,
            org=p.spec["name"],
            name="Scheduling administrator",
            email=p.email,
            password=p.password,
        )
        p.authenticate_admin()
        expect(page.get_by_role("link", name="Billing", exact=True)).to_have_count(0)
        organizations = p.request("GET", "/organizations/")["items"]
        assert [organization["id"] for organization in organizations] == [p.org]
        page.screenshot(path=str(tmp_path / f"{domain}-{width}-dashboard.png"), full_page=True)
        page.goto(f"{base}/a/onboarding")
        expect(page.locator("#onboarding-progress")).to_have_text("0 of 4 done")
        _fits(page)
        page.screenshot(path=str(tmp_path / f"{domain}-{width}-onboarding.png"), full_page=True)

        _onboard_qualified_members(page, new_context, base, db_path, p, width)
        page.screenshot(path=str(tmp_path / f"{domain}-{width}-qualified.png"), full_page=True)

        for week in range(6):
            _create_event_in_browser(page, base, p, week, "main", 10, 0)
            _create_event_in_browser(
                page,
                base,
                p,
                week,
                p.spec["secondary_event"],
                18,
                3,
            )
        events = p.request("GET", f"/events/?org_id={p.org}")["items"]
        assert len(events) == 12
        assert {event["id"] for event in events} == set(p.events)
        title = f"{p.spec['event']} W1 main"
        created = next(event for event in events if event["type"] == title)

        page.goto(f"{base}/a/solver")
        page.fill("#from_date", p.start.isoformat())
        page.fill("#to_date", (p.start + timedelta(weeks=6)).isoformat())
        page.get_by_role("button", name="Run solver").click()
        page.locator("#solver-result").get_by_role("link", name="Review solution").click()
        page.wait_for_url("**/a/solution/**")
        solution_id = int(page.url.rstrip("/").rsplit("/", 1)[1])
        p.assert_complete(solution_id)
        expect(page.locator(".kpi").filter(has_text="Assignments")).to_contain_text("84")
        expect(page.locator(".kpi").filter(has_text="Hard violations")).to_contain_text("0")
        assignments = p.assignments(solution_id)
        counts = Counter(
            assignment["person_id"] for event in assignments for assignment in event["assignees"]
        )
        for role in p.spec["roles"]:
            loads = [
                counts[person_id]
                for person_id, person in p.people.items()
                if role in person["roles"]
            ]
            assert max(loads) - min(loads) <= 1
        _fits(page)
        page.screenshot(
            path=str(tmp_path / f"{domain}-{width}-six-week-solution.png"),
            full_page=True,
        )

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
        member.screenshot(path=str(tmp_path / f"{domain}-{width}-unanswered.png"), full_page=True)
        member.get_by_role("link", name=title, exact=False).click()
        expect(member.locator("#assignment-card .status-text.pending")).to_contain_text(
            "Unanswered"
        )
        moved_start = datetime.fromisoformat(created["start_time"]) + timedelta(minutes=15)
        moved_end = datetime.fromisoformat(created["end_time"]) + timedelta(minutes=15)
        moved_event = {
            "start_time": moved_start.isoformat(),
            "end_time": moved_end.isoformat(),
        }
        p.request("PUT", f"/events/{created['id']}", data=moved_event)
        p.events[created["id"]].update(moved_event)
        member.get_by_role("button", name="Accept", exact=True).click()
        expect(member.locator("#assignment-card .alert-error")).to_contain_text(
            "Assignment changed from revision 1 to 2"
        )
        _fits(member)
        member.reload()
        member.get_by_role("button", name="Accept", exact=True).click()
        expect(member.locator("#assignment-card .status-text.accepted")).to_contain_text("Accepted")
        _fits(member)
        member.screenshot(path=str(tmp_path / f"{domain}-{width}-accepted.png"), full_page=True)
        member.context.clear_cookies()
        _login(member, base, person["email"], p.password, "/v/schedule")
        member.get_by_role("link", name=title, exact=False).click()
        expect(member.locator("#assignment-card .status-text.accepted")).to_contain_text("Accepted")
        page.goto(f"{base}/a/assignments?response=accepted")
        expect(page.locator(".status-text.accepted")).to_contain_text("Accepted")
        expect(page.locator(".scroll")).to_contain_text(person["name"])
        _fits(page)
        # A qualified reserve covers the actual published slot, preserving its role.
        role = first["assignees"][0]["role"]
        assigned_ids = {a["person_id"] for a in first["assignees"]}
        reserve = next(
            person
            for pid, person in p.people.items()
            if pid not in assigned_ids and role in person["roles"]
        )
        member.get_by_role("button", name="Request swap").click()
        expect(member.locator("#assignment-card .status-text.replacement_needed")).to_contain_text(
            "Replacement needed"
        )
        page.goto(f"{base}/a/assignments?response=replacement")
        expect(page.locator(".status-text.replacement_needed")).to_contain_text(
            "Replacement needed"
        )
        _fits(page)
        cover = new_context().new_page()
        cover.on("pageerror", lambda error: errors.append(str(error)))
        _login(cover, base, reserve["email"], p.password, "/v/schedule")
        cover.goto(f"{base}/v/swaps")
        expect(cover.locator("#swaps-open-list")).to_contain_text(title)
        cover.get_by_role("button", name="Cover this shift").click()
        expect(cover.locator("#swaps-open-list")).to_contain_text("No swap requests to cover")
        cover.goto(f"{base}/v/schedule")
        expect(cover.get_by_role("link", name=title)).to_have_count(1)
        cover.get_by_role("link", name=title).click()
        expect(cover.locator("#assignment-card .status-text.accepted")).to_contain_text("Accepted")
        _fits(cover)
        member.goto(f"{base}/v/schedule")
        expect(member.get_by_role("link", name=title)).to_have_count(0)
        p.assert_complete(solution_id)
        page.goto(f"{base}/a/onboarding")
        expect(page.locator("#onboarding-progress")).to_have_text("4 of 4 done")
        _fits(page)
        assert not errors
        no_js_errors(page)
