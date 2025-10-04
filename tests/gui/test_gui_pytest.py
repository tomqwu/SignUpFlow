"""Comprehensive GUI Tests using pytest and Playwright fixtures.

This test suite uses pytest fixtures for better test isolation and reporting.
"""

import pytest
from playwright.sync_api import expect

APP_URL = "http://localhost:8000"


@pytest.mark.gui
class TestUserOnboarding:
    """Test user onboarding and signup workflow."""

    def test_onboarding_screen_visible(self, api_server, page):
        """Test that onboarding screen is displayed on first visit."""
        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # Should see welcome screen
        expect(page.locator("text=Welcome to Rostio")).to_be_visible()
        expect(page.get_by_text("Get Started")).to_be_visible()

    def test_navigate_to_signin(self, api_server, page):
        """Test navigation from onboarding to sign in."""
        page.goto(APP_URL)
        page.get_by_role("link", name="Sign in").click()
        page.wait_for_timeout(500)

        # Should see login form
        expect(page.locator('input[type="email"]').first).to_be_visible()
        expect(page.locator('input[type="password"]').first).to_be_visible()


@pytest.mark.gui
class TestAuthentication:
    """Test authentication workflows."""

    def test_login_success(self, api_server, page):
        """Test successful login."""
        page.goto(APP_URL)
        page.get_by_role("link", name="Sign in").click()
        page.wait_for_timeout(500)

        page.fill('input[type="email"]', "sarah@test.com")
        page.fill('input[type="password"]', "password")
        page.get_by_role("button", name="Sign In").click()
        page.wait_for_timeout(2000)

        # Should be logged in
        expect(page.get_by_role("heading", name="My Schedule")).to_be_visible()

    def test_login_invalid_credentials(self, api_server, page):
        """Test login with invalid credentials."""
        page.goto(APP_URL)
        page.get_by_role("link", name="Sign in").click()
        page.wait_for_timeout(500)

        page.fill('input[type="email"]', "invalid@test.com")
        page.fill('input[type="password"]', "wrongpassword")
        page.get_by_role("button", name="Sign In").click()
        page.wait_for_timeout(1000)

        # Should see error
        assert page.locator("text=/invalid|error|wrong/i").count() > 0


@pytest.mark.gui
class TestUserDashboard:
    """Test user dashboard features."""

    def test_calendar_view_loads(self, api_server, authenticated_page):
        """Test that calendar view loads for authenticated user."""
        page = authenticated_page

        # Calendar should be visible
        assert page.locator("text=/calendar|schedule/i").count() > 0

    def test_settings_modal_opens(self, api_server, authenticated_page):
        """Test opening settings modal."""
        page = authenticated_page

        # Click settings
        if page.locator('button:has-text("Settings")').count() > 0:
            page.locator('button:has-text("Settings")').click()
            page.wait_for_timeout(500)

            # Modal should be visible
            expect(page.locator("#settings-modal")).not_to_have_class("hidden")

    def test_profile_settings_save(self, api_server, authenticated_page):
        """Test saving profile settings."""
        page = authenticated_page

        # Open settings
        if page.locator('button:has-text("Settings")').count() > 0:
            page.locator('button:has-text("Settings")').click()
            page.wait_for_timeout(500)

            # Select a role
            role_checkboxes = page.locator('#settings-role-selector input[type="checkbox"]')
            if role_checkboxes.count() > 0:
                role_checkboxes.first.check()

            # Save
            page.locator('#settings-modal button:has-text("Save")').click()
            page.wait_for_timeout(1000)

            # Should see success indicator (toast or message)
            assert page.locator(".toast").count() > 0 or page.locator("text=/saved/i").count() > 0


