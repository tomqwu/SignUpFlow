# API Contract: Touch Gesture Patterns

**Feature**: Mobile Responsive Design | **Version**: 1.0.0 | **Date**: 2025-10-23

## Overview

This contract defines touch gesture implementations using Hammer.js for SignUpFlow's mobile interface. Gestures enable natural mobile interactions like swipe navigation, pinch-zoom, and long-press context menus.

**Library**: Hammer.js 2.0.17+
**Bundle Size**: 7.3KB gzipped
**Browser Support**: iOS Safari 10+, Android Chrome 55+, modern mobile browsers

---

## Gesture Types

### 1. Swipe (Horizontal Navigation)

**Use Case**: Navigate between weeks/months in schedule view, swipe between tabs

**Configuration**:
```javascript
import Hammer from 'hammerjs';

const scheduleView = document.getElementById('schedule-view');
const hammer = new Hammer(scheduleView);

// Enable swipe detection
hammer.get('swipe').set({ direction: Hammer.DIRECTION_HORIZONTAL });

// Swipe left (next week)
hammer.on('swipeleft', (event) => {
    navigateToNextWeek();
    hapticFeedback('light');
});

// Swipe right (previous week)
hammer.on('swiperight', (event) => {
    navigateToPreviousWeek();
    hapticFeedback('light');
});
```

**Parameters**:
```javascript
hammer.get('swipe').set({
    direction: Hammer.DIRECTION_HORIZONTAL,
    threshold: 50,      // Minimum distance (px) to trigger swipe
    velocity: 0.3       // Minimum velocity (px/ms)
});
```

**Visual Feedback**:
```css
/* Show swipe progress indicator */
.swipe-progress {
    position: fixed;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0;
    transition: opacity 0.2s;
}

.swipe-progress.active {
    opacity: 1;
}

.swipe-progress.left {
    right: 20px;
}

.swipe-progress.right {
    left: 20px;
}
```

---

### 2. Pan (Drag/Pull to Refresh)

**Use Case**: Pull-to-refresh on schedule list, drag bottom sheet

**Configuration**:
```javascript
const scheduleList = document.getElementById('schedule-list');
const hammer = new Hammer(scheduleList);

let pullDistance = 0;
const pullThreshold = 80; // px to trigger refresh

hammer.on('panstart', (event) => {
    // Only pull down from top of list
    if (scheduleList.scrollTop === 0) {
        pullDistance = 0;
    }
});

hammer.on('panmove', (event) => {
    if (scheduleList.scrollTop === 0 && event.deltaY > 0) {
        pullDistance = Math.min(event.deltaY, pullThreshold * 1.5);

        // Update pull indicator
        const indicator = document.getElementById('pull-indicator');
        indicator.style.transform = `translateY(${pullDistance}px)`;

        // Change icon when threshold reached
        if (pullDistance >= pullThreshold) {
            indicator.classList.add('ready');
        } else {
            indicator.classList.remove('ready');
        }
    }
});

hammer.on('panend', (event) => {
    if (pullDistance >= pullThreshold) {
        // Trigger refresh
        refreshSchedule();
        hapticFeedback('medium');
    }

    // Reset indicator
    const indicator = document.getElementById('pull-indicator');
    indicator.style.transform = '';
    indicator.classList.remove('ready');
    pullDistance = 0;
});
```

**Visual Feedback**:
```html
<div id="pull-indicator" class="pull-indicator">
    <svg class="icon-refresh">...</svg>
    <span>Pull to refresh</span>
</div>
```

```css
.pull-indicator {
    position: absolute;
    top: -80px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    transition: transform 0.3s ease;
}

.pull-indicator.ready .icon-refresh {
    transform: rotate(180deg);
}
```

---

### 3. Pinch (Zoom Calendar)

**Use Case**: Pinch-zoom calendar to see more/fewer days

**Configuration**:
```javascript
const calendar = document.getElementById('calendar');
const hammer = new Hammer(calendar);

// Enable pinch gesture
hammer.get('pinch').set({ enable: true });

let currentScale = 1;
const minScale = 0.5;
const maxScale = 2;

hammer.on('pinchstart', (event) => {
    calendar.dataset.initialScale = currentScale;
});

hammer.on('pinchmove', (event) => {
    const initialScale = parseFloat(calendar.dataset.initialScale || 1);
    const newScale = Math.max(minScale, Math.min(initialScale * event.scale, maxScale));

    calendar.style.transform = `scale(${newScale})`;
    calendar.style.transformOrigin = 'center';
});

hammer.on('pinchend', (event) => {
    const initialScale = parseFloat(calendar.dataset.initialScale || 1);
    currentScale = Math.max(minScale, Math.min(initialScale * event.scale, maxScale));

    // Snap to zoom levels
    if (currentScale < 0.75) {
        currentScale = 0.5; // Month view
    } else if (currentScale < 1.25) {
        currentScale = 1.0; // Week view
    } else {
        currentScale = 2.0; // Day view
    }

    calendar.style.transform = `scale(${currentScale})`;
    calendar.style.transition = 'transform 0.3s ease';

    hapticFeedback('medium');

    // Remove transition after animation
    setTimeout(() => {
        calendar.style.transition = '';
    }, 300);
});
```

