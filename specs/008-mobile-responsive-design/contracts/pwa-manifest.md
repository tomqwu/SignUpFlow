# API Contract: PWA Manifest

**Feature**: Mobile Responsive Design | **Version**: 1.0.0 | **Date**: 2025-10-23

## Overview

This manifest.json file enables Progressive Web App (PWA) capabilities for SignUpFlow, allowing users to install the app on their home screen and use it like a native mobile application.

**File Location**: `frontend/manifest.json`
**Referenced From**: `frontend/index.html` via `<link rel="manifest" href="/manifest.json">`

---

## Manifest Schema

```json
{
  "name": "SignUpFlow - Volunteer Scheduling",
  "short_name": "SignUpFlow",
  "description": "AI-powered volunteer scheduling and sign-up management for churches and non-profits",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait-primary",
  "theme_color": "#2563eb",
  "background_color": "#ffffff",
  "lang": "en-US",
  "dir": "ltr",
  "categories": ["productivity", "lifestyle", "utilities"],
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable any"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshots/schedule-mobile.png",
      "sizes": "750x1334",
      "type": "image/png",
      "form_factor": "narrow",
      "label": "Schedule view on mobile"
    },
    {
      "src": "/screenshots/availability-mobile.png",
      "sizes": "750x1334",
      "type": "image/png",
      "form_factor": "narrow",
      "label": "Availability management"
    },
    {
      "src": "/screenshots/schedule-tablet.png",
      "sizes": "1536x2048",
      "type": "image/png",
      "form_factor": "wide",
      "label": "Schedule view on tablet"
    }
  ],
  "shortcuts": [
    {
      "name": "My Schedule",
      "short_name": "Schedule",
      "description": "View my upcoming volunteer schedule",
      "url": "/app/schedule",
      "icons": [
        {
          "src": "/icons/shortcut-schedule.png",
          "sizes": "96x96",
          "type": "image/png"
        }
      ]
    },
    {
      "name": "Update Availability",
      "short_name": "Availability",
      "description": "Add time-off or unavailable dates",
      "url": "/app/availability",
      "icons": [
        {
          "src": "/icons/shortcut-availability.png",
          "sizes": "96x96",
          "type": "image/png"
        }
      ]
    },
    {
      "name": "Upcoming Events",
      "short_name": "Events",
      "description": "View upcoming volunteer events",
      "url": "/app/events",
      "icons": [
        {
          "src": "/icons/shortcut-events.png",
          "sizes": "96x96",
          "type": "image/png"
        }
      ]
    }
  ],
  "related_applications": [],
  "prefer_related_applications": false
}
```

---

## Property Specifications

### Core Properties

#### `name` (string, required)
**Full application name** displayed during installation and in app switcher.

**Requirements**:
- Maximum 45 characters
- Descriptive and brandable
- Includes primary value proposition

**Example**: "SignUpFlow - Volunteer Scheduling"

#### `short_name` (string, required)
**Abbreviated name** displayed under home screen icon.

**Requirements**:
- Maximum 12 characters (to fit under icon)
- Must fit on single line
- Easy to recognize

**Example**: "SignUpFlow"

#### `description` (string, recommended)
**One-sentence description** of app functionality.

**Requirements**:
- Maximum 132 characters
- Clear value proposition
- Used in app stores/listings

**Example**: "AI-powered volunteer scheduling and sign-up management for churches and non-profits"

### Display Properties

#### `start_url` (string, required)
**URL loaded** when user launches app from home screen.

**Requirements**:
- Relative or absolute URL
- Should include UTM parameters for analytics
- Must be within `scope`

**Recommended**:
```json
{
  "start_url": "/?source=pwa&utm_source=homescreen"
}
```

#### `scope` (string, recommended)
**Navigation boundary** - URLs within scope use PWA chrome.

**Requirements**:
- Must be same origin
- Parent directory of `start_url`
- Defaults to directory of manifest

**Example**: `"scope": "/"` (entire site)

#### `display` (enum, required)
**Display mode** for installed app.

**Options**:
- `"standalone"` ✅ **RECOMMENDED**: App looks like native app (no browser chrome)
- `"fullscreen"`: Fullscreen mode (rare use case)
- `"minimal-ui"`: Minimal browser UI (back button only)
- `"browser"`: Regular browser tab