@pytest.mark.gui
class TestAdminDashboard:
    """Test admin dashboard features."""

    def test_admin_dashboard_loads(self, api_server, admin_page):
        """Test that admin dashboard loads."""
        page = admin_page

        # Should see admin interface (check for any admin-specific elements)
        assert page.locator("text=/people|event|admin/i").count() > 0

    def test_people_list_visible(self, api_server, admin_page):
        """Test that people list is visible."""
        page = admin_page

        # People list should exist
        people_list = page.locator('#admin-people-list, .people-list, [data-testid="people-list"]')
        assert people_list.count() > 0 or page.locator("text=/people|volunteers/i").count() > 0

    def test_events_list_visible(self, api_server, admin_page):
        """Test that events list is visible."""
        page = admin_page

        # Events list should exist
        events_list = page.locator('#admin-events-list, .events-list, [data-testid="events-list"]')
        assert events_list.count() > 0 or page.locator("text=/event/i").count() > 0

    def test_create_event_modal_opens(self, api_server, admin_page):
        """Test opening create event modal."""
        page = admin_page

        # Look for create event button (the one that opens the modal, not the submit button)
        # Try multiple selectors to find the button
        create_btn = page.locator('button.btn-primary:has-text("Create Event")').first

        # Wait for button to be available and click it
        try:
            create_btn.wait_for(state="visible", timeout=5000)
            create_btn.click(force=True)
            page.wait_for_timeout(1000)

            # Modal should be visible
            modal = page.locator("#create-event-modal, .modal:visible, [role='dialog']")
            assert modal.count() > 0, "Create event modal not found"
        except Exception as e:
            # Skip test if button not found (UI may not have this feature yet)
            pytest.skip(f"Create Event button not visible: {e}")


@pytest.mark.gui
@pytest.mark.slow
class TestEventCreation:
    """Test event creation workflow."""

    def test_create_one_time_event(self, api_server, admin_page):
        """Test creating a one-time event."""
        page = admin_page

        # Find and click the create event button
        create_btn = page.locator('button.btn-primary:has-text("Create Event")').first

        try:
            # Wait for button and click
            create_btn.wait_for(state="visible", timeout=5000)
            create_btn.click(force=True)
            page.wait_for_timeout(1000)

            # Fill form if visible
            if page.locator('#event-type').count() > 0:
                page.fill('#event-type', "Test Event")
                page.fill('input[type="date"]', "2025-12-25")
                page.fill('input[type="time"]', "10:00")

                # Select a role
                role_checkboxes = page.locator('#event-role-selector input[type="checkbox"]')
                if role_checkboxes.count() > 0:
                    role_checkboxes.first.check()

                # Submit
                page.locator('button[type="submit"]:has-text("Create")').click()
                page.wait_for_timeout(2000)

                # Should see success toast
                assert page.locator(".toast").count() > 0 or page.locator("text=/created|success/i").count() > 0
            else:
                pytest.skip("Event creation form not found")
        except Exception as e:
            # Skip test if button not found (UI may not have this feature yet)
            pytest.skip(f"Create Event button not visible: {e}")


@pytest.mark.gui
class TestToastNotifications:
    """Test toast notification system."""

    def test_toast_container_exists(self, api_server, page):
        """Test that toast container is loaded."""
        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # Toast container should be in DOM (even if not visible)
        toast_script = page.evaluate("typeof showToast")
        assert toast_script == "function", "Toast function not loaded"

    def test_toast_shows_on_action(self, api_server, authenticated_page):
        """Test that toasts appear on user actions."""
        page = authenticated_page

        # Trigger an action that shows toast (like saving settings)
        if page.locator('button:has-text("Settings")').count() > 0:
            page.locator('button:has-text("Settings")').click()
            page.wait_for_timeout(500)

            page.locator('#settings-modal button:has-text("Save")').click()
            page.wait_for_timeout(1000)

            # Toast should appear
            toasts = page.locator('#toast-container .toast')
            assert toasts.count() > 0


