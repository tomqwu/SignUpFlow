"""Domain browser acceptance: setup, availability, scheduling, change, and response.

The primary browser journey creates the organization, members, and full twelve-event
six-week plan through the UI before solving and publishing it. Focused availability and
rolling-horizon tests API-seed their preconditions, then exercise each claimed operation
through isolated browser sessions.
"""

import re
from collections import Counter
from datetime import UTC, date, datetime, timedelta

import httpx
import pytest
from icalendar import Calendar
from playwright.sync_api import expect

from tests.e2e._helpers import invite_token, no_js_errors, signup_admin
from tests.playbooks.registry import BUILTIN_DIRECTORY, discover_playbooks
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


def _utc_datetime(value):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _solve_in_browser(page, base, start_date, end_date, *, change_min=False):
    page.goto(f"{base}/a/solver")
    page.fill("#from_date", start_date.isoformat())
    page.fill("#to_date", end_date.isoformat())
    if change_min:
        page.check('input[name="change_min"]')
    page.get_by_role("button", name="Run solver").click()
    page.locator("#solver-result").get_by_role("link", name="Review solution").click()
    page.wait_for_url("**/a/solution/**")
    return int(page.url.rstrip("/").rsplit("/", 1)[1])


def _solve_and_publish_in_browser(page, base, start_date, end_date):
    solution_id = _solve_in_browser(page, base, start_date, end_date)
    page.get_by_role("button", name="Publish this solution").click()
    expect(page.locator("#publish-state")).to_contain_text("Unpublish")
    page.wait_for_selector("#publish-state:not(.htmx-added)")
    return solution_id


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
        expect(page.locator("#invite-result")).to_contain_text(f"Invitation created for {email}")

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
    expected_people = sum(count * 2 for count in playbook.spec["roles"].values()) + 1
    assert len(playbook.people) == expected_people
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


def _create_event_in_browser(page, base, playbook, week, label, hour, day_offset, roles=None):
    event_date = playbook.start + timedelta(weeks=week, days=day_offset)
    title = f"{playbook.spec['event']} W{week + 1} {label}"
    page.goto(f"{base}/a/events")
    page.get_by_role("button", name="New event", exact=True).click()
    page.fill("#ev_type", title)
    page.fill("#ev_date", event_date.isoformat())
    page.fill("#ev_start", f"{hour:02d}:00")
    page.fill("#ev_end", f"{hour + 2:02d}:00")
    role_counts = roles or playbook.spec["roles"]
    for index, (role, count) in enumerate(role_counts.items()):
        if index:
            page.get_by_role("button", name="Add another role").click()
        page.locator("input[name=role_name]").nth(index).fill(role)
        page.locator("input[name=role_count]").nth(index).fill(str(count))
    _fits(page)
    page.get_by_role("button", name="Create event", exact=True).click()
    expect(page.locator("#events-list")).to_contain_text(title)

    events = playbook.request("GET", f"/events/?org_id={playbook.org}")["items"]
    created = next(event for event in events if event["type"] == title)
    assert created["extra_data"]["role_counts"] == role_counts
    playbook.events[created["id"]] = created
    return created


def _edit_event_in_browser(page, base, playbook, event_id, start, end):
    page.goto(f"{base}/a/events")
    row = page.locator(f'.event-row[data-event-id="{event_id}"]')
    row.get_by_role("button", name="Edit", exact=False).click()
    form = page.locator(f'form.event-edit-form[data-event-id="{event_id}"]')
    expect(form).to_be_visible()
    form.locator('input[name="event_date"]').fill(start.date().isoformat())
    form.locator('input[name="start_time"]').fill(start.strftime("%H:%M"))
    form.locator('input[name="end_time"]').fill(end.strftime("%H:%M"))
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and response.url.endswith(f"/a/events/{event_id}/update")
    ) as response_info:
        form.get_by_role("button", name="Save change").click()
    assert response_info.value.ok
    expect(form).to_be_hidden()
    expect(page.locator("#events-list .form-error")).to_have_count(0)
    updated = playbook.request("GET", f"/events/{event_id}")
    if event_id in playbook.events:
        playbook.events[event_id].update(updated)
    return updated


def _assignment_map(playbook, solution_id):
    return {
        (entry["event_id"], assignee["role"]): assignee["person_id"]
        for entry in playbook.assignments(solution_id)
        for assignee in entry["assignees"]
    }