---

### 4. Long Press (Context Menu)

**Use Case**: Long-press event card to show context menu (edit, delete, copy)

**Configuration**:
```javascript
const eventCards = document.querySelectorAll('.event-card');

eventCards.forEach(card => {
    const hammer = new Hammer(card);

    // Enable long press (press & hold)
    hammer.get('press').set({ time: 500 }); // 500ms hold

    hammer.on('press', (event) => {
        const eventId = card.dataset.eventId;
        showContextMenu(event.center.x, event.center.y, eventId);
        hapticFeedback('heavy');
    });
});
```

**Context Menu Implementation**:
```javascript
function showContextMenu(x, y, eventId) {
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.innerHTML = `
        <button data-action="edit">Edit</button>
        <button data-action="delete">Delete</button>
        <button data-action="copy">Duplicate</button>
        <button data-action="cancel">Cancel</button>
    `;

    // Position near touch point
    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;

    document.body.appendChild(menu);

    // Handle menu actions
    menu.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', () => {
            const action = button.dataset.action;

            if (action === 'edit') {
                editEvent(eventId);
            } else if (action === 'delete') {
                deleteEvent(eventId);
            } else if (action === 'copy') {
                duplicateEvent(eventId);
            }

            menu.remove();
        });
    });

    // Close menu on outside click
    setTimeout(() => {
        document.addEventListener('click', () => menu.remove(), { once: true });
    }, 100);
}
```

```css
.context-menu {
    position: fixed;
    background: var(--bg-surface);
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    padding: 0.5rem 0;
    min-width: 200px;
    z-index: 3000;
    transform: translate(-50%, -100%) translateY(-10px);
}

.context-menu button {
    display: block;
    width: 100%;
    padding: 0.75rem 1rem;
    text-align: left;
    border: none;
    background: none;
    font-size: 16px;
}

.context-menu button:active {
    background: var(--bg-hover);
}

.context-menu button[data-action="delete"] {
    color: var(--color-danger);
}
```

---

### 5. Tap (Click Alternative)

**Use Case**: Single tap on buttons, cards, navigation items

**Configuration**:
```javascript
const buttons = document.querySelectorAll('button, .tappable');

buttons.forEach(button => {
    const hammer = new Hammer(button);

    // Enable tap gesture (faster than click on mobile)
    hammer.on('tap', (event) => {
        button.click(); // Trigger normal click handler

        // Visual feedback (ripple effect)
        showRipple(event.center.x, event.center.y, button);
        hapticFeedback('light');
    });
});
```

**Ripple Effect**:
```javascript
function showRipple(x, y, element) {
    const ripple = document.createElement('span');
    ripple.className = 'ripple';

    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);

    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${x - rect.left - size / 2}px`;
    ripple.style.top = `${y - rect.top - size / 2}px`;

    element.appendChild(ripple);

    setTimeout(() => ripple.remove(), 600);
}
```

```css
button {
    position: relative;
    overflow: hidden;
}

.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transform: scale(0);
    animation: ripple-animation 0.6s ease-out;
    pointer-events: none;
}

@keyframes ripple-animation {
    to {
        transform: scale(4);
        opacity: 0;
    }
}
```

---

### 6. Double Tap (Quick Action)

**Use Case**: Double-tap event card to quickly accept/confirm

**Configuration**:
```javascript
const eventCards = document.querySelectorAll('.event-card');

eventCards.forEach(card => {
    const hammer = new Hammer(card);

    // Enable double tap
    hammer.get('tap').set({ enable: true });
    hammer.on('doubletap', (event) => {
        const eventId = card.dataset.eventId;
        quickConfirmEvent(eventId);
        hapticFeedback('medium');

        // Visual feedback (scale animation)
        card.style.transform = 'scale(0.95)';
        setTimeout(() => {
            card.style.transform = '';
        }, 100);
    });
});
```

---

## Haptic Feedback

### Native Vibration API

```javascript
function hapticFeedback(intensity = 'light') {
    if (!navigator.vibrate) return;

    const patterns = {
        light: 10,
        medium: 20,
        heavy: 30,
        success: [10, 20, 10],
        error: [20, 10, 20, 10, 20]
    };

    navigator.vibrate(patterns[intensity]);
}
```

### iOS Haptic Engine (via Capacitor/Cordova)

```javascript
// Requires Capacitor Haptics plugin
import { Haptics, ImpactStyle } from '@capacitor/haptics';

