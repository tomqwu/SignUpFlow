# API Contract: Service Worker Caching Strategies

**Feature**: Mobile Responsive Design | **Version**: 1.0.0 | **Date**: 2025-10-23

## Overview

This contract defines Service Worker caching strategies for SignUpFlow's Progressive Web App, enabling offline functionality and performance optimization. Implementation uses Workbox 7 for simplified Service Worker management.

**File Location**: `frontend/service-worker.js`
**Build Tool**: Workbox CLI or webpack/rollup plugin
**Cache Strategy**: Hybrid (precache static assets, runtime cache dynamic content)

---

## Workbox Configuration

### Build Configuration

```javascript
// workbox-config.js
module.exports = {
    // Source files to precache
    globDirectory: 'frontend/',
    globPatterns: [
        '**/*.{html,js,css,png,jpg,svg,woff2,json}'
    ],
    globIgnores: [
        '**/node_modules/**',
        '**/*.map',
        '**/tests/**'
    ],

    // Output service worker file
    swDest: 'frontend/service-worker.js',

    // Precache options
    maximumFileSizeToCacheInBytes: 5 * 1024 * 1024, // 5MB

    // Runtime caching rules
    runtimeCaching: [
        // User data (profile, settings)
        {
            urlPattern: /^https:\/\/localhost:8000\/api\/people\/me$/,
            handler: 'NetworkFirst',
            options: {
                cacheName: 'user-data',
                expiration: {
                    maxAgeSeconds: 300 // 5 minutes
                },
                networkTimeoutSeconds: 3
            }
        },

        // Events data
        {
            urlPattern: /^https:\/\/localhost:8000\/api\/events/,
            handler: 'StaleWhileRevalidate',
            options: {
                cacheName: 'events-data',
                expiration: {
                    maxEntries: 100,
                    maxAgeSeconds: 3600 // 1 hour
                }
            }
        },

        // Availability data
        {
            urlPattern: /^https:\/\/localhost:8000\/api\/availability/,
            handler: 'NetworkFirst',
            options: {
                cacheName: 'availability-data',
                expiration: {
                    maxAgeSeconds: 600 // 10 minutes
                },
                networkTimeoutSeconds: 3
            }
        },

        // Event assignments (schedule)
        {
            urlPattern: /^https:\/\/localhost:8000\/api\/events\/assignments/,
            handler: 'StaleWhileRevalidate',
            options: {
                cacheName: 'assignments-data',
                expiration: {
                    maxEntries: 200,
                    maxAgeSeconds: 1800 // 30 minutes
                }
            }
        },

        // Images
        {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
            handler: 'CacheFirst',
            options: {
                cacheName: 'images',
                expiration: {
                    maxEntries: 100,
                    maxAgeSeconds: 30 * 24 * 60 * 60 // 30 days
                }
            }
        }
    ],

    // Skip waiting and claim clients immediately
    skipWaiting: true,
    clientsClaim: true
};
```

### Build Command

```bash
# Generate service worker with Workbox CLI
npx workbox-cli generateSW workbox-config.js

# Or use webpack plugin
npm install workbox-webpack-plugin --save-dev
```

---

## Caching Strategies

### 1. CacheFirst (Cache-Falling-Back-to-Network)

**Use Case**: Static assets that rarely change (images, fonts, CSS)

**Behavior**:
1. Check cache first
2. If found → return cached response
3. If not found → fetch from network, cache it, return response

**Advantages**:
- Fastest response time
- Works offline immediately after first load
- Reduces network requests

**Example**:
```javascript
import { CacheFirst } from 'workbox-strategies';
import { registerRoute } from 'workbox-routing';

registerRoute(
    ({ request }) => request.destination === 'image',
    new CacheFirst({
        cacheName: 'images',
        plugins: [
            {
                cacheWillUpdate: async ({ response }) => {
                    // Only cache successful responses
                    return response.status === 200 ? response : null;
                }
            }
        ]
    })
);
```

**Performance**: ~5ms cache hit, ~500ms+ network miss

---

### 2. NetworkFirst (Network-Falling-Back-to-Cache)

**Use Case**: Dynamic content that changes frequently (user profile, recent events)

**Behavior**:
1. Try network first (with timeout)
2. If network succeeds → update cache, return response
3. If network fails or times out → return cached response

**Advantages**:
- Always tries to get fresh data
- Graceful degradation offline
- Good for frequently updated content

