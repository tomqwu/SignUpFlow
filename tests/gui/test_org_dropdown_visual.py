"""Visual test to verify org dropdown is actually visible in the browser."""
import pytest
from playwright.sync_api import expect

APP_URL = "http://localhost:8000"


@pytest.mark.gui
def test_org_dropdown_actually_visible_screenshot(api_server, authenticated_page):
    """Take screenshot and verify org dropdown is visible to user."""
    page = authenticated_page
    
    # Wait for page to fully load
    page.wait_for_timeout(3000)
    
    # Take screenshot of the whole page
    page.screenshot(path="/tmp/org_dropdown_test.png")
    print("Screenshot saved to /tmp/org_dropdown_test.png")
    
    # Check if dropdown exists
    org_dropdown = page.locator('#org-dropdown-visible')
    
    # Verify it's in the DOM
    count = org_dropdown.count()
    print(f"Dropdown count in DOM: {count}")
    assert count > 0, "Dropdown not in DOM"
    
    # Check if it's VISIBLE (not hidden)
    is_visible = org_dropdown.is_visible()
    print(f"Dropdown is_visible: {is_visible}")
    
    # Get computed styles to see if it's hidden
    display = org_dropdown.evaluate("el => getComputedStyle(el).display")
    visibility = org_dropdown.evaluate("el => getComputedStyle(el).visibility")
    opacity = org_dropdown.evaluate("el => getComputedStyle(el).opacity")
    
    print(f"Display: {display}")
    print(f"Visibility: {visibility}")
    print(f"Opacity: {opacity}")
    
    # Check bounding box (size and position)
    box = org_dropdown.bounding_box()
    if box:
        print(f"Position: x={box['x']}, y={box['y']}")
        print(f"Size: width={box['width']}, height={box['height']}")
    else:
        print("Bounding box: None (element not rendered)")
    
    # Get the HTML content
    html = org_dropdown.evaluate("el => el.outerHTML")
    print(f"HTML: {html[:200]}")
    
    # ASSERTIONS
    assert is_visible, "Dropdown exists but is not visible!"
    assert display != "none", f"Dropdown has display: {display}"
    assert box is not None, "Dropdown has no bounding box (not rendered)"
    assert box['width'] > 0, f"Dropdown width is {box['width']}"
    assert box['height'] > 0, f"Dropdown height is {box['height']}"
