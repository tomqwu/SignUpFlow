# Quick Start: Mobile Responsive Design Testing (10 Minutes)

**Feature**: Mobile Responsive Design | **Branch**: `008-mobile-responsive-design` | **Date**: 2025-10-23

Get mobile testing running in 10 minutes using Playwright's mobile emulation. Test responsive layouts, touch interactions, and PWA functionality without physical devices.

---

## Prerequisites

- SignUpFlow backend running (`make run`)
- Playwright installed (`poetry run playwright install`)
- Modern browser (Chrome/Firefox)

**Time Estimate**: 10 minutes

---

## Step 1: Install Dependencies (2 minutes)

### Install Mobile Testing Tools

```bash
cd /home/ubuntu/SignUpFlow

# Install Playwright browsers with mobile support
poetry run playwright install chromium webkit

# Install Hammer.js for touch gestures
cd frontend
npm install hammerjs@2.0.17 --save

# Install Workbox for PWA
npm install workbox-cli --save-dev

# Verify installations
npm list hammerjs workbox-cli
```

**Expected Output**:
```
hammerjs@2.0.17
workbox-cli@7.0.0
```

---

## Step 2: Configure Playwright Mobile Emulation (2 minutes)

### Update Playwright Config

```bash
# Edit playwright.config.js
cat > playwright.config.js << 'EOF'
const { devices } = require('@playwright/test');

module.exports = {
    testDir: './tests/e2e',
    timeout: 30000,
    retries: 0,
    workers: 1,

    use: {
        baseURL: 'http://localhost:8000',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure'
    },

    projects: [
        // Mobile Chrome (Pixel 5)
        {
            name: 'Mobile Chrome',
            use: {
                ...devices['Pixel 5'],
                hasTouch: true,
                isMobile: true
            }
        },

        // Mobile Safari (iPhone 13)
        {
            name: 'Mobile Safari',
            use: {
                ...devices['iPhone 13'],
                hasTouch: true,
                isMobile: true
            }
        },

        // Tablet (iPad Pro)
        {
            name: 'Tablet',
            use: {
                ...devices['iPad Pro'],
                hasTouch: true
            }
        },

        // Desktop (for comparison)
        {
            name: 'Desktop',
            use: {
                ...devices['Desktop Chrome']
            }
        }
    ]
};
EOF
```

### Verify Configuration

```bash
# Test Playwright setup
poetry run playwright test --list

# Expected: Shows test files organized by project (Mobile Chrome, Mobile Safari, Tablet, Desktop)
```

---

## Step 3: Create Mobile Test Suite (3 minutes)

### Basic Responsive Layout Test

```bash
# Create test file
mkdir -p tests/e2e
cat > tests/e2e/test_mobile_workflows.py << 'EOF'
from playwright.sync_api import Page, expect

def test_mobile_navigation_visible(page: Page):
    """Test bottom navigation appears on mobile."""
    page.goto("/app/schedule")

    # Mobile: bottom nav visible, desktop nav hidden
    expect(page.locator('.bottom-nav')).to_be_visible()
    expect(page.locator('.desktop-nav')).to_be_hidden()

def test_schedule_loads_on_mobile(page: Page):
    """Test schedule view loads correctly on mobile."""
    page.goto("/app/schedule")

    # Verify schedule title
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible()

    # Verify at least one event card
    expect(page.locator('.event-card')).to_have_count_greater_than(0)

    # Verify mobile-optimized layout (single column)
    first_card = page.locator('.event-card').first
    width = first_card.bounding_box()['width']
    viewport_width = page.viewport_size['width']

    # On mobile, cards should be nearly full width (minus padding)
    assert width > viewport_width * 0.85, "Cards should be full-width on mobile"

def test_touch_targets_meet_wcag(page: Page):
    """Test all interactive elements meet 44x44px minimum (WCAG 2.1 AA)."""
    page.goto("/app/schedule")

    # Get all interactive elements
    buttons = page.locator('button, a, input[type="checkbox"]').all()

    for button in buttons:
        box = button.bounding_box()
        if box:  # Some elements might not be visible
            assert box['width'] >= 44, f"Button width {box['width']}px < 44px"
            assert box['height'] >= 44, f"Button height {box['height']}px < 44px"
EOF
```

### Touch Gesture Test

