# Research: Mobile Responsive Design Technology Decisions

**Feature**: Mobile Responsive Design | **Branch**: `008-mobile-responsive-design` | **Date**: 2025-10-23

This document captures research and technology decisions for implementing mobile-responsive design in SignUpFlow. Each decision includes rationale, alternatives considered, and implementation guidance.

---

## Decision 1: CSS Framework vs Vanilla CSS

### Problem Statement

Choose responsive CSS approach: full framework (Bootstrap, Tailwind), utility-first framework, or custom vanilla CSS with media queries.

### Options Evaluated

#### Option A: Bootstrap 5 (Component Framework)
**Pros**:
- Pre-built responsive components (navbar, cards, forms)
- Proven mobile-first grid system (12-column)
- Extensive documentation and community
- Built-in accessibility features
- ~25KB gzipped (CSS only)

**Cons**:
- Learning curve for team unfamiliar with Bootstrap
- Opinionated design system (requires customization)
- Bundle size overhead (~60KB including JS)
- May conflict with existing SignUpFlow styles
- JavaScript dependency for interactive components

**Bundle Analysis**: 25KB CSS + 18KB JS (gzipped) = 43KB total

#### Option B: Tailwind CSS (Utility-First)
**Pros**:
- Highly customizable via config
- No pre-built components (full design control)
- PurgeCSS removes unused styles (can be <10KB)
- Mobile-first by default
- No JavaScript required

**Cons**:
- Requires build process (PostCSS)
- Verbose HTML (many utility classes)
- Team learning curve
- Harder to maintain consistency
- Requires additional tooling setup

**Bundle Analysis**: ~8-15KB (after purge) for typical application

#### Option C: Custom Vanilla CSS (Media Queries) ✅ SELECTED
**Pros**:
- Zero dependencies, zero bundle overhead
- Full control over breakpoints and behavior
- Team already familiar with vanilla CSS
- No build process changes required
- Matches existing SignUpFlow architecture (no framework)
- Progressive enhancement friendly

**Cons**:
- Must write all responsive logic manually
- No pre-built components
- Potentially more code to maintain
- Requires discipline for consistency

**Bundle Analysis**: ~15-20KB custom CSS (application-specific, no framework overhead)

### Decision

**Selected**: **Option C - Custom Vanilla CSS with Media Queries**

**Rationale**:
1. **Architecture Alignment**: SignUpFlow uses Vanilla JS (no framework) - adding CSS framework creates inconsistency
2. **Bundle Size**: Custom CSS is actually smaller (15-20KB vs 43KB Bootstrap, similar to Tailwind after purge)
3. **Learning Curve**: Team already knows CSS, no new framework to learn
4. **Control**: Full control over breakpoints, no fighting framework defaults
5. **Progressive Enhancement**: Works without JavaScript (Bootstrap navbar requires JS)

**Implementation Pattern**:
```css
/* Mobile-first base styles */
.schedule-card {
    padding: 1rem;
    font-size: 14px;
}

/* Tablet (768px+) */
@media (min-width: 768px) {
    .schedule-card {
        padding: 1.5rem;
        font-size: 16px;
    }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
    .schedule-card {
        padding: 2rem;
        display: grid;
        grid-template-columns: 1fr 2fr;
    }
}
```

**Breakpoint Strategy**:
```css
/* Custom properties for consistency */
:root {
    --breakpoint-mobile: 320px;
    --breakpoint-tablet: 768px;
    --breakpoint-desktop: 1024px;
    --breakpoint-wide: 1440px;
}
```

---

## Decision 2: Touch Gesture Library Selection

### Problem Statement

Choose touch gesture handling: native Pointer Events API, Hammer.js library, or custom touch event handlers.

### Options Evaluated

#### Option A: Pointer Events API (Native)
**Pros**:
- Zero dependencies, native browser support
- Unified API for touch/mouse/pen input
- Good browser support (95%+ globally)
- Most performant (no library overhead)

**Cons**:
- More boilerplate for complex gestures
- Must implement swipe/pinch logic manually
- ~100-200 LOC for gesture detection
- No pre-built gesture recognition

**Implementation Complexity**: Medium (custom gesture detection required)