def _compare_in_browser(page, base, prior_id, candidate_id):
    page.goto(f"{base}/a/compare")
    page.select_option("#solution_a", str(prior_id))
    page.select_option("#solution_b", str(candidate_id))
    page.get_by_role("button", name="Compare", exact=True).click()
    result = page.locator("#compare-result")
    expect(result).to_contain_text(f"#{prior_id} → #{candidate_id}")
    return result


def _calendar_feed_url(member, base):
    member.goto(f"{base}/v/profile")
    match = re.search(r"/api/v1/calendar/feed/([A-Za-z0-9_\-]+)", member.content())
    assert match is not None
    return f"{base}/api/v1/calendar/feed/{match.group(1)}"


def _calendar_event(member, feed_url, title):
    response = member.request.get(feed_url)
    assert response.status == 200
    events = Calendar.from_ical(response.body()).walk("VEVENT")
    return next(event for event in events if str(event["SUMMARY"]).startswith(title))


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
def test_domain_late_withdrawals_require_exact_available_cover(
    live_server, page, new_context, tmp_path, playbook_spec, width
):
    """Exercise CH-D01 and BB-D02 from roles declared by each plugin fixture."""
    if not playbook_spec.late_cover_roles:
        pytest.skip("playbook does not configure late-cover roles")

    base = live_server
    page.set_viewport_size({"width": width, "height": 900})
    with httpx.Client(base_url=base, timeout=30) as client:
        playbook = Playbook(client, playbook_spec)
        event_ids = [
            playbook.event(index, f"{role}-late-cover")
            for index, role in enumerate(playbook_spec.late_cover_roles)
        ]
        solution = playbook.solve()
        solution_id = solution["solution_id"]
        playbook.assert_complete(solution_id)
        playbook.request("POST", f"/solutions/{solution_id}/publish")

        wrong_role = next(
            (role for role in playbook.spec["roles"] if role not in playbook_spec.late_cover_roles),
            "unrelated_qualification",
        )
        wrong_id = playbook.invite("Wrong-role reserve", [wrong_role])
        wrong = playbook.people[wrong_id]
        wrong_page = new_context().new_page()
        wrong_page.set_viewport_size({"width": width, "height": 900})
        _login(wrong_page, base, wrong["email"], playbook.password, "/v/schedule")

        _login(page, base, playbook.email, playbook.password, "/a/dashboard")
        for event_id, role in zip(event_ids, playbook_spec.late_cover_roles, strict=True):
            title = playbook.events[event_id]["type"]
            before = next(
                entry
                for entry in playbook.assignments(solution_id)
                if entry["event_id"] == event_id
            )["assignees"]
            assigned_ids = {assignment["person_id"] for assignment in before}
            original_assignment = next(
                assignment for assignment in before if assignment["role"] == role
            )
            original_id = original_assignment["person_id"]
            unavailable_id = next(
                person_id
                for person_id, person in playbook.people.items()
                if person_id not in assigned_ids and role in person["roles"]
            )
            event_date = datetime.fromisoformat(playbook.events[event_id]["start_time"]).date()
            playbook.request(
                "POST",
                f"/availability/{unavailable_id}/timeoff",
                201,
                {
                    "start_date": event_date.isoformat(),
                    "end_date": event_date.isoformat(),
                    "reason": f"Unavailable {role} reserve",
                },
            )
            playbook.blocked.add((unavailable_id, event_date.isoformat()))
            available_id = playbook.invite(f"Available {role} reserve", [role])

            original = playbook.people[original_id]
            original_page = new_context().new_page()
            original_page.set_viewport_size({"width": width, "height": 900})
            _login(original_page, base, original["email"], playbook.password, "/v/schedule")
            original_page.get_by_role("link", name=title, exact=False).click()
            original_page.get_by_role("button", name="Request swap").click()
            expect(
                original_page.locator("#assignment-card .status-text.replacement_needed")
            ).to_contain_text("Replacement needed")

            page.goto(f"{base}/a/swaps")
            expect(page.locator("#swaps-list")).to_contain_text(title)
            expect(page.locator("#swaps-list")).to_contain_text(role)
            _fits(page)
            page.screenshot(
                path=str(tmp_path / f"{playbook_spec.id}-{width}-{role}-late-gap.png"),
                full_page=True,
            )

            wrong_page.goto(f"{base}/v/swaps")
            expect(wrong_page.locator("#swaps-open-list")).not_to_contain_text(title)
            unavailable = playbook.people[unavailable_id]
            unavailable_page = new_context().new_page()
            unavailable_page.set_viewport_size({"width": width, "height": 900})
            _login(
                unavailable_page,
                base,
                unavailable["email"],
                playbook.password,
                "/v/schedule",
            )
            unavailable_page.goto(f"{base}/v/swaps")
            expect(unavailable_page.locator("#swaps-open-list")).not_to_contain_text(title)

            available = playbook.people[available_id]
            cover_page = new_context().new_page()
            cover_page.set_viewport_size({"width": width, "height": 900})
            _login(cover_page, base, available["email"], playbook.password, "/v/schedule")
            cover_page.goto(f"{base}/v/swaps")
            expect(cover_page.locator("#swaps-open-list")).to_contain_text(title)
            expect(cover_page.locator("#swaps-open-list")).to_contain_text(role)
            cover_page.get_by_role("button", name="Cover this shift").click()
            expect(cover_page.locator("#swaps-open-list")).not_to_contain_text(title)
            cover_page.goto(f"{base}/v/schedule")
            expect(cover_page.get_by_role("link", name=title, exact=False)).to_have_count(1)

            after = next(
                entry
                for entry in playbook.assignments(solution_id)
                if entry["event_id"] == event_id
            )["assignees"]
            assert Counter(
                (assignment["person_id"], assignment["role"])
                for assignment in after
                if assignment["role"] != role
            ) == Counter(
                (assignment["person_id"], assignment["role"])
                for assignment in before
                if assignment["role"] != role
            )
            replacement = next(assignment for assignment in after if assignment["role"] == role)
            assert replacement["person_id"] == available_id
            assert replacement["person_id"] != original_id
            playbook.assert_complete(solution_id)
            no_js_errors(original_page)
            no_js_errors(unavailable_page)
            no_js_errors(cover_page)

        no_js_errors(wrong_page)
        no_js_errors(page)


