# API Contract: Responsive Breakpoints & Layout Rules

**Feature**: Mobile Responsive Design | **Version**: 1.0.0 | **Date**: 2025-10-23

## Overview

This contract defines responsive breakpoints, media query patterns, and layout rules for SignUpFlow's mobile-first responsive design. All layouts adapt to screen sizes from 320px (small mobile) to 1920px+ (wide desktop).

**Approach**: Mobile-first CSS (start with mobile, add complexity with `min-width` media queries)
**Breakpoint Strategy**: 3 primary breakpoints (mobile, tablet, desktop)
**Target Devices**: iOS Safari 15+, Android Chrome 100+, modern tablets, desktop browsers

---

## Breakpoint Specifications

### Breakpoint Definitions

```css
/* CSS Custom Properties for consistency */
:root {
    --breakpoint-mobile-max: 767px;    /* Mobile: 320px - 767px */
    --breakpoint-tablet-min: 768px;    /* Tablet: 768px - 1023px */
    --breakpoint-tablet-max: 1023px;
    --breakpoint-desktop-min: 1024px;  /* Desktop: 1024px+ */
    --breakpoint-wide-min: 1440px;     /* Wide desktop: 1440px+ */
}
```

### Media Query Patterns

```css
/* Mobile (base styles, no media query needed) */
.container {
    padding: 1rem;
    font-size: 14px;
}

/* Tablet (768px+) */
@media (min-width: 768px) {
    .container {
        padding: 1.5rem;
        font-size: 16px;
    }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
    .container {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
}

/* Wide Desktop (1440px+) */
@media (min-width: 1440px) {
    .container {
        max-width: 1400px;
    }
}
```

---

## Device Targeting

### Specific Device Sizes