```bash
cat > tests/e2e/test_touch_interactions.py << 'EOF'
from playwright.sync_api import Page, expect

def test_swipe_navigation(page: Page):
    """Test swipe left/right on schedule view."""
    page.goto("/app/schedule")

    # Get current week text
    initial_week = page.locator('h2[data-i18n="schedule.week"]').text_content()

    # Swipe left on schedule view
    schedule_view = page.locator('#schedule-view')
    schedule_view.swipe_left()

    # Wait for animation
    page.wait_for_timeout(500)

    # Verify week changed
    new_week = page.locator('h2[data-i18n="schedule.week"]').text_content()
    assert new_week != initial_week, "Week should change after swipe left"

def test_tap_with_haptic_feedback(page: Page):
    """Test tap gesture on buttons."""
    page.goto("/app/schedule")

    # Tap on bottom nav item
    events_button = page.locator('.bottom-nav-item[data-route="/app/events"]')
    events_button.tap()

    # Verify navigation
    expect(page).to_have_url(/.*\/app\/events/)
EOF
```

---

## Step 4: Run Mobile Tests (2 minutes)

### Run All Mobile Tests

```bash
# Run tests on all mobile projects
poetry run pytest tests/e2e/test_mobile_workflows.py -v

# Run on specific device
poetry run pytest tests/e2e/test_mobile_workflows.py --project="Mobile Chrome" -v

# Run with visual output (headed mode)
poetry run pytest tests/e2e/test_mobile_workflows.py --headed -v
```

**Expected Output**:
```
tests/e2e/test_mobile_workflows.py::test_mobile_navigation_visible[Mobile Chrome] PASSED
tests/e2e/test_mobile_workflows.py::test_mobile_navigation_visible[Mobile Safari] PASSED
tests/e2e/test_mobile_workflows.py::test_schedule_loads_on_mobile[Mobile Chrome] PASSED
tests/e2e/test_mobile_workflows.py::test_touch_targets_meet_wcag[Mobile Chrome] PASSED

============================== 8 passed in 15.23s ==============================
```

### Run Touch Interaction Tests

```bash
poetry run pytest tests/e2e/test_touch_interactions.py --project="Mobile Chrome" -v
```

---

## Step 5: Manual Testing in Browser (1 minute)

### Chrome DevTools Device Toolbar

**Open DevTools**:
1. Navigate to `http://localhost:8000`
2. Press `Cmd+Opt+I` (Mac) or `Ctrl+Shift+I` (Windows/Linux)
3. Press `Cmd+Shift+M` (Mac) or `Ctrl+Shift+M` (Windows/Linux) to toggle device toolbar

**Test Devices**:
- **Mobile**: Select "iPhone 13" or "Pixel 5" from dropdown
- **Tablet**: Select "iPad Pro" from dropdown
- **Custom**: Click "Responsive" and enter custom dimensions

**Test Checklist**:
- [ ] Bottom navigation visible on mobile (< 768px)
- [ ] Desktop navigation visible on tablet/desktop (>= 768px)
- [ ] Touch targets are 44x44px minimum
- [ ] Text is readable (minimum 14px on mobile)
- [ ] No horizontal scrollbar
- [ ] Images load responsively

### Test Specific Breakpoints

```javascript
// Open DevTools Console and run:

// Test mobile (375px)
window.resizeTo(375, 667);

// Test tablet (768px)
window.resizeTo(768, 1024);

// Test desktop (1024px)
window.resizeTo(1024, 768);

// Verify layout adapts at each size
```

---

## Troubleshooting

### Issue: "Playwright browsers not installed"

**Symptom**: `Error: Executable doesn't exist at /path/to/chromium`

**Fix**:
```bash
# Install Playwright browsers
poetry run playwright install chromium webkit

# Verify installation
poetry run playwright --version
```

### Issue: "Cannot find module 'hammerjs'"

**Symptom**: `Error: Cannot resolve module 'hammerjs'`

**Fix**:
```bash
cd frontend
npm install hammerjs --save

# Verify
npm list hammerjs
# Should show: hammerjs@2.0.17
```

### Issue: Bottom nav not hiding on desktop

**Symptom**: Bottom navigation visible on desktop (1024px+)

**Fix**:
```css
/* frontend/css/mobile.css */
@media (max-width: 767px) {
    .desktop-nav { display: none; }
    .bottom-nav { display: flex; }
}

@media (min-width: 768px) {
    .desktop-nav { display: flex; }
    .bottom-nav { display: none; }
}
```