**Example**: `"display": "standalone"`

#### `orientation` (enum, optional)
**Screen orientation** preference.

**Options**:
- `"portrait-primary"` ✅ **RECOMMENDED**: Portrait mode (most mobile apps)
- `"landscape-primary"`: Landscape mode
- `"any"`: No orientation lock

**Example**: `"orientation": "portrait-primary"`

### Visual Properties

#### `theme_color` (hex color, required)
**Browser chrome color** (status bar, address bar).

**Requirements**:
- Hex color code
- Should match app primary brand color
- Visible in browser UI

**Example**: `"theme_color": "#2563eb"` (SignUpFlow blue)

#### `background_color` (hex color, required)
**Splash screen background color** during app launch.

**Requirements**:
- Hex color code
- Should match app background
- Shows before app loads

**Example**: `"background_color": "#ffffff"` (white)

### Icon Specifications

#### `icons` (array, required)
**App icons** for home screen, splash screen, app switcher.

**Requirements**:
- Minimum 1 icon (192x192px)
- Recommended sizes: 72, 96, 128, 144, 152, 192, 384, 512
- PNG format (maskable for Android adaptive icons)
- Square aspect ratio

**Icon Sizes**:
```
Android Home Screen:
- 48dp  → 72x72px  (ldpi)
- 72dp  → 96x96px  (mdpi)
- 96dp  → 144x144px (hdpi)
- 128dp → 192x192px (xhdpi)
- 192dp → 384x384px (xxhdpi)
- 256dp → 512x512px (xxxhdpi)

iOS Home Screen:
- 152x152px (iPad)
- 167x167px (iPad Pro)
- 180x180px (iPhone)
```

**Maskable Icons** (Android Adaptive Icons):
- Safe zone: center 80% (40% padding on each side)
- Icons can be cropped to circles, squares, rounded squares
- Example: Icon must fit within center 80% circle

```json
{
  "src": "/icons/icon-192x192.png",
  "sizes": "192x192",
  "type": "image/png",
  "purpose": "maskable any"
}
```

### Screenshots

#### `screenshots` (array, recommended)
**App store listing screenshots** (Android only, iOS uses App Store Connect).

**Requirements**:
- Minimum 1 screenshot
- Realistic device screenshot (not mockup)
- Labeled for context

**Form Factors**:
- `"narrow"`: Mobile phones (portrait)
- `"wide"`: Tablets, desktops (landscape)

**Example**:
```json
{
  "src": "/screenshots/schedule-mobile.png",
  "sizes": "750x1334",
  "type": "image/png",
  "form_factor": "narrow",
  "label": "Schedule view on mobile"
}
```

### Shortcuts

#### `shortcuts` (array, optional)
**Quick actions** from home screen long-press (Android) or 3D Touch (iOS).

**Requirements**:
- Maximum 4 shortcuts
- Each needs icon (96x96px minimum)
- Must link to valid URLs within `scope`

**Example**:
```json
{
  "name": "My Schedule",
  "short_name": "Schedule",
  "description": "View my upcoming volunteer schedule",
  "url": "/app/schedule",
  "icons": [
    {
      "src": "/icons/shortcut-schedule.png",
      "sizes": "96x96",
      "type": "image/png"
    }
  ]
}
```

---

## Installation Requirements

### HTML Reference

```html
<!-- frontend/index.html -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- PWA Manifest -->
  <link rel="manifest" href="/manifest.json">

  <!-- Theme color (matches manifest) -->
  <meta name="theme-color" content="#2563eb">

  <!-- Apple-specific meta tags (iOS doesn't fully support manifest) -->
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="SignUpFlow">
  <link rel="apple-touch-icon" href="/icons/icon-180x180.png">

  <!-- Android Chrome tab color -->
  <meta name="mobile-web-app-capable" content="yes">
</head>
```

### Service Worker Registration

```javascript
// frontend/js/pwa-installer.js
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
            })
            .catch(error => {
                console.error('Service Worker registration failed:', error);
            });
    });
}
```

---

## Install Prompt

### Custom Install Button