@pytest.mark.parametrize("width", [360, 1440])
def test_domain_eligibility_and_extended_availability_changes(
    live_server, page, tmp_path, playbook_spec, width
):
    """Exercise CH-D02 or BB-D01 from the extension declared by each fixture."""
    if (
        playbook_spec.qualification_review_role is None
        and playbook_spec.extended_absence_role is None
    ):
        pytest.skip("playbook does not configure an eligibility or absence extension")

    base = live_server
    page.set_viewport_size({"width": width, "height": 900})
    with httpx.Client(base_url=base, timeout=30) as client:
        playbook = Playbook(client, playbook_spec)

        if playbook_spec.qualification_review_role is not None:
            role = playbook_spec.qualification_review_role
            event_id = playbook.event(0, "qualification-review", roles={role: 1})
            solution = playbook.solve()
            playbook.assert_complete(solution["solution_id"])
            playbook.request("POST", f"/solutions/{solution['solution_id']}/publish")
            assigned = playbook.assignments(solution["solution_id"])[0]["assignees"][0]
            member_id = assigned["person_id"]
            member_name = playbook.people[member_id]["name"]

            _login(page, base, playbook.email, playbook.password, "/a/dashboard")
            page.goto(f"{base}/a/people")
            form = page.locator(f'form[action="/a/people/{member_id}/qualifications"]')
            form.locator('input[name="qualifications"]').fill("")
            form.get_by_role("button", name="Save").click()
            expect(page.locator("#people-list")).to_contain_text(
                f"Qualifications saved for {member_name}. 1 future assignment reopened."
            )

            page.goto(f"{base}/a/events/{event_id}/assignments")
            coverage = page.locator(f'.cov-row[data-role="{role}"]')
            expect(coverage).to_have_attribute("data-gap", "1")
            expect(coverage).to_contain_text("1 needed")
            _fits(page)
            page.screenshot(
                path=str(tmp_path / f"{playbook_spec.id}-{width}-qualification-gap.png"),
                full_page=True,
            )
        else:
            role = playbook_spec.extended_absence_role
            assert role is not None
            event_ids = [
                playbook.event(week, "injury-availability", roles={role: 1}) for week in range(4)
            ]
            qualified_ids = [
                person_id
                for person_id, person in playbook.people.items()
                if role in person["roles"]
            ]
            assert len(qualified_ids) == 2
            player_id, reserve_id = qualified_ids
            player = playbook.people[player_id]

            for week in (0, 3):
                playbook.timeoff(reserve_id, week)

            _login(page, base, player["email"], playbook.password, "/v/schedule")
            page.goto(f"{base}/v/availability")
            absence_start = playbook.start + timedelta(weeks=1)
            absence_end = playbook.start + timedelta(weeks=2)
            page.fill("#start_date", absence_start.isoformat())
            page.fill("#end_date", absence_end.isoformat())
            page.fill("#reason", "Recorded injury absence")
            page.get_by_role("button", name="Add time-off").click()
            expect(page.locator("#timeoff-list")).to_contain_text("Recorded injury absence")
            for week in (1, 2):
                playbook.blocked.add(
                    (player_id, (playbook.start + timedelta(weeks=week)).isoformat())
                )

            absent_solution = playbook.solve()
            playbook.assert_complete(absent_solution["solution_id"])
            absent_assignments = {
                entry["event_id"]: entry["assignees"][0]["person_id"]
                for entry in playbook.assignments(absent_solution["solution_id"])
            }
            assert absent_assignments[event_ids[0]] == player_id
            assert absent_assignments[event_ids[1]] == reserve_id
            assert absent_assignments[event_ids[2]] == reserve_id
            assert absent_assignments[event_ids[3]] == player_id

            page.once("dialog", lambda dialog: dialog.accept())
            page.get_by_role("button", name="Remove").click()
            expect(page.locator("#timeoff-list")).to_contain_text("No time-off booked")
            for week in (1, 2):
                playbook.blocked.discard(
                    (player_id, (playbook.start + timedelta(weeks=week)).isoformat())
                )
            playbook.timeoff(reserve_id, 1)

            return_solution = playbook.solve()
            playbook.assert_complete(return_solution["solution_id"])
            returned = next(
                entry
                for entry in playbook.assignments(return_solution["solution_id"])
                if entry["event_id"] == event_ids[1]
            )
            assert returned["assignees"][0]["person_id"] == player_id
            _fits(page)
            page.screenshot(
                path=str(tmp_path / f"{playbook_spec.id}-{width}-availability-return.png"),
                full_page=True,
            )

        no_js_errors(page)