**Example**:
```javascript
import { NetworkFirst } from 'workbox-strategies';

registerRoute(
    /^https:\/\/localhost:8000\/api\/people\/me$/,
    new NetworkFirst({
        cacheName: 'user-data',
        networkTimeoutSeconds: 3, // Fallback to cache after 3s
        plugins: [
            {
                cacheWillUpdate: async ({ response }) => {
                    return response.status === 200 ? response : null;
                },
                fetchDidFail: async ({ request }) => {
                    console.log(`Network request failed: ${request.url}`);
                }
            }
        ]
    })
);
```

**Performance**: ~500ms network success, ~3s timeout + 5ms cache fallback

---

### 3. StaleWhileRevalidate (Cache-Then-Network)

**Use Case**: Content that updates moderately (events, schedules, team data)

**Behavior**:
1. Return cached response immediately
2. Fetch from network in background
3. Update cache for next request

**Advantages**:
- Always fast (returns cache immediately)
- Keeps cache fresh
- Best user experience (instant load + fresh data)

**Example**:
```javascript
import { StaleWhileRevalidate } from 'workbox-strategies';

registerRoute(
    /^https:\/\/localhost:8000\/api\/events/,
    new StaleWhileRevalidate({
        cacheName: 'events-data',
        plugins: [
            {
                cacheDidUpdate: async ({ cacheName, request, oldResponse, newResponse }) => {
                    // Notify app that cache was updated
                    const channel = new BroadcastChannel('cache-updates');
                    channel.postMessage({
                        type: 'CACHE_UPDATED',
                        url: request.url,
                        cacheName
                    });
                }
            }
        ]
    })
);
```

**Performance**: ~5ms initial response, ~500ms background update

---

### 4. NetworkOnly (No Caching)

**Use Case**: Sensitive operations (login, logout, POST/PUT/DELETE requests)

**Behavior**:
1. Always fetch from network
2. Never cache response
3. Fail if offline

**Example**:
```javascript
import { NetworkOnly } from 'workbox-strategies';

registerRoute(
    ({ url, request }) => {
        return request.method === 'POST' ||
               request.method === 'PUT' ||
               request.method === 'DELETE';
    },
    new NetworkOnly()
);
```

---

### 5. CacheOnly (Never Network)

**Use Case**: App shell (critical HTML/CSS/JS that must be cached)

**Behavior**:
1. Only check cache
2. Never fetch from network
3. Fail if not in cache

**Example**:
```javascript
import { CacheOnly } from 'workbox-strategies';

registerRoute(
    '/app/shell',
    new CacheOnly({
        cacheName: 'app-shell'
    })
);
```

---

## Background Sync

### Queue Offline Actions

```javascript
// service-worker.js
import { BackgroundSyncPlugin } from 'workbox-background-sync';
import { registerRoute } from 'workbox-routing';
import { NetworkOnly } from 'workbox-strategies';

const bgSyncPlugin = new BackgroundSyncPlugin('availability-queue', {
    maxRetentionTime: 24 * 60 // Retry for 24 hours
});

// Queue POST requests to availability endpoint
registerRoute(
    /^https:\/\/localhost:8000\/api\/availability/,
    new NetworkOnly({
        plugins: [bgSyncPlugin]
    }),
    'POST'
);
```

### Replay Queue on Reconnect

```javascript
// Automatic replay when back online
self.addEventListener('sync', (event) => {
    if (event.tag === 'availability-queue') {
        event.waitUntil(
            // Workbox handles replaying automatically
            console.log('Background sync triggered')
        );
    }
});
```

---

## Precaching

### Static Asset Precaching

```javascript
// service-worker.js (generated by Workbox)
import { precacheAndRoute } from 'workbox-precaching';

// __WB_MANIFEST is injected by Workbox CLI
precacheAndRoute(self.__WB_MANIFEST || []);

// Manually add additional files
precacheAndRoute([
    { url: '/app/shell', revision: '1' },
    { url: '/offline.html', revision: '1' }
]);
```

### Precache Manifest Format

```javascript
// Workbox generates this manifest:
[
    {
        url: '/css/styles.css',
        revision: 'abc123' // File hash
    },
    {
        url: '/js/app.js',
        revision: 'def456'
    },
    {
        url: '/index.html',
        revision: 'ghi789'
    }
]
```

---

## Cache Expiration

### Time-Based Expiration

```javascript
import { ExpirationPlugin } from 'workbox-expiration';

new StaleWhileRevalidate({
    cacheName: 'events-data',
    plugins: [
        new ExpirationPlugin({
            maxAgeSeconds: 3600, // 1 hour
            purgeOnQuotaError: true // Auto-delete on storage quota error
        })
    ]
});
```

### Entry-Based Expiration

