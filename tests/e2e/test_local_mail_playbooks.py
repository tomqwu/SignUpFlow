"""Church and Basketball recovery and notification workflows through local mail."""

from __future__ import annotations

import re
import time
from datetime import date, timedelta
from email import policy
from email.message import Message
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path
from uuid import uuid4

import pytest
from playwright.sync_api import expect

from tests.e2e._helpers import no_js_errors, signup_admin

pytestmark = pytest.mark.e2e


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


def _message_parts(message: Message) -> list[str]:
    parts: list[str] = []
    for part in message.walk():
        if part.get_content_type() in {"text/plain", "text/html"}:
            parts.append(part.get_content())
    return parts


def _http_links(message: Message) -> list[str]:
    links: list[str] = []
    for part in message.walk():
        if part.get_content_type() == "text/html":
            parser = _LinkParser()
            parser.feed(part.get_content())
            links.extend(parser.links)
        elif part.get_content_type() == "text/plain":
            links.extend(re.findall(r"https?://[^\s<>]+", part.get_content()))
    return list(dict.fromkeys(link.rstrip(".,)") for link in links if link.startswith("http")))


def _wait_for_message(
    capture_dir: Path,
    *,
    recipient: str,
    subject_prefix: str,
    timeout: float = 15,
) -> Message:
    deadline = time.time() + timeout
    while time.time() < deadline:
        for path in capture_dir.glob("*.eml"):
            message = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
            if message["To"] == recipient and str(message["Subject"]).startswith(subject_prefix):
                return message
        time.sleep(0.1)
    found = [
        (
            path.name,
            str(BytesParser(policy=policy.default).parsebytes(path.read_bytes())["Subject"]),
        )
        for path in capture_dir.glob("*.eml")
    ]
    raise AssertionError(f"No {subject_prefix!r} message for {recipient}; found {found}")


def _action_link(message: Message, path_fragment: str) -> str:
    matches = [link for link in _http_links(message) if path_fragment in link]
    assert len(matches) == 1, (path_fragment, matches, _message_parts(message))
    return matches[0]


def _next_sunday() -> date:
    today = date.today()
    return today + timedelta(days=(6 - today.weekday()) % 7 + 14)


def _login(page, base: str, email: str, password: str) -> None:
    page.goto(f"{base}/auth/login")
    page.fill("#email", email)
    page.fill("#password", password)
    page.get_by_role("button", name="Sign in").click()