#### Option B: Hammer.js 2.0 ✅ SELECTED
**Pros**:
- Industry-standard gesture library
- Pre-built recognizers (swipe, pinch, pan, rotate)
- Configurable thresholds and directions
- ~7.3KB gzipped
- Used by major apps (Google Inbox, Pinterest mobile)

**Cons**:
- Additional dependency (7.3KB)
- Not maintained as actively (last release 2019)
- Overkill for simple tap handling

**Bundle Analysis**: 7.3KB gzipped, 24KB uncompressed

#### Option C: Custom Touch Event Handlers
**Pros**:
- Zero dependencies
- Minimal code for simple gestures
- Full control over behavior

**Cons**:
- Must handle touch quirks across browsers
- ~150-300 LOC for swipe/pinch/long-press
- Testing burden (many edge cases)
- Reinventing the wheel

**Implementation Complexity**: High (2-3 weeks for robust implementation)

### Decision

**Selected**: **Option B - Hammer.js 2.0**

**Rationale**:
1. **Development Velocity**: Pre-built gesture recognizers save 2-3 weeks vs custom implementation
2. **Bundle Size Acceptable**: 7.3KB gzipped is reasonable for robust gesture handling
3. **Production-Proven**: Used by major mobile web apps, well-tested
4. **Feature Requirements**: SignUpFlow needs swipe navigation (calendar, schedule tabs), pinch-zoom (calendar view), long-press (context menus)
5. **Maintenance**: Despite inactive maintenance, library is stable and complete (no breaking changes needed)

**Usage Pattern**:
```javascript
import Hammer from 'hammerjs';

// Swipe navigation on schedule view
const scheduleView = document.getElementById('schedule-view');
const hammer = new Hammer(scheduleView);

hammer.on('swipeleft', () => {
    navigateToNextWeek();
});

hammer.on('swiperight', () => {
    navigateToPreviousWeek();
});

// Pinch-zoom on calendar
const calendar = document.getElementById('calendar');
const hammerCalendar = new Hammer(calendar);
hammerCalendar.get('pinch').set({ enable: true });

hammerCalendar.on('pinchstart pinchmove', (ev) => {
    const scale = Math.max(0.5, Math.min(ev.scale, 2));
    calendar.style.transform = `scale(${scale})`;
});
```

**Configuration**:
```javascript
// Global Hammer configuration
Hammer.defaults.cssProps.userSelect = 'auto'; // Allow text selection
Hammer.defaults.inputClass = Hammer.TouchInput; // Touch-only (no mouse emulation)
```

---

## Decision 3: PWA Pattern Selection

### Problem Statement

Choose Progressive Web App implementation: Workbox (abstraction layer) or manual service worker with custom caching logic.

### Options Evaluated

#### Option A: Workbox 7 ✅ SELECTED
**Pros**:
- Abstraction over Service Worker API
- Pre-built caching strategies (CacheFirst, NetworkFirst, StaleWhileRevalidate)
- Background sync for offline actions
- Google-maintained, industry standard
- ~15KB gzipped (runtime)
- Webpack/Rollup plugins available

**Cons**:
- Additional dependency (15KB)
- Abstraction hides some Service Worker details
- Requires build step for precaching manifest

**Bundle Analysis**: 15KB runtime + 5KB precache manifest = 20KB total

#### Option B: Manual Service Worker
**Pros**:
- Zero dependencies
- Full control over caching logic
- Educational value (deeper understanding)

**Cons**:
- ~500-1000 LOC for robust implementation
- Must handle cache versioning manually
- Background sync requires complex code
- Higher maintenance burden
- More bugs (Service Worker API has many edge cases)

**Implementation Complexity**: High (3-4 weeks for production-ready)

### Decision

**Selected**: **Option A - Workbox 7**

**Rationale**:
1. **Development Velocity**: Workbox provides production-ready PWA in 2-3 days vs 3-4 weeks manual
2. **Best Practices**: Workbox encapsulates Google's PWA best practices
3. **Caching Strategies**: Pre-built strategies cover 95% of use cases
4. **Bundle Size**: 15KB is acceptable for robust offline functionality
5. **Maintenance**: Google-maintained, regular updates for new Service Worker features