@pytest.mark.parametrize("width", [360, 1440])
def test_domain_requirement_and_postponement_changes(
    live_server, new_context, page, tmp_path, playbook_spec, width
):
    """Exercise CH-D03 or BB-D03 from the change declared by each fixture."""
    if playbook_spec.additional_event_role is None and playbook_spec.postponed_event_role is None:
        pytest.skip("playbook does not configure an additional-event or postponement extension")

    base = live_server
    page.set_viewport_size({"width": width, "height": 900})
    with httpx.Client(base_url=base, timeout=30) as client:
        playbook = Playbook(client, playbook_spec)
        role = playbook_spec.additional_event_role or playbook_spec.postponed_event_role
        assert role is not None
        event_ids = [playbook.event(week, "change", roles={role: 1}) for week in range(3)]
        unchanged_times = {
            event_id: (
                _utc_datetime(playbook.events[event_id]["start_time"]),
                _utc_datetime(playbook.events[event_id]["end_time"]),
            )
            for event_id in (event_ids[0], event_ids[2])
        }
        prior = playbook.solve()
        prior_id = prior["solution_id"]
        playbook.assert_complete(prior_id)
        playbook.request("POST", f"/solutions/{prior_id}/publish")
        prior_assignments = _assignment_map(playbook, prior_id)
        target_id = event_ids[1]
        target_title = playbook.events[target_id]["type"]
        target_person_id = prior_assignments[(target_id, role)]
        target_person = playbook.people[target_person_id]

        _login(page, base, playbook.email, playbook.password, "/a/dashboard")
        member = new_context().new_page()
        member.set_viewport_size({"width": width, "height": 900})
        _login(member, base, target_person["email"], playbook.password, "/v/schedule")
        member.get_by_role("link", name=target_title, exact=False).click()
        member.get_by_role("button", name="Accept", exact=True).click()
        expect(member.locator("#assignment-card .status-text.accepted")).to_contain_text("Accepted")

        if playbook_spec.additional_event_role is not None:
            added = _create_event_in_browser(
                page,
                base,
                playbook,
                1,
                "holiday-extra",
                14,
                1,
                roles={role: 1},
            )
            candidate_id = _solve_in_browser(
                page,
                base,
                playbook.start,
                playbook.start + timedelta(weeks=3),
                change_min=True,
            )
            playbook.assert_complete(candidate_id)
            candidate_assignments = _assignment_map(playbook, candidate_id)
            assert set(prior_assignments.items()) <= set(candidate_assignments.items())
            assert (added["id"], role) in candidate_assignments

            comparison = _compare_in_browser(page, base, prior_id, candidate_id)
            expect(comparison.locator(".kpi", has_text="Added").locator(".kpi-value")).to_have_text(
                "1"
            )
            expect(
                comparison.locator(".kpi", has_text="Removed").locator(".kpi-value")
            ).to_have_text("0")
            expect(
                comparison.locator(".kpi", has_text="Unchanged").locator(".kpi-value")
            ).to_have_text("3")

            page.goto(f"{base}/a/solution/{candidate_id}")
            page.get_by_role("button", name="Publish this solution").click()
            expect(page.locator("#publish-state")).to_contain_text("Unpublish")
            page.wait_for_selector("#publish-state:not(.htmx-added)")
            page.get_by_role("button", name="Notify assignees").click()
            expect(page.locator("#notify-result")).to_contain_text("Reminder added")

            member.goto(f"{base}/v/schedule")
            member.get_by_role("link", name=target_title, exact=False).click()
            expect(member.locator("#assignment-card .status-text.accepted")).to_contain_text(
                "Accepted"
            )

            added_person_id = candidate_assignments[(added["id"], role)]
            added_person = playbook.people[added_person_id]
            added_member = new_context().new_page()
            added_member.set_viewport_size({"width": width, "height": 900})
            _login(added_member, base, added_person["email"], playbook.password, "/v/schedule")
            added_member.goto(f"{base}/v/inbox")
            expect(added_member.locator("#inbox-list")).to_contain_text("New assignment")
            expect(added_member.locator("#inbox-list")).to_contain_text("Reminder")
            added_member.goto(f"{base}/v/schedule")
            added_member.get_by_role("link", name=added["type"], exact=False).click()
            expect(added_member.locator("#assignment-card .status-text.pending")).to_contain_text(
                "Unanswered"
            )
            added_member.get_by_role("button", name="Accept", exact=True).click()
            expect(added_member.locator("#assignment-card .status-text.accepted")).to_contain_text(
                "Accepted"
            )
            _fits(added_member)
            no_js_errors(added_member)
        else:
            feed_url = _calendar_feed_url(member, base)
            published_event = _calendar_event(member, feed_url, target_title)
            published_uid = str(published_event["UID"])
            published_start = published_event.decoded("DTSTART")
            target_start = _utc_datetime(playbook.events[target_id]["start_time"])
            target_end = _utc_datetime(playbook.events[target_id]["end_time"])
            moved = _edit_event_in_browser(
                page,
                base,
                playbook,
                target_id,
                target_start + timedelta(days=1, hours=1),
                target_end + timedelta(days=1, hours=1),
            )
            assert _utc_datetime(moved["start_time"]) == target_start + timedelta(days=1, hours=1)

            member.goto(f"{base}/v/inbox")
            expect(member.locator("#inbox-list")).to_contain_text("Schedule update")
            member.goto(f"{base}/v/schedule")
            member.get_by_role("link", name=target_title, exact=False).click()
            expect(member.locator("#assignment-card .status-text.pending")).to_contain_text(
                "Unanswered"
            )

            candidate_id = _solve_in_browser(
                page,
                base,
                playbook.start,
                playbook.start + timedelta(weeks=3, days=2),
                change_min=True,
            )
            playbook.assert_complete(candidate_id)
            candidate_assignments = _assignment_map(playbook, candidate_id)
            assert candidate_assignments == prior_assignments
            comparison = _compare_in_browser(page, base, prior_id, candidate_id)
            expect(comparison.locator(".kpi", has_text="Added").locator(".kpi-value")).to_have_text(
                "0"
            )
            expect(
                comparison.locator(".kpi", has_text="Removed").locator(".kpi-value")
            ).to_have_text("0")
            expect(
                comparison.locator(".kpi", has_text="Unchanged").locator(".kpi-value")
            ).to_have_text("3")

            page.goto(f"{base}/a/solution/{candidate_id}")
            page.get_by_role("button", name="Publish this solution").click()
            expect(page.locator("#publish-state")).to_contain_text("Unpublish")
            page.wait_for_selector("#publish-state:not(.htmx-added)")
            page.get_by_role("button", name="Notify assignees").click()
            expect(page.locator("#notify-result")).to_contain_text("Reminder added")

            moved_event = _calendar_event(member, feed_url, target_title)
            assert str(moved_event["UID"]) == published_uid
            assert moved_event.decoded("DTSTART") - published_start == timedelta(days=1, hours=1)
            member.goto(f"{base}/v/inbox")
            expect(member.locator("#inbox-list")).to_contain_text("Reminder")
            member.goto(f"{base}/v/schedule")
            member.get_by_role("link", name=target_title, exact=False).click()
            expect(member.locator("#assignment-card .status-text.pending")).to_contain_text(
                "Unanswered"
            )
            member.get_by_role("button", name="Accept", exact=True).click()
            expect(member.locator("#assignment-card .status-text.accepted")).to_contain_text(
                "Accepted"
            )

        solutions = playbook.request("GET", f"/solutions/?org_id={playbook.org}")["items"]
        assert [item["id"] for item in solutions if item["is_published"]] == [candidate_id]
        current_assignments = _assignment_map(playbook, candidate_id)
        for event_id in event_ids:
            assert current_assignments[(event_id, role)] == prior_assignments[(event_id, role)]
        for event_id, times in unchanged_times.items():
            event = playbook.request("GET", f"/events/{event_id}")
            assert (
                _utc_datetime(event["start_time"]),
                _utc_datetime(event["end_time"]),
            ) == times
        _fits(page)
        _fits(member)
        page.screenshot(
            path=str(tmp_path / f"{playbook_spec.id}-{width}-schedule-change-admin.png"),
            full_page=True,
        )
        member.screenshot(
            path=str(tmp_path / f"{playbook_spec.id}-{width}-schedule-change-member.png"),
            full_page=True,
        )
        no_js_errors(member)
        no_js_errors(page)