@pytest.mark.parametrize("width", [360, 1440])
def test_domain_recovery_and_notification_mail_flow(
    mail_live_server,
    mail_capture_dir,
    page,
    new_context,
    tmp_path,
    playbook_spec,
    width,
):
    base = mail_live_server
    page.set_viewport_size({"width": width, "height": 900})
    suffix = uuid4().hex[:10]
    admin_email = f"admin-{playbook_spec.id}-{suffix}@mail.e2e"
    member_email = f"member-{playbook_spec.id}-{suffix}@mail.e2e"
    old_password = "PlaybookTest123!"
    new_password = "RecoveredPlaybook123!"
    event_title = f"{playbook_spec.event} notification drill {suffix}"
    role = playbook_spec.critical_role

    signup_admin(
        page,
        base,
        org=f"{playbook_spec.name} {suffix}",
        name="Scheduling administrator",
        email=admin_email,
        password=old_password,
    )
    expect(page.get_by_role("link", name="Billing", exact=True)).to_have_count(0)
    page.goto(f"{base}/a/settings")
    expect(page.get_by_text("Local capture", exact=True)).to_be_visible()
    expect(page.get_by_text("No external message is sent", exact=False)).to_be_visible()

    page.goto(f"{base}/a/people")
    page.get_by_role("button", name="Invite person").click()
    page.fill("#inv_name", f"{role} member")
    page.fill("#inv_email", member_email)
    page.select_option("#inv_role", "volunteer")
    page.fill("#inv_qualifications", role)
    page.get_by_role("button", name="Send invite").click()
    expect(page.locator("#invite-result")).to_contain_text("queued in local mail capture")

    invitation = _wait_for_message(
        mail_capture_dir,
        recipient=member_email,
        subject_prefix="You're invited",
    )
    invitation_link = _action_link(invitation, "/auth/invitation/")
    assert invitation_link.startswith(base)

    member_context = new_context()
    member = member_context.new_page()
    member.set_viewport_size({"width": width, "height": 900})
    member.goto(invitation_link)
    member.fill("#password", old_password)
    member.get_by_role("button", name="Accept & continue").click()
    member.wait_for_url("**/v/schedule")

    member.goto(f"{base}/v/profile")
    member.get_by_role("button", name="Sign out").click()
    member.wait_for_url("**/auth/login")
    member.goto(f"{base}/auth/forgot")
    member.fill("#email", member_email)
    member.get_by_role("button", name="Send reset link").click()
    expect(member.get_by_role("status")).to_contain_text("recovery instructions were processed")

    reset = _wait_for_message(
        mail_capture_dir,
        recipient=member_email,
        subject_prefix="Reset your SignUpFlow password",
    )
    reset_link = _action_link(reset, "/auth/reset/")
    assert reset_link.startswith(base)
    member.goto(reset_link)
    member.fill("#password", new_password)
    member.get_by_role("button", name="Update password").click()
    member.wait_for_url("**/auth/login?reset=1")

    old_login = new_context().new_page()
    _login(old_login, base, member_email, old_password)
    expect(old_login.get_by_role("alert")).to_contain_text("Invalid email or password")
    replay = new_context().new_page()
    replay.goto(reset_link)
    replay.fill("#password", "ReplayMustFail123!")
    replay.get_by_role("button", name="Update password").click()
    expect(replay.get_by_role("alert")).to_contain_text("Invalid or expired reset token")

    _login(member, base, member_email, new_password)
    member.wait_for_url("**/v/schedule")

    event_date = _next_sunday()
    page.goto(f"{base}/a/events")
    page.get_by_role("button", name="New event", exact=True).click()
    page.fill("#ev_type", event_title)
    page.fill("#ev_date", event_date.isoformat())
    page.fill("#ev_start", "10:00")
    page.fill("#ev_end", "12:00")
    page.fill("input[name=role_name]", role)
    page.fill("input[name=role_count]", "1")
    page.get_by_role("button", name="Create event", exact=True).click()
    expect(page.locator("#events-list")).to_contain_text(event_title)

    page.goto(f"{base}/a/solver")
    page.fill("#from_date", event_date.isoformat())
    page.fill("#to_date", event_date.isoformat())
    page.get_by_role("button", name="Run solver").click()
    page.locator("#solver-result").get_by_role("link", name="Review solution").click()
    page.wait_for_url("**/a/solution/**")
    solution_url = page.url
    page.get_by_role("button", name="Publish this solution").click()
    expect(page.locator("#publish-state")).to_contain_text("Unpublish")

    assignment = _wait_for_message(
        mail_capture_dir,
        recipient=member_email,
        subject_prefix="New Assignment:",
    )
    assert event_title in str(assignment["Subject"])
    member.goto(f"{base}/v/inbox")
    expect(member.locator("#inbox-list")).to_contain_text("New assignment")

    page.goto(f"{base}/a/events")
    row = page.locator(".event-row", has_text=event_title)
    event_id = row.get_attribute("data-event-id")
    assert event_id
    row.get_by_role("button", name="Edit", exact=False).click()
    form = page.locator(f'form.event-edit-form[data-event-id="{event_id}"]')
    form.locator('input[name="start_time"]').fill("11:00")
    form.locator('input[name="end_time"]').fill("13:00")
    form.get_by_role("button", name="Save change").click()
    expect(form).to_be_hidden()

    update = _wait_for_message(
        mail_capture_dir,
        recipient=member_email,
        subject_prefix="Schedule Update:",
    )
    assert event_title in str(update["Subject"])
    member.reload()
    expect(member.locator("#inbox-list")).to_contain_text("Schedule update")

    page.goto(solution_url)
    page.get_by_role("button", name="Notify assignees").click()
    expect(page.locator("#notify-result")).to_contain_text("local mail capture")
    reminder = _wait_for_message(
        mail_capture_dir,
        recipient=member_email,
        subject_prefix="Reminder:",
    )
    assert event_title in str(reminder["Subject"])
    member.reload()
    expect(member.locator("#inbox-list")).to_contain_text("Reminder")
    page.screenshot(
        path=str(tmp_path / f"{playbook_spec.id}-{width}-local-mail-admin.png"),
        full_page=True,
    )
    member.screenshot(
        path=str(tmp_path / f"{playbook_spec.id}-{width}-local-mail-inbox.png"),
        full_page=False,
    )

    for message in (assignment, update, reminder):
        links = [link for link in _http_links(message) if link.startswith(base)]
        assert links
        for link in links:
            response = member.request.get(link)
            assert response.status < 400, (message["Subject"], link, response.status)

    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert member.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    no_js_errors(page)
    no_js_errors(member)