**Caching Strategy**:
```javascript
// workbox-config.js
module.exports = {
    // Precache static assets
    globDirectory: 'frontend/',
    globPatterns: [
        '**/*.{html,js,css,png,jpg,svg,woff2}'
    ],
    swDest: 'frontend/service-worker.js',

    // Runtime caching rules
    runtimeCaching: [
        {
            urlPattern: /^https:\/\/localhost:8000\/api\/people\/me/,
            handler: 'NetworkFirst', // Always try network, fallback to cache
            options: {
                cacheName: 'user-data',
                expiration: {
                    maxAgeSeconds: 300 // 5 minutes
                }
            }
        },
        {
            urlPattern: /^https:\/\/localhost:8000\/api\/events/,
            handler: 'StaleWhileRevalidate', // Use cache, update in background
            options: {
                cacheName: 'events-data',
                expiration: {
                    maxEntries: 50,
                    maxAgeSeconds: 3600 // 1 hour
                }
            }
        },
        {
            urlPattern: /^https:\/\/localhost:8000\/api\/availability/,
            handler: 'NetworkFirst',
            options: {
                cacheName: 'availability-data',
                expiration: {
                    maxAgeSeconds: 600 // 10 minutes
                }
            }
        }
    ]
};
```

**Background Sync**:
```javascript
import { BackgroundSyncPlugin } from 'workbox-background-sync';

const bgSyncPlugin = new BackgroundSyncPlugin('availability-queue', {
    maxRetentionTime: 24 * 60 // Retry for 24 hours
});

registerRoute(
    /^https:\/\/localhost:8000\/api\/availability/,
    new NetworkOnly({
        plugins: [bgSyncPlugin]
    }),
    'POST'
);
```

---

## Decision 4: Offline Data Strategy

### Problem Statement

Choose offline data storage: IndexedDB (structured data), localStorage (key-value), or cache-only (no structured storage).

### Options Evaluated

#### Option A: IndexedDB ✅ SELECTED
**Pros**:
- Structured storage with indexes/queries
- Large storage limits (50MB+, can request more)
- Async API (non-blocking)
- Transactional (ACID properties)
- Can store complex objects (events, schedules, people)

**Cons**:
- Complex API (Workbox helps abstract)
- Requires schema design
- More code than localStorage

**Storage Limits**: 50MB-1GB (varies by browser)

#### Option B: localStorage
**Pros**:
- Simple key-value API
- Synchronous (easy to use)
- 5-10MB storage

**Cons**:
- Synchronous (blocks main thread)
- Limited storage (5-10MB)
- String-only (must JSON.stringify)
- No query capabilities
- Too small for schedule data

**Storage Limits**: 5-10MB (insufficient for 200+ events)

#### Option C: Cache-Only (No Structured Storage)
**Pros**:
- Simplest implementation
- Workbox handles automatically