async function hapticFeedback(style = 'light') {
    const styles = {
        light: ImpactStyle.Light,
        medium: ImpactStyle.Medium,
        heavy: ImpactStyle.Heavy
    };

    await Haptics.impact({ style: styles[style] });
}
```

---

## Gesture Conflicts

### Prevent Browser Default

```javascript
// Prevent browser pull-to-refresh
document.body.addEventListener('touchmove', (event) => {
    if (event.target.closest('.prevent-overscroll')) {
        event.preventDefault();
    }
}, { passive: false });

// Prevent pinch-zoom on specific elements
const calendar = document.getElementById('calendar');
calendar.addEventListener('gesturestart', (event) => {
    event.preventDefault();
});
```

### Gesture Priority

```javascript
const element = document.getElementById('interactive-element');
const hammer = new Hammer(element);

// Require pan to fail before swipe fires
hammer.get('swipe').requireFailure('pan');

// Require tap to fail before double-tap fires
hammer.get('doubletap').recognizeWith('tap');
hammer.get('tap').requireFailure('doubletap');

// Prevent scroll during pinch
hammer.get('pinch').set({ enable: true });
hammer.on('pinchstart', () => {
    document.body.style.overflow = 'hidden';
});
hammer.on('pinchend', () => {
    document.body.style.overflow = '';
});
```

---

## Accessibility

### Keyboard Equivalents

```javascript
// Swipe left/right = Arrow keys
document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
        navigateToPreviousWeek();
    } else if (event.key === 'ArrowRight') {
        navigateToNextWeek();
    }
});

// Long press = Space/Enter key
document.addEventListener('keydown', (event) => {
    if (event.key === ' ' || event.key === 'Enter') {
        const focusedElement = document.activeElement;
        if (focusedElement.classList.contains('event-card')) {
            const eventId = focusedElement.dataset.eventId;
            showContextMenu(0, 0, eventId); // Show at focused element
        }
    }
});
```

### Screen Reader Announcements

```html
<!-- Announce swipe action -->
<div role="status" aria-live="polite" class="sr-only">
    <span id="swipe-announcement"></span>
</div>
```

```javascript
function navigateToNextWeek() {
    // Update UI
    loadNextWeek();

    // Announce to screen readers
    const announcement = document.getElementById('swipe-announcement');
    announcement.textContent = `Showing week of ${getNextWeekDate()}`;
}
```

---

## Performance

### Debounce Gesture Events

```javascript
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

const debouncedSwipe = debounce((direction) => {
    if (direction === 'left') {
        navigateToNextWeek();
    } else {
        navigateToPreviousWeek();
    }
}, 100);

hammer.on('swipeleft swiperight', (event) => {
    debouncedSwipe(event.type === 'swipeleft' ? 'left' : 'right');
});
```

### Request Animation Frame

```javascript
let rafId;

hammer.on('pinchmove', (event) => {
    if (rafId) cancelAnimationFrame(rafId);

    rafId = requestAnimationFrame(() => {
        const scale = calculateScale(event);
        calendar.style.transform = `scale(${scale})`;
    });
});
```

---

## Testing

### Playwright Touch Emulation

```python
# tests/e2e/test_touch_interactions.py
def test_swipe_navigation(page: Page):
    """Test swipe left/right navigation."""
    page.goto("http://localhost:8000/app/schedule")

    # Get initial week
    initial_week = page.locator('h2[data-i18n="schedule.week"]').inner_text()

    # Swipe left (next week)
    page.locator('#schedule-view').swipe_left()

    # Verify week changed
    new_week = page.locator('h2[data-i18n="schedule.week"]').inner_text()
    assert new_week != initial_week

def test_long_press_context_menu(page: Page):
    """Test long-press shows context menu."""
    page.goto("http://localhost:8000/app/schedule")

    # Long press on event card
    event_card = page.locator('.event-card').first
    event_card.long_press()

    # Verify context menu appears
    expect(page.locator('.context-menu')).to_be_visible()

    # Verify menu options
    expect(page.locator('.context-menu button[data-action="edit"]')).to_be_visible()
```

---

## References

- **Hammer.js Docs**: http://hammerjs.github.io/
- **Touch Events API**: https://developer.mozilla.org/en-US/docs/Web/API/Touch_events
- **Pointer Events API**: https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events
- **Vibration API**: https://developer.mozilla.org/en-US/docs/Web/API/Vibration_API

---

**Last Updated**: 2025-10-23
**Feature**: 018 - Mobile Responsive Design
**Library**: Hammer.js 2.0.17+