| Device | Viewport Width | Viewport Height | Breakpoint | DPR |
|--------|---------------|-----------------|------------|-----|
| **Mobile** |
| iPhone SE | 375px | 667px | Mobile | 2x |
| iPhone 13/14 | 390px | 844px | Mobile | 3x |
| iPhone 13/14 Pro Max | 428px | 926px | Mobile | 3x |
| Pixel 5 | 393px | 851px | Mobile | 2.75x |
| Galaxy S22 | 360px | 800px | Mobile | 3x |
| **Tablet** |
| iPad Mini | 768px | 1024px | Tablet | 2x |
| iPad Air | 820px | 1180px | Tablet | 2x |
| iPad Pro 11" | 834px | 1194px | Tablet | 2x |
| iPad Pro 12.9" | 1024px | 1366px | Desktop | 2x |
| **Desktop** |
| Laptop (13") | 1280px | 800px | Desktop | 1-2x |
| Desktop (1080p) | 1920px | 1080px | Wide | 1x |
| Desktop (4K) | 3840px | 2160px | Wide | 2x |

### Safe Area Insets (Notches)

```css
/* Handle iPhone notch, Android notch, bottom home indicator */
.header {
    padding-top: env(safe-area-inset-top);
}

.bottom-nav {
    padding-bottom: env(safe-area-inset-bottom);
}

.content {
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
}
```

---

## Layout Rules

### Grid System

```css
/* Mobile-first grid (single column by default) */
.grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
}

/* Tablet: 2 columns */
@media (min-width: 768px) {
    .grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
    }
}

/* Desktop: 3+ columns */
@media (min-width: 1024px) {
    .grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
    }

    .grid-4 {
        grid-template-columns: repeat(4, 1fr);
    }
}
```

### Flexbox Patterns

```css
/* Stack on mobile, row on tablet+ */
.flex-row {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

@media (min-width: 768px) {
    .flex-row {
        flex-direction: row;
        align-items: center;
    }
}

/* Reverse order on mobile */
.flex-reverse {
    display: flex;
    flex-direction: column-reverse;
}

@media (min-width: 768px) {
    .flex-reverse {
        flex-direction: row;
    }
}
```

### Container Widths

```css
.container {
    width: 100%;
    padding-inline: 1rem; /* Modern CSS logical properties */
}

@media (min-width: 768px) {
    .container {
        padding-inline: 2rem;
    }
}

@media (min-width: 1024px) {
    .container {
        max-width: 1200px;
        margin-inline: auto;
    }
}

@media (min-width: 1440px) {
    .container {
        max-width: 1400px;
    }
}
```

---

## Component-Specific Breakpoints

### Navigation

```css
/* Mobile: Bottom navigation bar */
@media (max-width: 767px) {
    .desktop-nav {
        display: none;
    }

    .bottom-nav {
        display: flex;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 56px;
        background: var(--bg-surface);
        border-top: 1px solid var(--border-color);
        z-index: 1000;
        padding-bottom: env(safe-area-inset-bottom);
    }

    .bottom-nav-item {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 4px;
        font-size: 12px;
    }
}

/* Tablet/Desktop: Top navigation bar */
@media (min-width: 768px) {
    .bottom-nav {
        display: none;
    }

    .desktop-nav {
        display: flex;
        height: 64px;
        padding: 0 2rem;
        align-items: center;
        gap: 2rem;
    }
}
```

### Schedule Cards

```css
/* Mobile: Full-width cards, vertical layout */
.schedule-card {
    display: flex;
    flex-direction: column;
    padding: 1rem;
    gap: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 8px;
}

/* Tablet: 2-column grid, horizontal layout */
@media (min-width: 768px) {
    .schedule-card {
        flex-direction: row;
        padding: 1.5rem;
        gap: 1.5rem;
        align-items: center;
    }

    .schedule-card-content {
        flex: 1;
    }

    .schedule-card-actions {
        flex-shrink: 0;
        width: auto;
    }
}

/* Desktop: More spacing, larger text */
@media (min-width: 1024px) {
    .schedule-card {
        padding: 2rem;
        font-size: 16px;
    }
}
```

### Forms

```css
/* Mobile: Stacked form fields */
.form-row {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-field {
    width: 100%;
}

/* Tablet/Desktop: Inline form fields */
@media (min-width: 768px) {
    .form-row {
        flex-direction: row;
        gap: 1.5rem;
    }

    .form-field {
        flex: 1;
    }

    .form-field-half {
        flex: 0 0 calc(50% - 0.75rem);
    }
}
```

### Tables

```css
/* Mobile: Card-based table (no actual table) */
@media (max-width: 767px) {
    table {
        display: none; /* Hide actual table */
    }

    .table-card {
        display: block;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .table-card-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border-light);
    }

    .table-card-label {
        font-weight: 600;
        color: var(--text-secondary);
    }
}

/* Tablet/Desktop: Actual table */
@media (min-width: 768px) {
    .table-card {
        display: none; /* Hide card version */
    }

    table {
        display: table;
        width: 100%;
        border-collapse: collapse;
    }

    th, td {
        padding: 0.75rem 1rem;
        text-align: left;
    }
}
```

### Modals/Dialogs

```css
/* Mobile: Full-screen modal */
@media (max-width: 767px) {
    .modal {
        position: fixed;
        inset: 0; /* top, right, bottom, left: 0 */
        background: var(--bg-surface);
        z-index: 2000;
        overflow-y: auto;
    }

    .modal-content {
        padding: 1rem;
        min-height: 100vh;
    }

    .modal-header {
        position: sticky;
        top: 0;
        background: var(--bg-surface);
        padding: 1rem;
        border-bottom: 1px solid var(--border-color);
        z-index: 1;
    }
}

/* Tablet/Desktop: Centered dialog */
@media (min-width: 768px) {
    .modal {
        position: fixed;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.5);
        z-index: 2000;
    }

    .modal-content {
        background: var(--bg-surface);
        border-radius: 12px;
        max-width: 600px;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }

    .modal-header {
        padding: 1.5rem;
        border-bottom: 1px solid var(--border-color);
    }
}
```

---

## Typography Scale

```css
/* Mobile typography (base) */
:root {
    --font-size-xs: 12px;
    --font-size-sm: 14px;
    --font-size-base: 16px;
    --font-size-lg: 18px;
    --font-size-xl: 20px;
    --font-size-2xl: 24px;
    --font-size-3xl: 28px;
}

/* Tablet: Slightly larger */
@media (min-width: 768px) {
    :root {
        --font-size-base: 16px;
        --font-size-lg: 20px;
        --font-size-xl: 24px;
        --font-size-2xl: 28px;
        --font-size-3xl: 32px;
    }
}

/* Desktop: Larger still */
@media (min-width: 1024px) {
    :root {
        --font-size-lg: 22px;
        --font-size-xl: 26px;
        --font-size-2xl: 32px;
        --font-size-3xl: 36px;
    }
}
```

---

## Spacing Scale

```css
/* Mobile spacing (base) */
:root {
    --spacing-xs: 0.25rem;  /* 4px */
    --spacing-sm: 0.5rem;   /* 8px */
    --spacing-md: 1rem;     /* 16px */
    --spacing-lg: 1.5rem;   /* 24px */
    --spacing-xl: 2rem;     /* 32px */
    --spacing-2xl: 3rem;    /* 48px */
}

/* Tablet/Desktop: More generous spacing */
@media (min-width: 768px) {
    :root {
        --spacing-lg: 2rem;    /* 32px */
        --spacing-xl: 3rem;    /* 48px */
        --spacing-2xl: 4rem;   /* 64px */
    }
}
```

---

## Touch Target Sizes

```css
/* WCAG 2.1 AA: Minimum 44x44px touch targets */
button,
a,
input[type="checkbox"],
input[type="radio"],
.interactive {
    min-width: 44px;
    min-height: 44px;
    padding: 0.5rem 1rem;
}

/* Desktop: Can be smaller (using mouse) */
@media (min-width: 1024px) and (pointer: fine) {
    button,
    a {
        min-width: auto;
        min-height: auto;
        padding: 0.5rem 1rem;
    }
}
```

---

## Orientation Handling

```css
/* Portrait orientation (default) */
@media (orientation: portrait) {
    .schedule-calendar {
        grid-template-columns: 1fr;
    }
}

/* Landscape orientation (e.g., phone rotated) */
@media (orientation: landscape) and (max-height: 500px) {
    /* Reduce vertical spacing on short landscape screens */
    .header {
        height: 48px;
        font-size: 14px;
    }

    .schedule-calendar {
        grid-template-columns: repeat(2, 1fr);
    }
}
```

---

## Print Styles

```css
@media print {
    /* Hide navigation, buttons */
    .bottom-nav,
    .desktop-nav,
    .hamburger-menu,
    button:not(.print-button) {
        display: none !important;
    }

    /* Expand content to full width */
    .container {
        max-width: 100%;
        padding: 0;
    }

    /* Black text on white background */
    body {
        color: #000;
        background: #fff;
    }

    /* Show URLs for links */
    a[href]:after {
        content: " (" attr(href) ")";
        font-size: 0.8em;
        color: #666;
    }
}
```

---

## High Contrast Mode

```css
@media (prefers-contrast: high) {
    :root {
        --text-primary: #000;
        --text-secondary: #333;
        --bg-surface: #fff;
        --border-color: #000;
    }

    button {
        border: 2px solid #000;
    }
}
```

---

## Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## Dark Mode

```css
@media (prefers-color-scheme: dark) {
    :root {
        --text-primary: #e5e5e5;
        --text-secondary: #a3a3a3;
        --bg-surface: #1a1a1a;
        --bg-elevated: #262626;
        --border-color: #404040;
    }
}
```

---

## Testing Breakpoints

### Manual Testing

```bash
# Test all breakpoints in Chrome DevTools
# Device Toolbar (Cmd+Shift+M / Ctrl+Shift+M)
# Toggle device toolbar
# Select device from dropdown or custom dimensions
```

**Test Checklist**:
- [ ] 320px (iPhone SE portrait)
- [ ] 375px (iPhone 13 portrait)
- [ ] 768px (iPad portrait)
- [ ] 1024px (iPad landscape, laptop)
- [ ] 1440px (desktop)

### Playwright Test

```python
# tests/e2e/test_responsive_layout.py
def test_layout_adapts_to_breakpoints(page: Page):
    """Test layout adapts correctly at each breakpoint."""

    # Mobile (375px)
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:8000/app/schedule")

    # Verify bottom nav visible
    expect(page.locator('.bottom-nav')).to_be_visible()
    expect(page.locator('.desktop-nav')).to_be_hidden()

    # Tablet (768px)
    page.set_viewport_size({"width": 768, "height": 1024})

    # Verify desktop nav visible
    expect(page.locator('.desktop-nav')).to_be_visible()
    expect(page.locator('.bottom-nav')).to_be_hidden()

    # Desktop (1024px)
    page.set_viewport_size({"width": 1024, "height": 768})

    # Verify container max-width applied
    container = page.locator('.container')
    box = container.bounding_box()
    assert box['width'] <= 1200, "Container should be max 1200px"
```

---

## References

- **CSS Media Queries**: https://developer.mozilla.org/en-US/docs/Web/CSS/Media_Queries
- **Responsive Design Guidelines**: https://web.dev/responsive-web-design-basics/
- **Device Metrics**: https://material.io/resources/devices/
- **Safe Area Insets**: https://webkit.org/blog/7929/designing-websites-for-iphone-x/

---

**Last Updated**: 2025-10-23
**Feature**: 018 - Mobile Responsive Design
**Breakpoints**: 320px, 768px, 1024px, 1440px
