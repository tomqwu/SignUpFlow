#!/bin/bash
# Take screenshots of all new features and update documentation

set -e

echo "📸 Taking Feature Screenshots..."
echo "================================"

# Kill any existing servers
lsof -ti:8000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
sleep 2

# Start server
echo "1️⃣ Starting server..."
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/screenshot_server.log 2>&1 &
SERVER_PID=$!
sleep 5

# Setup demo data
echo "2️⃣ Setting up demo data..."
bash /tmp/setup_demo_data.sh > /dev/null 2>&1 || true
bash scripts/prepare_for_screenshots.sh > /dev/null 2>&1 || true

# Create screenshots directory
mkdir -p docs/screenshots/features

# Take screenshots using Python/Playwright
echo "3️⃣ Taking screenshots..."
cat > /tmp/take_screenshots.py << 'PYTHON_SCRIPT'
from playwright.sync_api import sync_playwright
import time

BASE_URL = "http://localhost:8000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # Login as Sarah
    print("   Logging in...")
    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a:has-text("Sign in")').click()
    page.wait_for_timeout(500)
    page.fill('#login-email', 'sarah@grace.church')
    page.fill('#login-password', 'password123')
    page.click('button:has-text("Sign In")')
    page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

    # Screenshot 1: Calendar view
    print("   📸 Calendar view...")
    page.screenshot(path='/home/ubuntu/rostio/docs/screenshots/features/calendar-view.png', full_page=True)

    # Screenshot 2: Availability with edit/delete
    print("   📸 Availability page...")
    page.locator('button:has-text("Availability")').click()
    page.wait_for_timeout(1000)
    page.screenshot(path='/home/ubuntu/rostio/docs/screenshots/features/availability-edit-delete.png', full_page=True)

    # Screenshot 3: Add time-off
    print("   📸 Adding time-off...")
    page.fill('#timeoff-start', '2025-12-25')
    page.fill('#timeoff-end', '2025-12-31')
    page.screenshot(path='/home/ubuntu/rostio/docs/screenshots/features/add-timeoff-form.png', full_page=True)

    # Screenshot 4: Toast notification (after adding)
    page.click('button:has-text("Add Time Off")')
    page.wait_for_timeout(2000)
    print("   📸 Toast notification...")
    page.screenshot(path='/home/ubuntu/rostio/docs/screenshots/features/toast-notification.png', full_page=True)

    # Screenshot 5: Settings modal
    print("   📸 Settings modal...")
    page.locator('button.btn-icon').first.click()
    page.wait_for_timeout(500)
    page.screenshot(path='/home/ubuntu/rostio/docs/screenshots/features/settings-modal.png', full_page=True)

    # Screenshot 6: Admin dashboard
    print("   📸 Admin dashboard...")
    page.goto(BASE_URL)
    page.wait_for_load_state('networkidle')
    page.locator('a:has-text("Sign in")').click()
    page.wait_for_timeout(500)
    page.fill('#login-email', 'pastor@grace.church')
    page.fill('#login-password', 'password123')
    page.click('button:has-text("Sign In")')
    page.wait_for_selector('#main-app:not(.hidden)', timeout=10000)

    page.locator('button:has-text("Admin Dashboard")').click()
    page.wait_for_timeout(2000)
    page.screenshot(path='/home/ubuntu/rostio/docs/screenshots/features/admin-dashboard.png', full_page=True)

    browser.close()
    print("✅ Screenshots complete!")

PYTHON_SCRIPT

poetry run python /tmp/take_screenshots.py

# Kill server
echo "4️⃣ Cleaning up..."
kill $SERVER_PID 2>/dev/null || true
lsof -ti:8000 2>/dev/null | xargs -r kill -9 2>/dev/null || true

echo ""
echo "✅ Screenshots saved to docs/screenshots/features/"
ls -lh docs/screenshots/features/
