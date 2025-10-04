"""GUI tests for dynamic assignment modal."""

import pytest
from playwright.sync_api import Page, expect
import time


@pytest.fixture
def setup_test_data(page: Page):
    """Setup test organization, people, and event."""
    timestamp = int(time.time() * 1000)
    org_id = f"gui_assign_org_{timestamp}"
    event_id = f"gui_assign_event_{timestamp}"

    # Create org
    page.goto("http://localhost:8000")
    page.evaluate(f"""
        fetch('http://localhost:8000/api/organizations/', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                id: '{org_id}',
                name: 'GUI Assignment Test Org',
                config: {{roles: ['volunteer', 'leader', 'admin']}}
            }})
        }})
    """)

    # Create people with different roles
    for name, email, roles in [
        ("Alice Volunteer", f"alice_{timestamp}@test.com", ["volunteer"]),
        ("Bob Leader", f"bob_{timestamp}@test.com", ["leader"]),
        ("Charlie Multi", f"charlie_{timestamp}@test.com", ["volunteer", "leader"]),
    ]:
        page.evaluate(f"""
            fetch('http://localhost:8000/api/auth/signup', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    name: '{name}',
                    email: '{email}',
                    password: 'password',
                    org_id: '{org_id}',
                    roles: {roles}
                }})
            }})
        """)

    # Create event with role requirements
    page.evaluate(f"""
        fetch('http://localhost:8000/api/events/', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                id: '{event_id}',
                org_id: '{org_id}',
                type: 'Test Event',
                start_time: new Date(Date.now() + 86400000).toISOString(),
                end_time: new Date(Date.now() + 90000000).toISOString(),
                extra_data: {{
                    role_counts: {{volunteer: 2, leader: 1}}
                }}
            }})
        }})
    """)

    return {"org_id": org_id, "event_id": event_id, "timestamp": timestamp}


def test_assignment_modal_opens(page: Page, setup_test_data):
    """Test that assignment modal opens when clicking Assign People button."""
    data = setup_test_data

    # Login
    page.goto("http://localhost:8000")
    page.fill("#login-email", f"alice_{data['timestamp']}@test.com")
    page.fill("#login-password", "password")
    page.click("button:text('Sign In')")
    page.wait_for_timeout(1000)

    # Go to admin events
    page.click("text=Admin")
    page.wait_for_timeout(500)

    # Click Assign People button
    page.click("button:text('Assign People')")

    # Modal should be visible
    expect(page.locator("#assignment-modal")).not_to_have_class("hidden")
    expect(page.locator("#assignment-modal h3")).to_contain_text("Assign People to Event")


def test_assignment_modal_shows_role_groups(page: Page, setup_test_data):
    """Test that assignment modal groups people by role."""
    data = setup_test_data

    # Login
    page.goto("http://localhost:8000")
    page.fill("#login-email", f"alice_{data['timestamp']}@test.com")
    page.fill("#login-password", "password")
    page.click("button:text('Sign In')")
    page.wait_for_timeout(1000)

    # Go to admin events
    page.click("text=Admin")
    page.wait_for_timeout(500)

    # Open assignment modal
    page.click("button:text('Assign People')")
    page.wait_for_timeout(500)

    # Check for role groups
    expect(page.locator(".role-group")).to_have_count(2)  # volunteer and leader
    expect(page.locator(".role-header:has-text('Volunteer')")).to_be_visible()
    expect(page.locator(".role-header:has-text('Leader')")).to_be_visible()

    # Check role counts are shown
    expect(page.locator(".role-count")).to_have_count(2)


def test_assign_person_from_modal(page: Page, setup_test_data):
    """Test assigning a person from the modal."""
    data = setup_test_data

    # Login
    page.goto("http://localhost:8000")
    page.fill("#login-email", f"bob_{data['timestamp']}@test.com")
    page.fill("#login-password", "password")
    page.click("button:text('Sign In')")
    page.wait_for_timeout(1000)

    # Go to admin events
    page.click("text=Admin")
    page.wait_for_timeout(500)

    # Open assignment modal
    page.click("button:text('Assign People')")
    page.wait_for_timeout(500)

    # Click Assign button for first person
    assign_button = page.locator(".person-assignment-item button:text('Assign')").first
    assign_button.click()
    page.wait_for_timeout(500)

    # Button should change to Unassign
    expect(assign_button).to_have_text("Unassign")
    expect(assign_button).to_have_class("btn btn-small btn-remove")


def test_unassign_person_from_modal(page: Page, setup_test_data):
    """Test unassigning a person from the modal."""
    data = setup_test_data

    # Login
    page.goto("http://localhost:8000")
    page.fill("#login-email", f"charlie_{data['timestamp']}@test.com")
    page.fill("#login-password", "password")
    page.click("button:text('Sign In')")
    page.wait_for_timeout(1000)

    # Go to admin events
    page.click("text=Admin")
    page.wait_for_timeout(500)

    # Open assignment modal
    page.click("button:text('Assign People')")
    page.wait_for_timeout(500)

    # Assign first
    assign_button = page.locator(".person-assignment-item button:text('Assign')").first
    assign_button.click()
    page.wait_for_timeout(500)

    # Now unassign
    assign_button.click()
    page.wait_for_timeout(500)

    # Button should change back to Assign
    expect(assign_button).to_have_text("Assign")
    expect(assign_button).not_to_have_class("btn-remove")


def test_assignment_reflects_on_event_card(page: Page, setup_test_data):
    """Test that assignments show on the event card."""
    data = setup_test_data

    # Login
    page.goto("http://localhost:8000")
    page.fill("#login-email", f"alice_{data['timestamp']}@test.com")
    page.fill("#login-password", "password")
    page.click("button:text('Sign In')")
    page.wait_for_timeout(1000)

    # Go to admin events
    page.click("text=Admin")
    page.wait_for_timeout(500)

    # Check initial state - no assignments
    event_card = page.locator(f"#event-{data['event_id']}")
    expect(event_card.locator(".event-assignments")).to_contain_text("No one assigned yet")

    # Open assignment modal and assign someone
    page.click("button:text('Assign People')")
    page.wait_for_timeout(500)
    page.locator(".person-assignment-item button:text('Assign')").first.click()
    page.wait_for_timeout(500)

    # Close modal
    page.click("#assignment-modal button:text('Done')")
    page.wait_for_timeout(500)

    # Event card should now show assignment
    expect(event_card.locator(".assigned-people")).to_be_visible()


def test_modal_closes_on_done_button(page: Page, setup_test_data):
    """Test that modal closes when clicking Done button."""
    data = setup_test_data

    # Login
    page.goto("http://localhost:8000")
    page.fill("#login-email", f"alice_{data['timestamp']}@test.com")
    page.fill("#login-password", "password")
    page.click("button:text('Sign In')")
    page.wait_for_timeout(1000)

    # Go to admin events
    page.click("text=Admin")
    page.wait_for_timeout(500)

    # Open assignment modal
    page.click("button:text('Assign People')")
    expect(page.locator("#assignment-modal")).not_to_have_class("hidden")

    # Click Done
    page.click("#assignment-modal button:text('Done')")
    page.wait_for_timeout(300)

    # Modal should be hidden
    expect(page.locator("#assignment-modal")).to_have_class("hidden")
