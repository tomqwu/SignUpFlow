"""Debug what's actually in the dropdown when page loads."""
import pytest

APP_URL = "http://localhost:8000"


@pytest.mark.gui
def test_what_dropdown_shows_on_load(api_server, authenticated_page):
    """Debug: What does the dropdown actually show when page loads?"""
    page = authenticated_page
    
    print("\n=== WAITING 1 second ===")
    page.wait_for_timeout(1000)
    
    dropdown = page.locator('#org-dropdown-visible')
    print(f"Dropdown exists: {dropdown.count() > 0}")
    
    if dropdown.count() > 0:
        # Get the HTML
        html = dropdown.evaluate("el => el.outerHTML")
        print(f"Dropdown HTML: {html}")
        
        # Get the value
        value = dropdown.evaluate("el => el.value")
        print(f"Selected value: '{value}'")
        
        # Count options
        options = dropdown.locator('option')
        print(f"Number of options: {options.count()}")
        
        # List all options
        for i in range(options.count()):
            opt = options.nth(i)
            opt_value = opt.get_attribute('value')
            opt_text = opt.text_content()
            print(f"  Option {i}: value='{opt_value}', text='{opt_text}'")
    
    print("\n=== WAITING 3 more seconds for async load ===")
    page.wait_for_timeout(3000)
    
    # Check again after waiting
    if dropdown.count() > 0:
        html = dropdown.evaluate("el => el.outerHTML")
        print(f"After wait - HTML: {html}")
        
        value = dropdown.evaluate("el => el.value")
        print(f"After wait - Selected value: '{value}'")
        
        options = dropdown.locator('option')
        print(f"After wait - Number of options: {options.count()}")
        
        for i in range(options.count()):
            opt = options.nth(i)
            opt_value = opt.get_attribute('value')
            opt_text = opt.text_content()
            print(f"  Option {i}: value='{opt_value}', text='{opt_text}'")
    
    # Take screenshot
    page.screenshot(path="/tmp/dropdown_debug.png")
    print("Screenshot: /tmp/dropdown_debug.png")