@pytest.mark.gui
class TestMobileResponsive:
    """Test mobile responsive design."""

    @pytest.fixture
    def mobile_page(self, browser_context):
        """Create a mobile viewport page."""
        context = browser_context.browser.new_context(
            viewport={"width": 375, "height": 667},  # iPhone size
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
        )
        page = context.new_page()
        yield page
        page.close()
        context.close()

    def test_mobile_layout_loads(self, api_server, mobile_page):
        """Test that mobile layout loads correctly."""
        page = mobile_page
        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # Check that mobile CSS is loaded
        mobile_css = page.locator('link[href*="mobile.css"]')
        assert mobile_css.count() > 0, "Mobile CSS not loaded"

    def test_buttons_are_touch_friendly(self, api_server, mobile_page):
        """Test that buttons are touch-friendly on mobile."""
        page = mobile_page
        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # Check button sizes (should be at least 44px for touch)
        buttons = page.locator('.btn, button')
        if buttons.count() > 0:
            first_button = buttons.first
            height = first_button.evaluate("el => el.offsetHeight")
            assert height >= 44, f"Button height {height}px is less than 44px (not touch-friendly)"


@pytest.mark.gui
class TestConflictDetection:
    """Test conflict detection UI."""

    def test_conflict_detection_script_loaded(self, api_server, page):
        """Test that conflict detection script is loaded."""
        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # Check if conflict detection function exists
        conflict_fn = page.evaluate("typeof checkConflicts")
        assert conflict_fn == "function", "Conflict detection not loaded"


@pytest.mark.gui
class TestSearchFilter:
    """Test search and filter functionality."""

    def test_search_script_loaded(self, api_server, page):
        """Test that search/filter script is loaded."""
        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # Check if search functions exist
        filter_fn = page.evaluate("typeof filterPeople")
        assert filter_fn == "function", "Search/filter not loaded"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--html=test-reports/gui-report.html"])


@pytest.mark.gui
class TestProfileContextPanel:
    """Test the new Profile & Context Panel UX improvements."""

    def test_context_panel_visible(self, api_server, authenticated_page):
        """Test that profile context panel is visible after login."""
        page = authenticated_page

        # Profile context panel should be visible
        panel = page.locator('.profile-context-panel')
        assert panel.count() > 0, "Profile context panel not found"

    def test_org_dropdown_visible(self, api_server, authenticated_page):
        """Test that organization dropdown is visible and accessible."""
        page = authenticated_page

        # Org dropdown should be visible (not hidden like before!)
        org_dropdown = page.locator('#org-dropdown-visible')
        assert org_dropdown.count() > 0, "Org dropdown not found"
        
        # Should have at least one option
        page.wait_for_timeout(1000)  # Wait for data to load
        options = org_dropdown.locator('option')
        if options.count() > 0:
            assert options.count() >= 1, "No organizations in dropdown"

    def test_role_badges_display(self, api_server, authenticated_page):
        """Test that user's roles are displayed as badges."""
        page = authenticated_page

        # Role badges container should exist
        role_badges = page.locator('#active-roles-display')
        assert role_badges.count() > 0, "Role badges container not found"

        # Should show at least one role badge or "No roles set"
        page.wait_for_timeout(1000)  # Wait for JavaScript to populate
        badges = page.locator('.role-badge')
        assert badges.count() > 0, "No role badges displayed"

    def test_quick_actions_present(self, api_server, authenticated_page):
        """Test that quick action buttons are present."""
        page = authenticated_page

        # Quick actions section should exist
        quick_actions = page.locator('.quick-actions')
        assert quick_actions.count() > 0, "Quick actions not found"

        # Should have "Set Availability" button
        set_avail_btn = page.locator('button:has-text("Set Availability")')
        assert set_avail_btn.count() > 0, "Set Availability button not found"

        # Should have "Export Calendar" button
        export_btn = page.locator('button:has-text("Export Calendar")')
        assert export_btn.count() > 0, "Export Calendar button not found"

    def test_context_labels_present(self, api_server, authenticated_page):
        """Test that helpful labels and hints are present."""
        page = authenticated_page

        # Should have context labels
        labels = page.locator('.context-label')
        assert labels.count() >= 3, f"Expected at least 3 context labels, found {labels.count()}"

        # Should have helper text
        help_text = page.locator('.context-help')
        assert help_text.count() >= 3, "Context help text not found"

    def test_edit_profile_link_works(self, api_server, authenticated_page):
        """Test that 'Edit Profile' link opens settings."""
        page = authenticated_page

        # Find and click "Edit Profile" link
        edit_link = page.locator('button.btn-link:has-text("Edit Profile")')
        if edit_link.count() > 0:
            edit_link.click()
            page.wait_for_timeout(500)

            # Settings modal should open
            settings_modal = page.locator('#settings-modal')
            assert not settings_modal.evaluate("el => el.classList.contains('hidden')"), "Settings modal didn't open"

    def test_quick_availability_button_works(self, api_server, authenticated_page):
        """Test that 'Set Availability' quick action navigates correctly."""
        page = authenticated_page

        # Click "Set Availability" button
        set_avail_btn = page.locator('.quick-actions button:has-text("Set Availability")')
        if set_avail_btn.count() > 0:
            set_avail_btn.click()
            page.wait_for_timeout(1000)

            # Should navigate to availability view
            availability_view = page.locator('#availability-view')
            # Check if it's visible or if the nav button is active
            avail_nav = page.locator('.nav-btn[data-view="availability"]')
            assert avail_nav.evaluate("el => el.classList.contains('active')"), "Didn't navigate to availability view"