@pytest.mark.parametrize("width", [360, 1440])
def test_two_org_every_role_respects_tenant_and_admin_boundaries(
    live_server, new_context, tmp_path, width
):
    """Run BO-12 with both bundled organizations alive in the same server."""
    base = live_server
    specs = discover_playbooks([BUILTIN_DIRECTORY])
    assert {spec.id for spec in specs} == {"church", "basketball"}

    with httpx.Client(base_url=base, timeout=30) as client:
        domains = {spec.id: Playbook(client, spec.model_copy(deep=True)) for spec in specs}
        solutions = {}
        for domain, playbook in domains.items():
            playbook.event(0)
            solution = playbook.solve()
            playbook.assert_complete(solution["solution_id"])
            solutions[domain] = solution["solution_id"]

        for domain, playbook in domains.items():
            foreign = next(candidate for key, candidate in domains.items() if key != domain)
            foreign_person_id, foreign_person = next(iter(foreign.people.items()))

            admin = new_context().new_page()
            admin.set_viewport_size({"width": width, "height": 900})
            _login(admin, base, playbook.email, playbook.password, "/a/dashboard")
            admin.goto(f"{base}/a/people")
            expect(admin.locator("#people-list")).to_contain_text(
                next(iter(playbook.people.values()))["name"]
            )
            expect(admin.locator("#people-list")).not_to_contain_text(foreign_person["name"])
            _fits(admin)
            admin.screenshot(
                path=str(tmp_path / f"{domain}-{width}-tenant-admin-boundary.png"),
                full_page=True,
            )

            playbook.request("GET", f"/organizations/{foreign.org}", 403)
            playbook.request("GET", f"/people/?org_id={foreign.org}", 403)
            playbook.request(
                "POST",
                f"/solutions/{solutions[foreign.spec['id']]}/publish",
                404,
            )

            for role in playbook.spec["roles"]:
                person_id, person = next(
                    (candidate_id, candidate)
                    for candidate_id, candidate in playbook.people.items()
                    if role in candidate["roles"]
                )
                peer_id = next(
                    candidate_id for candidate_id in playbook.people if candidate_id != person_id
                )
                member_headers = playbook.member_headers(person_id)

                actor = new_context().new_page()
                actor.set_viewport_size({"width": width, "height": 900})
                _login(actor, base, person["email"], playbook.password, "/v/schedule")
                expect(actor.locator(".page-title")).to_have_text("Schedule")
                _fits(actor)
                actor.screenshot(
                    path=str(tmp_path / f"{domain}-{width}-{role}-tenant-boundary.png"),
                    full_page=True,
                )
                actor.goto(f"{base}/a/people")
                actor.wait_for_url("**/v/schedule")
                expect(actor.locator(".page-title")).to_have_text("Schedule")

                me = playbook.request("GET", "/people/me", headers=member_headers)
                assert me["id"] == person_id
                assert me["org_id"] == playbook.org
                playbook.request(
                    "POST",
                    f"/invitations?org_id={playbook.org}",
                    403,
                    {
                        "name": "Unauthorized invite",
                        "email": f"denied-{role}@{playbook.org}.example",
                        "roles": ["volunteer"],
                    },
                    headers=member_headers,
                )
                playbook.request(
                    "POST",
                    f"/solutions/{solutions[domain]}/publish",
                    403,
                    headers=member_headers,
                )
                playbook.request(
                    "GET",
                    f"/people/{foreign_person_id}",
                    403,
                    headers=member_headers,
                )
                rejected_date = (playbook.start + timedelta(days=2)).isoformat()
                playbook.request(
                    "POST",
                    f"/availability/{peer_id}/timeoff",
                    403,
                    {
                        "start_date": rejected_date,
                        "end_date": rejected_date,
                        "reason": "Peer mutation must fail",
                    },
                    headers=member_headers,
                )