```javascript
// frontend/js/pwa-installer.js
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (event) => {
    // Prevent automatic install prompt
    event.preventDefault();
    deferredPrompt = event;

    // Show custom install button
    const installButton = document.getElementById('pwa-install-button');
    installButton.style.display = 'block';

    installButton.addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();

            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response: ${outcome}`); // 'accepted' or 'dismissed'

            deferredPrompt = null;
            installButton.style.display = 'none';
        }
    });
});

// Listen for successful install
window.addEventListener('appinstalled', () => {
    console.log('PWA installed successfully');
    deferredPrompt = null;

    // Hide install button
    const installButton = document.getElementById('pwa-install-button');
    installButton.style.display = 'none';

    // Show thank you message
    showToast('App installed! Access from your home screen.', 'success');
});
```

---

## Icon Generation

### Required Icon Sizes

```bash
# Generate all required icon sizes from source SVG
# Requires ImageMagick

SOURCE="logo.svg"
SIZES=(72 96 128 144 152 192 384 512)

for size in "${SIZES[@]}"; do
    convert -background none \
            -resize ${size}x${size} \
            $SOURCE \
            icons/icon-${size}x${size}.png
done

# Apple Touch Icon (180x180)
convert -background none \
        -resize 180x180 \
        $SOURCE \
        icons/icon-180x180.png
```

### Maskable Icon Safe Zone

```css
/* Maskable icon design guidelines */
/* Center 80% is safe zone (40% padding each side) */

.icon-safe-zone {
    width: 512px;
    height: 512px;
}

.safe-content {
    width: 410px;  /* 80% of 512px */
    height: 410px;
    margin: 51px;  /* 10% padding = 51px */
}
```

---

## Testing & Validation

### Chrome DevTools

1. Open DevTools → Application tab
2. Click "Manifest" in left sidebar
3. Verify:
   - ✅ Name and icons load correctly
   - ✅ Start URL is valid
   - ✅ Theme color matches design
   - ✅ "Add to Home Screen" link works

### Lighthouse PWA Audit

```bash
# Run Lighthouse PWA audit
npx lighthouse http://localhost:8000 \
    --only-categories=pwa \
    --output=html \
    --output-path=./lighthouse-pwa-report.html
```

**Required Checks**:
- ✅ Manifest includes name, short_name, icons, start_url
- ✅ Icon sizes include 192x192 and 512x512
- ✅ Service worker registered
- ✅ HTTPS (required for PWA, except localhost)

### Browser Support

| Browser | Manifest Support | Install Prompt | Shortcuts |
|---------|-----------------|----------------|-----------|
| Chrome (Android) | ✅ Full | ✅ Yes | ✅ Yes |
| Chrome (Desktop) | ✅ Full | ✅ Yes | ❌ No |
| Safari (iOS) | ⚠️ Partial | ❌ No (manual) | ❌ No |
| Safari (macOS) | ⚠️ Partial | ❌ No | ❌ No |
| Edge (Android) | ✅ Full | ✅ Yes | ✅ Yes |
| Firefox (Android) | ✅ Full | ✅ Yes | ❌ No |

**iOS Quirks**:
- Must use `<link rel="apple-touch-icon">` for icons
- Must use `<meta name="apple-mobile-web-app-*">` for config
- No automatic install prompt (user must manually "Add to Home Screen")

---

## Security

### HTTPS Requirement

PWAs require HTTPS (except localhost development):

```nginx
# nginx configuration for HTTPS
server {
    listen 443 ssl http2;
    server_name signupflow.io;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
    }
}
```

### Content Security Policy

```html
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    img-src 'self' data: https:;
    manifest-src 'self';
">
```

---

## References

- **W3C Manifest Spec**: https://www.w3.org/TR/appmanifest/
- **MDN Web Manifest**: https://developer.mozilla.org/en-US/docs/Web/Manifest
- **Google PWA Guide**: https://web.dev/progressive-web-apps/
- **Maskable.app**: https://maskable.app/ (test maskable icons)
- **PWA Builder**: https://www.pwabuilder.com/ (generate manifest)

---

**Last Updated**: 2025-10-23
**Feature**: 018 - Mobile Responsive Design
**Manifest Version**: 1.0.0