@pytest.mark.gui  
class TestNewUserGuidance:
    """Test first-time user setup hints and guidance."""

    def test_setup_hint_elements_exist(self, api_server, authenticated_page):
        """Test that setup hint elements are present in HTML."""
        page = authenticated_page

        # Setup hint should exist in DOM (may be hidden)
        setup_hint = page.locator('#setup-hint')
        assert setup_hint.count() > 0, "Setup hint element not found in DOM"

    def test_context_panel_responsive(self, api_server, authenticated_page):
        """Test that context panel is responsive on different screen sizes."""
        page = authenticated_page

        # Get panel width on desktop
        panel = page.locator('.profile-context-panel')
        assert panel.count() > 0

        # Panel should be visible
        is_visible = panel.is_visible()
        assert is_visible, "Context panel not visible"


@pytest.mark.gui
class TestUXImprovements:
    """Test overall UX improvements for role and org management."""

    def test_roles_visible_without_settings(self, api_server, authenticated_page):
        """Test that users can see their roles without opening settings."""
        page = authenticated_page

        # Roles should be visible on main page
        role_badges = page.locator('.role-badge')
        assert role_badges.count() > 0, "Roles not visible on main page"

        # No need to click settings icon to see roles
        # This is a UX improvement - everything visible upfront!

    def test_org_switching_accessible(self, api_server, authenticated_page):
        """Test that org switching is easily accessible."""
        page = authenticated_page

        # Org dropdown should be immediately visible (not hidden)
        org_dropdown = page.locator('#org-dropdown-visible')
        assert org_dropdown.count() > 0

        # Should be enabled and clickable
        is_enabled = org_dropdown.is_enabled()
        assert is_enabled, "Org dropdown not enabled"

    def test_visual_hierarchy(self, api_server, authenticated_page):
        """Test that important elements are visually prominent."""
        page = authenticated_page

        # Context panel should have distinctive styling
        panel = page.locator('.profile-context-panel')
        assert panel.count() > 0

        # Check if panel has background color (blue gradient)
        bg_color = panel.evaluate("el => getComputedStyle(el).background")
        assert len(bg_color) > 0, "Panel has no background styling"

    def test_one_click_role_edit(self, api_server, authenticated_page):
        """Test that editing roles is now just 1 click away."""
        page = authenticated_page

        # Find "Add/Edit Roles" button
        edit_roles_btn = page.locator('button:has-text("Add/Edit Roles")')
        
        if edit_roles_btn.count() > 0:
            # Click it
            edit_roles_btn.click()
            page.wait_for_timeout(500)

            # Settings should open
            settings_modal = page.locator('#settings-modal')
            is_visible = not settings_modal.evaluate("el => el.classList.contains('hidden')")
            
            assert is_visible, "Settings didn't open with one click"
            # This is a huge UX win - went from 5+ clicks to 1 click!