```javascript
new CacheFirst({
    cacheName: 'images',
    plugins: [
        new ExpirationPlugin({
            maxEntries: 100, // Keep max 100 images
            maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
            purgeOnQuotaError: true
        })
    ]
});
```

---

## Cache Warmup

### Warm Cache on Install

```javascript
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open('events-data').then(cache => {
            // Pre-fetch critical data
            return cache.addAll([
                '/api/events/?org_id=current',
                '/api/people/me'
            ]);
        })
    );
});
```

---

## Cache Updates

### Notify App of Cache Updates

```javascript
// service-worker.js
self.addEventListener('message', (event) => {
    if (event.data.type === 'CACHE_UPDATED') {
        // Notify all clients
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'CACHE_UPDATED',
                    url: event.data.url
                });
            });
        });
    }
});

// frontend/js/app.js
navigator.serviceWorker.addEventListener('message', (event) => {
    if (event.data.type === 'CACHE_UPDATED') {
        console.log(`Cache updated for: ${event.data.url}`);
        // Optionally reload data in UI
    }
});
```

---

## Offline Fallback

### Offline Page

```javascript
// service-worker.js
import { setCatchHandler } from 'workbox-routing';

setCatchHandler(async ({ event }) => {
    // Return cached offline page for navigation requests
    if (event.request.destination === 'document') {
        return caches.match('/offline.html');
    }

    return Response.error();
});
```

```html
<!-- frontend/offline.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Offline - SignUpFlow</title>
    <style>
        body {
            font-family: system-ui;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background: #f5f5f5;
        }
        .offline-message {
            text-align: center;
            padding: 2rem;
        }
    </style>
</head>
<body>
    <div class="offline-message">
        <h1>You're Offline</h1>
        <p>Please check your internet connection and try again.</p>
        <button onclick="location.reload()">Retry</button>
    </div>
</body>
</html>
```

---

## Performance Monitoring

### Cache Hit Rate

```javascript
// service-worker.js
let cacheHits = 0;
let cacheMisses = 0;

self.addEventListener('fetch', (event) => {
    event.waitUntil(
        caches.match(event.request).then(response => {
            if (response) {
                cacheHits++;
            } else {
                cacheMisses++;
            }

            // Report metrics every 100 requests
            if ((cacheHits + cacheMisses) % 100 === 0) {
                const hitRate = (cacheHits / (cacheHits + cacheMisses)) * 100;
                console.log(`Cache hit rate: ${hitRate.toFixed(1)}%`);
            }
        })
    );
});
```

---

## Testing

### Service Worker Test

```javascript
// tests/unit/test_service_worker.js
describe('Service Worker', () => {
    it('should cache static assets', async () => {
        const cache = await caches.open('workbox-precache-v2');
        const cachedResponse = await cache.match('/css/styles.css');
        expect(cachedResponse).toBeDefined();
    });

    it('should use NetworkFirst for user data', async () => {
        const response = await fetch('/api/people/me');
        expect(response.ok).toBe(true);

        // Check cache was updated
        const cache = await caches.open('user-data');
        const cachedResponse = await cache.match('/api/people/me');
        expect(cachedResponse).toBeDefined();
    });
});
```

### Offline Test (Playwright)

```python
# tests/e2e/test_offline_mode.py
def test_app_works_offline(page: Page):
    """Test app functions offline after initial load."""
    # Load app online
    page.goto("http://localhost:8000/app/schedule")

    # Wait for cache to populate
    page.wait_for_timeout(2000)

    # Go offline
    page.context.set_offline(True)

    # Reload page
    page.reload()

    # Verify page loads from cache
    expect(page.locator('h2[data-i18n="schedule.my_schedule"]')).to_be_visible()

    # Verify data loads from cache
    expect(page.locator('.event-card')).to_have_count_greater_than(0)
```

---

## Security

### HTTPS Requirement

Service Workers require HTTPS (except localhost):

```nginx
# nginx HTTPS configuration
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

### Same-Origin Policy

Service Workers only work on same-origin requests:

```javascript
// Only cache same-origin requests
registerRoute(
    ({ url }) => url.origin === self.location.origin,
    new StaleWhileRevalidate()
);
```

---

## References

- **Workbox Docs**: https://developers.google.com/web/tools/workbox
- **Service Worker API**: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API
- **Cache Storage API**: https://developer.mozilla.org/en-US/docs/Web/API/CacheStorage
- **Background Sync API**: https://web.dev/background-sync/

---

**Last Updated**: 2025-10-23
**Feature**: 018 - Mobile Responsive Design
**Workbox Version**: 7.0+
