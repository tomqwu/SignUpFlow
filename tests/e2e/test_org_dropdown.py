"""Tests for verifying the organization dropdown functionality."""

from playwright.sync_api import sync_playwright, expect

from tests.e2e.helpers import ApiTestClient, AppConfig, login_via_ui


class TestOrgDropdown:
    def test_org_dropdown_exists(self, api_server, app_config: AppConfig):
        """Test that the organization selector exists for an authenticated user.

        The UI may render either a <select> dropdown (org-dropdown) or a read-only
        org badge (org-name-display) depending on how many orgs are available.
        """

        api = ApiTestClient(app_config.api_base)
        org = api.create_org(org_id="dropdown_test_org", name="Dropdown Test Org", region="US")
        user = api.create_user(
            org_id=org["id"],
            email="dropdown_test@example.com",
            password="password123",
            name="Dropdown Test User",
            roles=["admin"],
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})

            login_via_ui(page, app_config.app_url, user["email"], user["password"])

            dropdown = page.locator("#org-dropdown")
            org_badge = page.locator("#org-name-display")

            # Ensure the top-bar organization selector is present.
            expect(dropdown).to_have_count(1)

            # Wait until organizations have loaded: either the dropdown has options
            # or the org badge becomes visible.
            page.wait_for_function(
                """() => {
                    const dd = document.querySelector('#org-dropdown');
                    const badge = document.querySelector('#org-name-display');
                    const hasOptions = dd && dd.options && dd.options.length > 0;
                    const badgeVisible = badge && badge.offsetParent !== null;
                    return hasOptions || badgeVisible;
                }""",
                timeout=10000,
            )

            # Assert one of the two render modes is visible.
            if dropdown.is_visible():
                assert dropdown.locator('option').count() > 0
            else:
                expect(org_badge).to_be_visible()

            browser.close()

        api.close()