@pytest.mark.parametrize("width", [360, 1440])
def test_recurring_change_and_cancel_scope(live_server, page, tmp_path, playbook_spec, width):
    base = live_server
    page.set_viewport_size({"width": width, "height": 900})
    with httpx.Client(base_url=base, timeout=30) as client:
        playbook = Playbook(client, playbook_spec, seed_people=False)
        _login(page, base, playbook.email, playbook.password, "/a/dashboard")
        title = f"{playbook.spec['event']} change drill"
        page.goto(f"{base}/a/recurring")
        page.get_by_role("button", name="New series").click()
        page.fill("#rs_title", title)
        page.check('input[name="selected_days"][value="sunday"]')
        page.fill("#rs_sd", playbook.start.isoformat())
        page.fill("#rs_st", "14:00")
        page.fill("#rs_oc", "3")
        page.fill('input[name="role_name"]', playbook.spec["critical_role"])
        page.fill('input[name="role_count"]', "1")
        page.get_by_role("button", name="Create series").click()
        expect(page.locator("#recurring-list")).to_contain_text(title)

        series = playbook.request("GET", f"/recurring-series?org_id={playbook.org}")["items"]
        assert len(series) == 1
        series_id = series[0]["id"]
        occurrences = playbook.request("GET", f"/recurring-series/{series_id}/occurrences")[
            "occurrences"
        ]
        assert len(occurrences) == 3
        first, second, third = occurrences
        original_third_start = _utc_datetime(third["start_time"])

        first_start = _utc_datetime(first["start_time"]) + timedelta(hours=1)
        first_end = _utc_datetime(first["end_time"]) + timedelta(hours=1)
        moved = _edit_event_in_browser(
            page,
            base,
            playbook,
            first["id"],
            first_start,
            first_end,
        )
        assert _utc_datetime(moved["start_time"]) == first_start
        assert (
            _utc_datetime(playbook.request("GET", f"/events/{third['id']}")["start_time"])
            == original_third_start
        )

        page.goto(f"{base}/a/events")
        second_row = page.locator(f'.event-row[data-event-id="{second["id"]}"]')
        page.once("dialog", lambda dialog: dialog.accept())
        second_row.get_by_role("button", name="Cancel occurrence").click()
        expect(page.locator(f'[data-event-id="{second["id"]}"]')).to_have_count(0)
        playbook.request("GET", f"/events/{second['id']}", 404)
        assert playbook.request("GET", f"/events/{first['id']}")["id"] == first["id"]
        assert (
            _utc_datetime(playbook.request("GET", f"/events/{third['id']}")["start_time"])
            == original_third_start
        )
        _fits(page)
        page.screenshot(
            path=str(tmp_path / f"{playbook_spec.id}-{width}-occurrence-scope.png"),
            full_page=True,
        )

        page.goto(f"{base}/a/recurring")
        page.once("dialog", lambda dialog: dialog.accept())
        page.get_by_role("button", name="Delete entire series").click()
        expect(page.locator("#recurring-list")).to_contain_text("No recurring series yet")
        playbook.request("GET", f"/events/{first['id']}", 404)
        playbook.request("GET", f"/events/{third['id']}", 404)
        no_js_errors(page)


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
        expected_assignments = sum(p.spec["roles"].values()) * 12
        expect(page.locator(".kpi").filter(has_text="Assignments")).to_contain_text(
            str(expected_assignments)
        )
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
        _edit_event_in_browser(page, base, p, created["id"], moved_start, moved_end)
        member.get_by_role("button", name="Accept", exact=True).click()
        expect(member.locator("#assignment-card .alert-error")).to_contain_text(
            "Assignment changed from revision 1 to 2"
        )
        _fits(member)
        member.reload()
        member.get_by_role("button", name="Accept", exact=True).click()
        expect(member.locator("#assignment-card .status-text.accepted")).to_contain_text("Accepted")
        _fits(member)
        accepted_start = datetime.fromisoformat(p.events[created["id"]]["start_time"])
        accepted_end = datetime.fromisoformat(p.events[created["id"]]["end_time"])
        _edit_event_in_browser(
            page,
            base,
            p,
            created["id"],
            accepted_start + timedelta(minutes=15),
            accepted_end + timedelta(minutes=15),
        )
        member.reload()
        expect(member.locator("#assignment-card .status-text.pending")).to_contain_text(
            "Unanswered"
        )
        member.get_by_role("button", name="Accept", exact=True).click()
        expect(member.locator("#assignment-card .status-text.accepted")).to_contain_text("Accepted")
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


