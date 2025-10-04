"""Test what happens when user clicks the org dropdown."""
import pytest

APP_URL = "http://localhost:8000"


@pytest.mark.gui
def test_click_org_dropdown_and_see_options(api_server, authenticated_page):
    """Test clicking the org dropdown to see what options appear."""
    page = authenticated_page
    page.wait_for_timeout(3000)
    
    # Find the dropdown
    dropdown = page.locator('#org-dropdown-visible')
    
    # Get all options
    options = dropdown.locator('option')
    option_count = options.count()
    
    print(f"\n=== Dropdown has {option_count} option(s) ===")
    
    for i in range(option_count):
        opt = options.nth(i)
        value = opt.get_attribute('value')
        text = opt.text_content()
        is_selected = opt.get_attribute('selected') is not None
        print(f"Option {i+1}: value='{value}', text='{text}', selected={is_selected}")
    
    # Click the dropdown to open it
    dropdown.click()
    page.wait_for_timeout(500)
    
    # Take screenshot after clicking
    page.screenshot(path="/tmp/dropdown_clicked.png")
    print("Screenshot saved to /tmp/dropdown_clicked.png")
    
    # The dropdown should have at least 1 option
    assert option_count >= 1, f"Expected at least 1 org option, found {option_count}"
    
    if option_count == 1:
        print("\n⚠️  WARNING: Only 1 organization found!")
        print("    User cannot 'switch between organizations' with only 1 org.")
        print("    The help text is misleading for single-org users.")