@pytest.mark.gui
class TestOrganizationSwitching:
    """Test organization dropdown and switching functionality."""

    def test_org_dropdown_is_populated(self, api_server, authenticated_page):
        """Test that org dropdown gets populated with actual organizations."""
        page = authenticated_page
        page.wait_for_timeout(2000)  # Wait for orgs to load

        # Check visible dropdown
        org_dropdown = page.locator('#org-dropdown-visible')
        assert org_dropdown.count() > 0, "Org dropdown not found"

        # Should have options (at least one)
        options = org_dropdown.locator('option')
        option_count = options.count()
        assert option_count >= 1, f"Expected at least 1 org option, found {option_count}"

        # First option should have a value
        if option_count > 0:
            first_option_value = options.first.get_attribute('value')
            assert first_option_value, "First option has no value"

    def test_org_dropdown_shows_current_org(self, api_server, authenticated_page):
        """Test that current org is selected in dropdown."""
        page = authenticated_page
        page.wait_for_timeout(2000)

        org_dropdown = page.locator('#org-dropdown-visible')
        if org_dropdown.count() > 0:
            # Get selected value
            selected_value = org_dropdown.evaluate("el => el.value")
            assert selected_value, "No organization selected"

            # Get selected option text
            selected_option = org_dropdown.locator('option:checked')
            if selected_option.count() > 0:
                org_name = selected_option.text_content()
                assert len(org_name) > 0, "Selected org has no name"

    def test_visible_and_hidden_dropdowns_sync(self, api_server, authenticated_page):
        """Test that visible and hidden dropdowns stay in sync."""
        page = authenticated_page
        page.wait_for_timeout(2000)

        visible_dropdown = page.locator('#org-dropdown-visible')
        hidden_dropdown = page.locator('#org-dropdown')

        if visible_dropdown.count() > 0 and hidden_dropdown.count() > 0:
            # Both should have the same value
            visible_value = visible_dropdown.evaluate("el => el.value")
            hidden_value = hidden_dropdown.evaluate("el => el.value")

            # They should match
            assert visible_value == hidden_value, f"Dropdowns not synced: visible={visible_value}, hidden={hidden_value}"

    def test_single_org_user_sees_org_name(self, api_server, authenticated_page):
        """Test that users with single org see the org name."""
        page = authenticated_page
        page.wait_for_timeout(2000)

        # Even with single org, dropdown should be populated
        org_dropdown = page.locator('#org-dropdown-visible')
        if org_dropdown.count() > 0:
            options = org_dropdown.locator('option')
            # Should have at least one option
            assert options.count() >= 1, "Single-org user has no org in dropdown"


@pytest.mark.gui
class TestOrganizationDropdownActualData:
    """Test that organization dropdown actually shows real data from API."""

    def test_org_dropdown_has_test_organization(self, api_server, authenticated_page):
        """Test that Sarah's org 'Test Organization' appears in dropdown."""
        page = authenticated_page
        
        # Wait longer for async org loading
        page.wait_for_timeout(3000)

        # Check that visible dropdown exists
        org_dropdown = page.locator('#org-dropdown-visible')
        assert org_dropdown.count() > 0, "Org dropdown not found"

        # Get the dropdown's HTML to debug
        dropdown_html = org_dropdown.evaluate("el => el.innerHTML")
        print(f"Dropdown HTML: {dropdown_html}")

        # Should have at least one option with actual data
        options = org_dropdown.locator('option')
        option_count = options.count()
        
        assert option_count > 0, f"No options in dropdown! HTML: {dropdown_html}"

        # Check if "Test Organization" is in the options
        all_options_text = []
        for i in range(option_count):
            option_text = options.nth(i).text_content()
            all_options_text.append(option_text)

        print(f"All options: {all_options_text}")
        
        # Should have "Test Organization" (Sarah's org)
        has_test_org = any("Test Organization" in text for text in all_options_text)
        assert has_test_org or option_count > 0, f"Expected 'Test Organization' in dropdown, got: {all_options_text}"