@pytest.mark.parametrize("width", [360, 1440])
def test_domain_browser_rolls_published_horizon_to_week_seven(
    live_server, page, tmp_path, playbook_spec, width
):
    base = live_server
    page.set_viewport_size({"width": width, "height": 900})
    with httpx.Client(base_url=base, timeout=30) as client:
        playbook = Playbook(client, playbook_spec)
        # The fixture is three days into its operating week: both week-one
        # sessions are completed while weeks two through six remain future.
        playbook.start = date.today() - timedelta(days=3)
        for week in range(6):
            playbook.event(week, "main", 10)
            playbook.event(week, playbook.spec["secondary_event"], 18, day_offset=1)

        prior = playbook.solve()
        prior_id = prior["solution_id"]
        playbook.assert_complete(prior_id)
        playbook.request("POST", f"/solutions/{prior_id}/publish")
        original_ids = set(playbook.events)
        completed_ids = {
            event_id
            for event_id, event in playbook.events.items()
            if datetime.fromisoformat(event["end_time"]).date() < date.today()
        }
        assert len(completed_ids) == 2

        _login(page, base, playbook.email, playbook.password, "/a/dashboard")
        page.goto(f"{base}/a/events")
        past = page.locator("#events-list .group").last
        for event_id in completed_ids:
            expect(past).to_contain_text(playbook.events[event_id]["type"])

        _create_event_in_browser(page, base, playbook, 6, "main", 10, 0)
        _create_event_in_browser(
            page,
            base,
            playbook,
            6,
            playbook.spec["secondary_event"],
            18,
            1,
        )
        rolling_start = playbook.start + timedelta(weeks=1)
        rolling_end = rolling_start + timedelta(weeks=6)
        candidate_id = _solve_and_publish_in_browser(page, base, rolling_start, rolling_end)

        expected_ids = set(playbook.events) - completed_ids
        assert len(expected_ids) == 12
        playbook.assert_complete(candidate_id, expected_ids)
        solutions = playbook.request("GET", f"/solutions/?org_id={playbook.org}")["items"]
        assert [row["id"] for row in solutions if row["is_published"]] == [candidate_id]
        assert next(row for row in solutions if row["id"] == prior_id)["is_published"] is False

        current_ids = {
            event["id"]
            for event in playbook.request("GET", f"/events/?org_id={playbook.org}")["items"]
        }
        assert current_ids == set(playbook.events)
        assert original_ids <= current_ids
        page.goto(f"{base}/a/events")
        for event_id in completed_ids:
            expect(page.locator("#events-list")).to_contain_text(playbook.events[event_id]["type"])
        if width <= 480:
            completed_row = page.locator(f'.event-row[data-event-id="{next(iter(completed_ids))}"]')
            row_box = completed_row.bounding_box()
            title_box = completed_row.locator(".row-main").bounding_box()
            actions_box = completed_row.locator(".event-actions").bounding_box()
            assert row_box is not None and title_box is not None and actions_box is not None
            assert title_box["width"] >= row_box["width"] - 30
            assert actions_box["width"] >= row_box["width"] - 30
        _fits(page)
        page.screenshot(
            path=str(tmp_path / f"{playbook_spec.id}-{width}-week-seven-rollover.png"),
            full_page=True,
        )
        no_js_errors(page)