**Cons**:
- No offline data manipulation
- Can't queue actions offline
- Cache is HTTP-only (can't store computed data)

### Decision

**Selected**: **Option A - IndexedDB**

**Rationale**:
1. **Data Requirements**: Need to store 200+ events, 50+ people, availability records (exceeds localStorage 5MB limit)
2. **Querying**: Need to filter events by date, person, role (IndexedDB indexes support this)
3. **Async**: Non-blocking API critical for mobile performance
4. **Background Sync**: Can queue offline actions (add availability, update profile) and sync when online
5. **Workbox Integration**: Workbox provides simple IndexedDB abstraction

**Schema Design**:
```javascript
// IndexedDB schema via idb library (Workbox compatible)
import { openDB } from 'idb';

const db = await openDB('signupflow-offline', 1, {
    upgrade(db) {
        // Events store
        const eventsStore = db.createObjectStore('events', { keyPath: 'id' });
        eventsStore.createIndex('datetime', 'datetime');
        eventsStore.createIndex('org_id', 'org_id');

        // People store
        const peopleStore = db.createObjectStore('people', { keyPath: 'id' });
        peopleStore.createIndex('org_id', 'org_id');

        // Availability store
        const availStore = db.createObjectStore('availability', { keyPath: 'id' });
        availStore.createIndex('person_id', 'person_id');
        availStore.createIndex('start_date', 'start_date');

        // Assignments store
        const assignStore = db.createObjectStore('assignments', { keyPath: 'id' });
        assignStore.createIndex('event_id', 'event_id');
        assignStore.createIndex('person_id', 'person_id');

        // Pending actions (offline queue)
        const pendingStore = db.createObjectStore('pending_actions', {
            keyPath: 'id',
            autoIncrement: true
        });
        pendingStore.createIndex('timestamp', 'timestamp');
    }
});
```

**Sync Strategy**:
```javascript
// Sync IndexedDB with backend on reconnect
async function syncOfflineData() {
    const db = await openDB('signupflow-offline', 1);
    const pendingActions = await db.getAll('pending_actions');

    for (const action of pendingActions) {
        try {
            // Replay action against backend
            await authFetch(action.endpoint, {
                method: action.method,
                body: JSON.stringify(action.data)
            });

            // Remove from queue on success
            await db.delete('pending_actions', action.id);
        } catch (error) {
            // Keep in queue, retry later
            console.log('Sync failed, will retry:', error);
        }
    }
}

// Listen for online event
window.addEventListener('online', syncOfflineData);
```

---

## Decision 5: Mobile Navigation Patterns

### Problem Statement

Choose mobile navigation pattern: bottom navigation bar, hamburger menu, tab bar, or hybrid approach.

### Options Evaluated

#### Option A: Bottom Navigation Bar
**Pros**:
- Thumb-reachable on large phones (one-handed use)
- Industry standard (iOS/Android guidelines)
- Always visible (no tapping to reveal)
- 3-5 primary actions

**Cons**:
- Takes vertical space (48px)
- Limited to 5 items max
- Less space for content

**Use Case**: Primary navigation (Home, Schedule, Availability, Profile)

#### Option B: Hamburger Menu (Slide-out Drawer)
**Pros**:
- Saves screen space (hidden until opened)
- Can hold many items (10+)
- Common pattern (users familiar)

**Cons**:
- Hidden (requires tap to reveal)
- Poor discoverability for new users
- Requires extra tap to navigate

**Use Case**: Secondary navigation, settings, logout

#### Option C: Tab Bar (Top)
**Pros**:
- Horizontal layout fits many tabs
- Swipeable tabs (nice UX)

**Cons**:
- Hard to reach on large phones (top of screen)
- Conflicts with browser chrome
- Not recommended by iOS/Android guidelines

**Use Case**: Sub-navigation within views

#### Option D: Hybrid Approach ✅ SELECTED
**Pros**:
- Combines best of all patterns
- Bottom nav for primary (4 items)
- Hamburger for secondary (settings, logout)
- Tabs for sub-navigation (schedule views: week/month)

**Cons**:
- More complex implementation
- Requires consistency across views

### Decision

**Selected**: **Option D - Hybrid Approach**

**Rationale**:
1. **Usability**: Bottom nav for frequent actions (schedule, availability), hamburger for occasional (settings, logout)
2. **Information Architecture**: SignUpFlow has 4 primary sections (perfect for bottom nav) + secondary actions (hamburger)
3. **Industry Standard**: iOS and Android both use this pattern
4. **Accessibility**: Bottom nav is thumb-reachable (44px tap targets), hamburger has clear affordance

**Navigation Structure**:
```
Bottom Navigation (4 items, always visible):
├── Schedule (Home)
├── Events
├── Availability
└── Profile

Hamburger Menu (slide-out from left, hidden by default):
├── Settings
├── Teams
├── Help
├── Admin Console (if admin role)
└── Logout

Tabs (within views, swipeable):
└── Schedule view:
    ├── Week
    ├── Month
    └── List
```

**Implementation**:
```html
<!-- Bottom Navigation -->
<nav class="bottom-nav" role="navigation" aria-label="Primary navigation">
    <button class="bottom-nav-item" data-route="/app/schedule" aria-label="Schedule">
        <svg class="icon">...</svg>
        <span>Schedule</span>
    </button>
    <button class="bottom-nav-item" data-route="/app/events" aria-label="Events">
        <svg class="icon">...</svg>
        <span>Events</span>
    </button>
    <button class="bottom-nav-item" data-route="/app/availability" aria-label="Availability">
        <svg class="icon">...</svg>
        <span>Availability</span>
    </button>
    <button class="bottom-nav-item" data-route="/app/profile" aria-label="Profile">
        <svg class="icon">...</svg>
        <span>Profile</span>
    </button>
</nav>

<!-- Hamburger Menu -->
<button class="hamburger-toggle" aria-label="Open menu" aria-expanded="false">
    <span class="hamburger-icon"></span>
</button>

<aside class="hamburger-menu" role="navigation" aria-label="Secondary navigation" hidden>
    <nav>
        <a href="/app/settings">Settings</a>
        <a href="/app/teams">Teams</a>
        <a href="/app/help">Help</a>
        <a href="/app/admin" data-if-role="admin">Admin Console</a>
        <button id="logout-button">Logout</button>
    </nav>
</aside>
```

**CSS**:
```css
/* Bottom Navigation */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 56px;
    display: flex;
    background: var(--bg-surface);
    border-top: 1px solid var(--border-color);
    z-index: 1000;
    padding-bottom: env(safe-area-inset-bottom); /* iOS notch */
}

.bottom-nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 44px; /* WCAG touch target */
    min-height: 44px;
    gap: 4px;
    font-size: 12px;
}

/* Hamburger Menu */
.hamburger-menu {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 280px;
    background: var(--bg-surface);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 2000;
    box-shadow: 2px 0 8px rgba(0,0,0,0.2);
}

.hamburger-menu[aria-hidden="false"] {
    transform: translateX(0);
}

/* Mobile: Hide desktop nav, show bottom nav */
@media (max-width: 767px) {
    .desktop-nav { display: none; }
    .bottom-nav { display: flex; }
}

/* Desktop: Show desktop nav, hide bottom nav */
@media (min-width: 768px) {
    .desktop-nav { display: flex; }
    .bottom-nav { display: none; }
}
```

---

## Decision 6: Performance Optimization Approach

### Problem Statement

Choose performance optimization strategy: code splitting, lazy loading, compression, or combination.

### Optimization Techniques Evaluated

#### Technique A: Code Splitting (Route-Based)
**Benefit**: Load only code for current route
**Implementation**: Dynamic imports for each route
**Savings**: ~60% reduction in initial bundle (120KB → 48KB)

**Example**:
```javascript
// router.js - lazy load route modules
const routes = {
    '/app/schedule': () => import('./schedule.js'),
    '/app/events': () => import('./events.js'),
    '/app/availability': () => import('./availability.js')
};

async function loadRoute(path) {
    const module = await routes[path]();
    module.init();
}
```

#### Technique B: Lazy Loading Images
**Benefit**: Defer offscreen image loading
**Implementation**: Intersection Observer API
**Savings**: ~40% reduction in initial page load time

**Example**:
```javascript
const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            imageObserver.unobserve(img);
        }
    });
});

document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
});
```

#### Technique C: Gzip/Brotli Compression
**Benefit**: Reduce transfer size
**Implementation**: Server configuration (Uvicorn/nginx)
**Savings**: ~70% reduction in transfer size (120KB → 36KB)

**Example** (Uvicorn):
```python
import uvicorn

uvicorn.run(
    "api.main:app",
    host="0.0.0.0",
    port=8000,
    # Enable compression
    compression="gzip",
    compression_level=6
)
```

#### Technique D: Critical CSS Inlining
**Benefit**: Eliminate render-blocking CSS
**Implementation**: Inline critical CSS in <head>, defer rest
**Savings**: ~1-2s improvement in First Contentful Paint

**Example**:
```html
<head>
    <!-- Inline critical CSS (above-the-fold) -->
    <style>
        /* Mobile layout, typography, colors */
        body { font-family: system-ui; margin: 0; }
        .header { height: 56px; background: #fff; }
    </style>

    <!-- Defer non-critical CSS -->
    <link rel="preload" href="/css/styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="/css/styles.css"></noscript>
</head>
```

### Decision

**Selected**: **Combination of All Techniques** ✅

**Rationale**:
1. **Code Splitting**: 60% bundle reduction critical for mobile (3G connections)
2. **Lazy Loading**: 40% page load improvement with minimal effort
3. **Compression**: 70% transfer size reduction with zero code changes (server config)
4. **Critical CSS**: 1-2s FCP improvement for mobile (most impactful metric)

**Performance Budget**:
```json
{
    "budget": [
        {
            "path": "/*",
            "timings": [
                {
                    "metric": "first-contentful-paint",
                    "budget": 2000
                },
                {
                    "metric": "interactive",
                    "budget": 5000
                },
                {
                    "metric": "speed-index",
                    "budget": 3500
                }
            ],
            "resourceSizes": [
                {
                    "resourceType": "script",
                    "budget": 150
                },
                {
                    "resourceType": "stylesheet",
                    "budget": 50
                },
                {
                    "resourceType": "image",
                    "budget": 200
                },
                {
                    "resourceType": "total",
                    "budget": 500
                }
            ]
        }
    ]
}
```

**Lighthouse CI Configuration**:
```json
{
    "ci": {
        "collect": {
            "url": ["http://localhost:8000/"],
            "numberOfRuns": 3,
            "settings": {
                "emulatedFormFactor": "mobile",
                "throttling": {
                    "rttMs": 150,
                    "throughputKbps": 1638.4,
                    "cpuSlowdownMultiplier": 4
                }
            }
        },
        "assert": {
            "preset": "lighthouse:recommended",
            "assertions": {
                "first-contentful-paint": ["error", {"maxNumericValue": 3000}],
                "interactive": ["error", {"maxNumericValue": 5000}],
                "speed-index": ["error", {"maxNumericValue": 4000}],
                "performance-budget": ["error", {"maxNumericValue": 0}]
            }
        }
    }
}
```

---

## Decision 7: Testing Strategy

### Problem Statement

Choose mobile testing approach: device lab (real devices), emulators (Playwright/BrowserStack), or cloud testing service.

### Options Evaluated

#### Option A: Playwright Mobile Emulation ✅ SELECTED
**Pros**:
- Included with existing Playwright setup (zero new cost)
- Fast test execution (<5s per test)
- Emulates touch events, viewport, user agent
- Integrates with CI/CD pipeline
- Good for functional testing

**Cons**:
- Not real devices (may miss device-specific bugs)
- No GPU/hardware emulation
- Limited to Chromium rendering

**Cost**: $0 (already using Playwright)

#### Option B: BrowserStack (Cloud Testing)
**Pros**:
- Real devices (1000+ iOS/Android devices)
- Tests actual hardware behavior
- Automated testing on multiple devices
- Screenshots/video recording

**Cons**:
- $99-$199/month (paid service)
- Slower test execution (~30s per test)
- Requires network connection
- Adds complexity to CI/CD

**Cost**: $99-$199/month

#### Option C: Physical Device Lab
**Pros**:
- Real devices under full control
- No subscription costs (one-time purchase)
- Tests actual hardware

**Cons**:
- Expensive upfront ($2000-$5000 for 10 devices)
- Maintenance burden (OS updates, charging)
- Manual testing (hard to automate)
- Space requirements

**Cost**: $2000-$5000 upfront + maintenance

### Decision

**Selected**: **Option A - Playwright Mobile Emulation** (primary) + **Option B - BrowserStack** (pre-release validation)

**Rationale**:
1. **Development Testing**: Playwright emulation for rapid iteration (CI/CD, developer testing)
2. **Pre-Release Validation**: BrowserStack for real device testing before major releases (quarterly)
3. **Cost-Effective**: $0 daily (Playwright) + $99/month BrowserStack (pay-as-needed) vs $2000+ device lab
4. **CI/CD Integration**: Playwright runs in GitHub Actions (automated), BrowserStack for manual validation

**Playwright Configuration**:
```javascript
// playwright.config.js
module.exports = {
    projects: [
        {
            name: 'Mobile Chrome',
            use: {
                ...devices['Pixel 5'],
                viewport: { width: 393, height: 851 },
                userAgent: 'Mozilla/5.0 (Linux; Android 11; Pixel 5) ...',
                hasTouch: true,
                isMobile: true
            }
        },
        {
            name: 'Mobile Safari',
            use: {
                ...devices['iPhone 13'],
                viewport: { width: 390, height: 844 },
                userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) ...',
                hasTouch: true,
                isMobile: true
            }
        },
        {
            name: 'Tablet',
            use: {
                ...devices['iPad Pro'],
                viewport: { width: 1024, height: 1366 },
                hasTouch: true,
                isMobile: false
            }
        }
    ]
};
```

**Test Examples**:
```python
# tests/e2e/test_mobile_workflows.py
def test_schedule_view_mobile(page: Page):
    """Test schedule view on mobile device."""
    page.goto("http://localhost:8000/app/schedule")

    # Verify bottom navigation visible
    expect(page.locator('.bottom-nav')).to_be_visible()

    # Verify desktop nav hidden
    expect(page.locator('.desktop-nav')).to_be_hidden()

    # Test swipe navigation
    schedule = page.locator('#schedule-view')
    schedule.swipe_left()  # Playwright touch gesture

    # Verify next week loaded
    expect(page.locator('h2[data-i18n="schedule.next_week"]')).to_be_visible()

def test_touch_targets_minimum_size(page: Page):
    """Test all interactive elements meet 44x44px minimum (WCAG)."""
    page.goto("http://localhost:8000/app/schedule")

    buttons = page.locator('button, a, input[type="checkbox"]').all()

    for button in buttons:
        box = button.bounding_box()
        assert box['width'] >= 44, f"Button {button} width {box['width']}px < 44px"
        assert box['height'] >= 44, f"Button {button} height {box['height']}px < 44px"
```

**BrowserStack Integration** (pre-release only):
```yaml
# .github/workflows/browserstack.yml (run manually before releases)
name: BrowserStack Mobile Testing

on:
  workflow_dispatch:  # Manual trigger only

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run BrowserStack Tests
        env:
          BROWSERSTACK_USERNAME: ${{ secrets.BROWSERSTACK_USERNAME }}
          BROWSERSTACK_ACCESS_KEY: ${{ secrets.BROWSERSTACK_ACCESS_KEY }}
        run: |
          npx playwright test --config=playwright.browserstack.config.js
```

---

## Decision 8: Responsive Image Strategy

### Problem Statement

Choose responsive image approach: `srcset` attribute, `<picture>` element with media queries, or CSS `background-image` with media queries.

### Options Evaluated

#### Option A: `srcset` with Sizes ✅ SELECTED
**Pros**:
- Native browser feature (no JS)
- Automatic DPR handling (Retina displays)
- Simplest syntax for resolution switching

**Cons**:
- Limited art direction (can't crop differently)
- Requires server-side image resizing

**Example**:
```html
<img
    src="/images/event-small.jpg"
    srcset="
        /images/event-small.jpg 400w,
        /images/event-medium.jpg 800w,
        /images/event-large.jpg 1200w
    "
    sizes="
        (max-width: 767px) 100vw,
        (max-width: 1023px) 50vw,
        33vw
    "
    alt="Event thumbnail">
```

#### Option B: `<picture>` Element
**Pros**:
- Full art direction control (different crops)
- Media query support
- Fallback image for old browsers

**Cons**:
- More verbose markup
- Requires multiple image versions
- Overkill for simple resolution switching

**Example**:
```html
<picture>
    <source media="(max-width: 767px)" srcset="/images/event-mobile.jpg">
    <source media="(max-width: 1023px)" srcset="/images/event-tablet.jpg">
    <img src="/images/event-desktop.jpg" alt="Event thumbnail">
</picture>
```

#### Option C: CSS Background Images
**Pros**:
- No HTML changes
- Media query control

**Cons**:
- Not accessible (no alt text)
- Blocks page rendering (CSS-dependent)
- Hard to lazy load

### Decision

**Selected**: **Option A - `srcset` with Sizes** (primary) + **Option B - `<picture>`** (for hero images with art direction)

**Rationale**:
1. **Simplicity**: `srcset` covers 90% of cases (thumbnails, event images, profile photos)
2. **Performance**: Browser automatically selects optimal image (DPR + viewport)
3. **Accessibility**: Works with `alt` text (unlike CSS backgrounds)
4. **Art Direction**: Use `<picture>` only for hero images needing different crops (login screen, onboarding)

**Image Sizing Strategy**:
```
Small (mobile): 400px wide (for 320-767px viewports)
Medium (tablet): 800px wide (for 768-1023px viewports)
Large (desktop): 1200px wide (for 1024px+ viewports)

Retina support: Browser automatically requests 2x if needed (srcset handles)
```

**Server-Side Resizing** (FastAPI endpoint):
```python
# api/routers/images.py
from PIL import Image
from fastapi.responses import StreamingResponse

@router.get("/images/{image_id}")
async def get_image(image_id: str, width: int = 400):
    """Resize image on-the-fly based on width parameter."""
    image_path = f"uploads/{image_id}.jpg"

    img = Image.open(image_path)
    img.thumbnail((width, width * img.height // img.width))

    # Return resized image
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/jpeg")
```

**Usage Pattern**:
```html
<!-- Event thumbnails (resolution switching) -->
<img
    src="/api/images/event_123?width=400"
    srcset="
        /api/images/event_123?width=400 400w,
        /api/images/event_123?width=800 800w,
        /api/images/event_123?width=1200 1200w
    "
    sizes="(max-width: 767px) 100vw, (max-width: 1023px) 50vw, 33vw"
    loading="lazy"
    alt="Sunday Service Event">

<!-- Hero image (art direction - different crops) -->
<picture>
    <source
        media="(max-width: 767px)"
        srcset="/api/images/hero_mobile_123?width=767">
    <source
        media="(max-width: 1023px)"
        srcset="/api/images/hero_tablet_123?width=1023">
    <img
        src="/api/images/hero_desktop_123?width=1920"
        alt="Welcome to SignUpFlow">
</picture>
```

---

## Summary of Decisions

| Decision | Selected Option | Key Benefit | Bundle Impact |
|----------|----------------|-------------|---------------|
| CSS Framework | Vanilla CSS | No dependencies, full control | 0 KB (vs +43KB Bootstrap) |
| Touch Gestures | Hammer.js 2.0 | Production-proven, saves 2-3 weeks | +7.3KB |
| PWA Implementation | Workbox 7 | Industry standard, saves 3-4 weeks | +15KB |
| Offline Storage | IndexedDB | 50MB+ capacity, async, queryable | 0 KB (native API) |
| Navigation Pattern | Hybrid (Bottom Nav + Hamburger) | Best usability, industry standard | +2KB |
| Performance | All techniques (split, lazy, compress, critical CSS) | 60-70% improvements | -50KB (net savings) |
| Testing | Playwright (primary) + BrowserStack (validation) | Fast CI/CD + real device validation | $99/month |
| Responsive Images | `srcset` + `<picture>` | Automatic DPR, art direction | 0 KB (native) |

**Total Bundle Impact**: +24.3KB (Hammer.js + Workbox) - 50KB (optimizations) = **-25.7KB net savings**

**Performance Targets** (Lighthouse Mobile):
- Performance Score: >90
- First Contentful Paint: <3s on 3G
- Time to Interactive: <5s on 3G
- Cumulative Layout Shift: <0.1
- Total Bundle Size: <500KB

---

## Implementation Priorities

**Phase 1: Responsive Layouts** (Week 1)
1. Mobile-first CSS with 3 breakpoints
2. Touch-optimized UI (44px tap targets)
3. Bottom navigation + hamburger menu
4. Responsive images with `srcset`

**Phase 2: PWA Capabilities** (Week 2)
1. Workbox service worker setup
2. Offline caching strategies
3. IndexedDB schema for offline data
4. Background sync for queued actions

**Phase 3: Performance Optimization** (Week 3)
1. Code splitting by route
2. Lazy loading images
3. Critical CSS inlining
4. Gzip/Brotli compression

**Phase 4: Testing & Validation** (Week 4)
1. Playwright mobile tests (CI/CD)
2. Lighthouse CI integration
3. BrowserStack validation (real devices)
4. Accessibility audit (WCAG 2.1 AA)

---

**Last Updated**: 2025-10-23
**Feature**: 018 - Mobile Responsive Design
**Total Research Time**: ~8 hours