### Issue: Touch gestures not working

**Symptom**: Swipe left/right does nothing

**Fix**:
```javascript
// Verify Hammer.js initialization
import Hammer from 'hammerjs';

const element = document.getElementById('schedule-view');
const hammer = new Hammer(element);

// Enable swipe
hammer.get('swipe').set({ direction: Hammer.DIRECTION_HORIZONTAL });

// Log events for debugging
hammer.on('swipeleft swiperight', (event) => {
    console.log('Swipe detected:', event.type);
});
```

### Issue: Touch targets too small

**Symptom**: Buttons/links are less than 44x44px on mobile

**Fix**:
```css
/* Ensure minimum touch target size */
button,
a,
input[type="checkbox"],
.interactive {
    min-width: 44px;
    min-height: 44px;
    padding: 0.5rem 1rem;
}

/* Add visible touch areas for small icons */
.icon-button {
    min-width: 44px;
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
```

---

## Performance Testing

### Lighthouse Mobile Audit

```bash
# Run Lighthouse performance audit (mobile)
npx lighthouse http://localhost:8000 \
    --only-categories=performance \
    --emulated-form-factor=mobile \
    --throttling.rttMs=150 \
    --throttling.throughputKbps=1638 \
    --output=html \
    --output-path=./lighthouse-mobile-report.html

# Open report
open lighthouse-mobile-report.html
```

**Target Scores**:
- Performance: >90
- First Contentful Paint: <3s
- Time to Interactive: <5s
- Speed Index: <4s

### Network Throttling

```python
# tests/e2e/test_mobile_performance.py
def test_loads_on_slow_3g(page: Page, context):
    """Test app loads on Slow 3G network."""
    # Throttle network to Slow 3G
    context.set_offline(False)
    context.set_extra_http_headers({
        "Connection": "keep-alive"
    })

    # Emulate Slow 3G (500ms RTT, 400kbps down, 400kbps up)
    page.route("**/*", lambda route: route.continue_())

    page.goto("/app/schedule")

    # Verify page loads (even if slowly)
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible(
        timeout=10000  # 10 seconds for slow network
    )
```

---

## Verification Checklist

Before moving to implementation phase, verify:

- [ ] Playwright installed with mobile browsers
- [ ] Hammer.js installed in frontend
- [ ] Mobile test suite runs successfully
- [ ] Bottom navigation visible on mobile (<768px)
- [ ] Desktop navigation visible on tablet+ (>=768px)
- [ ] Touch targets meet 44x44px minimum (WCAG 2.1 AA)
- [ ] Swipe gestures work in Playwright tests
- [ ] Lighthouse mobile score >80
- [ ] Manual testing works in Chrome DevTools device mode

**Test Summary**:
```bash
# Run all mobile tests
poetry run pytest tests/e2e/test_mobile_workflows.py tests/e2e/test_touch_interactions.py -v

# Expected: All tests pass on Mobile Chrome, Mobile Safari, Tablet
```

---

## Next Steps

After completing this quickstart:

1. **Implement Responsive Layouts**:
   - Add mobile-first CSS with 3 breakpoints (320px, 768px, 1024px)
   - Implement bottom navigation for mobile
   - Add hamburger menu for secondary navigation

2. **Add Touch Gestures**:
   - Implement swipe navigation (Hammer.js)
   - Add pull-to-refresh
   - Add long-press context menus

3. **Enable PWA Capabilities**:
   - Generate PWA manifest
   - Implement service worker (Workbox)
   - Add offline data caching (IndexedDB)

4. **Run Comprehensive Tests**:
   ```bash
   # All mobile tests
   poetry run pytest tests/e2e/ --project="Mobile Chrome" -v

   # Visual regression (optional)
   npx percy exec -- pytest tests/e2e/test_mobile_workflows.py
   ```

---

## Reference Documentation

- **Plan**: `specs/008-mobile-responsive-design/plan.md`
- **Research**: `specs/008-mobile-responsive-design/research.md`
- **Data Model**: `specs/008-mobile-responsive-design/data-model.md`
- **Contracts**: `specs/008-mobile-responsive-design/contracts/`
- **Playwright Docs**: https://playwright.dev/python/docs/emulation
- **Hammer.js Docs**: http://hammerjs.github.io/

---

**Time to Complete**: 10 minutes
**Last Updated**: 2025-10-23
**Feature**: 018 - Mobile Responsive Design
