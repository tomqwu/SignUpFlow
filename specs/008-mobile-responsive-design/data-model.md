# Data Model: Mobile Responsive Design - Offline Storage

**Feature**: Mobile Responsive Design | **Branch**: `008-mobile-responsive-design` | **Date**: 2025-10-23

This document defines the IndexedDB schema for offline data storage, enabling SignUpFlow to function without network connectivity. All data models follow Progressive Web App (PWA) patterns with background sync capabilities.

---

## Overview

**Storage Technology**: IndexedDB (via Workbox/idb library)
**Storage Capacity**: 50MB-1GB (varies by browser, can request more)
**Sync Strategy**: Background Sync API for queued actions, periodic sync for data freshness
**Offline Capabilities**: View schedules, update availability, queue actions, view cached events

---

## Database Schema

### Database Configuration

```javascript
// offline-db.js
import { openDB } from 'idb';

const DB_NAME = 'signupflow-offline';
const DB_VERSION = 1;

export async function initOfflineDB() {
    return await openDB(DB_NAME, DB_VERSION, {
        upgrade(db, oldVersion, newVersion, transaction) {
            // Create object stores and indexes
            if (oldVersion < 1) {
                createV1Schema(db);
            }
        },
        blocked() {
            console.warn('Database upgrade blocked by another tab');
        },
        blocking() {
            console.warn('This tab is blocking database upgrade');
        }
    });
}

function createV1Schema(db) {
    // 1. Events Store
    const eventsStore = db.createObjectStore('events', {
        keyPath: 'id'
    });
    eventsStore.createIndex('datetime', 'datetime');
    eventsStore.createIndex('org_id', 'org_id');
    eventsStore.createIndex('cached_at', 'cached_at');

    // 2. People Store
    const peopleStore = db.createObjectStore('people', {
        keyPath: 'id'
    });
    peopleStore.createIndex('org_id', 'org_id');
    peopleStore.createIndex('email', 'email', { unique: true });
    peopleStore.createIndex('cached_at', 'cached_at');

    // 3. Availability Store
    const availStore = db.createObjectStore('availability', {
        keyPath: 'id'
    });
    availStore.createIndex('person_id', 'person_id');
    availStore.createIndex('start_date', 'start_date');
    availStore.createIndex('cached_at', 'cached_at');

    // 4. Event Assignments Store
    const assignStore = db.createObjectStore('assignments', {
        keyPath: 'id'
    });
    assignStore.createIndex('event_id', 'event_id');
    assignStore.createIndex('person_id', 'person_id');
    assignStore.createIndex('cached_at', 'cached_at');

    // 5. Teams Store
    const teamsStore = db.createObjectStore('teams', {
        keyPath: 'id'
    });
    teamsStore.createIndex('org_id', 'org_id');
    teamsStore.createIndex('cached_at', 'cached_at');

    // 6. Pending Actions Store (offline queue)
    const pendingStore = db.createObjectStore('pending_actions', {
        keyPath: 'id',
        autoIncrement: true
    });
    pendingStore.createIndex('timestamp', 'timestamp');
    pendingStore.createIndex('action_type', 'action_type');
    pendingStore.createIndex('status', 'status'); // 'pending', 'syncing', 'failed'

    // 7. Cache Metadata Store
    const metaStore = db.createObjectStore('cache_metadata', {
        keyPath: 'key'
    });
    metaStore.createIndex('last_sync', 'last_sync');
}
```

---

## Entity Models

### 1. Event (Cached from Backend)

**Purpose**: Store event data for offline schedule viewing

```typescript
interface Event {
    // Primary key
    id: string;

    // Event details (from backend)
    title: string;
    datetime: string; // ISO 8601 format
    duration: number; // minutes
    location: string | null;
    org_id: string;
    role_requirements: RoleRequirement[]; // JSON array

    // Caching metadata
    cached_at: number; // Unix timestamp
    cache_expires_at: number; // Unix timestamp
    is_stale: boolean; // True if cache expired
}

interface RoleRequirement {
    role: string;
    count: number;
    required: boolean;
}
```

**Storage Size**: ~500 bytes per event
**Estimated Total**: 200 events × 500 bytes = **100 KB**

**Example Data**:
```json
{
    "id": "event_123",
    "title": "Sunday Service",
    "datetime": "2025-10-30T10:00:00Z",
    "duration": 90,
    "location": "Main Sanctuary",
    "org_id": "org_456",
    "role_requirements": [
        { "role": "Worship Leader", "count": 1, "required": true },
        { "role": "Sound Tech", "count": 1, "required": true }
    ],
    "cached_at": 1729700000000,
    "cache_expires_at": 1729703600000,
    "is_stale": false
}
```

**Queries**:
```javascript
// Get upcoming events
const now = Date.now();
const upcomingEvents = await db.getAllFromIndex(
    'events',
    'datetime',
    IDBKeyRange.lowerBound(new Date().toISOString())
);

// Get events by organization
const orgEvents = await db.getAllFromIndex(
    'events',
    'org_id',
    'org_456'
);

// Get stale events (need refresh)
const staleEvents = await db.getAll('events').then(events =>
    events.filter(e => e.is_stale || Date.now() > e.cache_expires_at)
);
```

---

### 2. Person (Cached from Backend)

**Purpose**: Store user/volunteer data for offline viewing

```typescript
interface Person {
    // Primary key
    id: string;

    // Person details (from backend)
    email: string;
    name: string;
    org_id: string;
    roles: string[]; // ["volunteer", "admin"]
    language: string; // "en", "es", "pt", etc.

    // Caching metadata
    cached_at: number;
    cache_expires_at: number;
    is_stale: boolean;
}
```

**Storage Size**: ~300 bytes per person
**Estimated Total**: 50 people × 300 bytes = **15 KB**

**Example Data**:
```json
{
    "id": "person_789",
    "email": "jane@example.com",
    "name": "Jane Doe",
    "org_id": "org_456",
    "roles": ["volunteer"],
    "language": "en",
    "cached_at": 1729700000000,
    "cache_expires_at": 1729786400000,
    "is_stale": false
}
```

**Queries**:
```javascript
// Get current user (from localStorage)
const currentUserId = localStorage.getItem('currentUser').id;
const currentUser = await db.get('people', currentUserId);

// Get all people in organization
const orgPeople = await db.getAllFromIndex('people', 'org_id', 'org_456');

// Search by email
const person = await db.getFromIndex('people', 'email', 'jane@example.com');
```

---

### 3. Availability (Cached + Locally Created)

**Purpose**: Store time-off requests, supporting offline creation

```typescript
interface Availability {
    // Primary key
    id: string;

    // Availability details
    person_id: string;
    start_date: string; // ISO 8601 date
    end_date: string; // ISO 8601 date
    reason: string | null;

    // Sync status
    is_synced: boolean; // False if created offline
    cached_at: number;
}
```

**Storage Size**: ~200 bytes per availability
**Estimated Total**: 100 availability records × 200 bytes = **20 KB**

**Example Data**:
```json
{
    "id": "avail_012",
    "person_id": "person_789",
    "start_date": "2025-11-01",
    "end_date": "2025-11-07",
    "reason": "Vacation",
    "is_synced": true,
    "cached_at": 1729700000000
}
```

**Queries**:
```javascript
// Get availability for person
const personAvailability = await db.getAllFromIndex(
    'availability',
    'person_id',
    'person_789'
);

// Get availability in date range
const startDate = '2025-11-01';
const availInRange = await db.getAllFromIndex(
    'availability',
    'start_date',
    IDBKeyRange.lowerBound(startDate)
);

// Get unsynced availability (created offline)
const unsyncedAvail = await db.getAll('availability').then(records =>
    records.filter(a => !a.is_synced)
);
```

---

### 4. EventAssignment (Cached from Backend)

**Purpose**: Store schedule assignments for offline viewing

```typescript
interface EventAssignment {
    // Primary key
    id: string;

    // Assignment details
    event_id: string;
    person_id: string;
    role: string;

    // Manual editing support
    is_locked: boolean;
    locked_at: string | null; // ISO 8601
    locked_by: string | null; // person_id

    // Caching metadata
    cached_at: number;
    is_stale: boolean;
}
```

**Storage Size**: ~250 bytes per assignment
**Estimated Total**: 500 assignments × 250 bytes = **125 KB**

**Example Data**:
```json
{
    "id": "assignment_345",
    "event_id": "event_123",
    "person_id": "person_789",
    "role": "Worship Leader",
    "is_locked": false,
    "locked_at": null,
    "locked_by": null,
    "cached_at": 1729700000000,
    "is_stale": false
}
```

**Queries**:
```javascript
// Get assignments for event
const eventAssignments = await db.getAllFromIndex(
    'assignments',
    'event_id',
    'event_123'
);

// Get assignments for person (my schedule)
const myAssignments = await db.getAllFromIndex(
    'assignments',
    'person_id',
    'person_789'
);

// Get locked assignments
const lockedAssignments = await db.getAll('assignments').then(assignments =>
    assignments.filter(a => a.is_locked)
);
```

---

### 5. Team (Cached from Backend)

**Purpose**: Store team data for offline viewing

```typescript
interface Team {
    // Primary key
    id: string;

    // Team details
    name: string;
    org_id: string;
    role: string;
    members: string[]; // Array of person_ids

    // Caching metadata
    cached_at: number;
    cache_expires_at: number;
    is_stale: boolean;
}
```

**Storage Size**: ~400 bytes per team
**Estimated Total**: 10 teams × 400 bytes = **4 KB**

**Example Data**:
```json
{
    "id": "team_678",
    "name": "Worship Team",
    "org_id": "org_456",
    "role": "Worship Leader",
    "members": ["person_789", "person_012", "person_345"],
    "cached_at": 1729700000000,
    "cache_expires_at": 1729786400000,
    "is_stale": false
}
```

**Queries**:
```javascript
// Get teams for organization
const orgTeams = await db.getAllFromIndex('teams', 'org_id', 'org_456');

// Get teams for person
const personTeams = await db.getAll('teams').then(teams =>
    teams.filter(t => t.members.includes('person_789'))
);
```

---

### 6. PendingAction (Offline Queue)

**Purpose**: Queue actions performed offline for background sync

```typescript
interface PendingAction {
    // Primary key (auto-increment)
    id: number;

    // Action details
    action_type: 'add_availability' | 'update_profile' | 'delete_availability';
    endpoint: string; // API endpoint to call
    method: 'POST' | 'PUT' | 'DELETE';
    body: any; // JSON payload

    // Sync metadata
    timestamp: number; // When action was queued
    status: 'pending' | 'syncing' | 'failed';
    retry_count: number;
    last_error: string | null;
    max_retries: number; // Default 3
}
```

**Storage Size**: ~500 bytes per action
**Estimated Total**: 50 pending actions × 500 bytes = **25 KB**

**Example Data**:
```json
{
    "id": 1,
    "action_type": "add_availability",
    "endpoint": "/api/availability?org_id=org_456",
    "method": "POST",
    "body": {
        "person_id": "person_789",
        "start_date": "2025-11-01",
        "end_date": "2025-11-07",
        "reason": "Vacation"
    },
    "timestamp": 1729700000000,
    "status": "pending",
    "retry_count": 0,
    "last_error": null,
    "max_retries": 3
}
```

**Queries**:
```javascript
// Get pending actions
const pendingActions = await db.getAllFromIndex(
    'pending_actions',
    'status',
    'pending'
);

// Get failed actions
const failedActions = await db.getAllFromIndex(
    'pending_actions',
    'status',
    'failed'
);

// Get actions by type
const availActions = await db.getAllFromIndex(
    'pending_actions',
    'action_type',
    'add_availability'
);
```

---

### 7. CacheMetadata (System Info)

**Purpose**: Track cache state and sync timestamps

```typescript
interface CacheMetadata {
    // Primary key
    key: string; // e.g., 'events_last_sync', 'people_last_sync'

    // Metadata
    last_sync: number; // Unix timestamp
    sync_status: 'idle' | 'syncing' | 'error';
    error_message: string | null;
    next_sync: number | null; // Scheduled next sync time
}
```

**Storage Size**: ~150 bytes per entry
**Estimated Total**: 10 metadata entries × 150 bytes = **1.5 KB**

**Example Data**:
```json
{
    "key": "events_last_sync",
    "last_sync": 1729700000000,
    "sync_status": "idle",
    "error_message": null,
    "next_sync": 1729703600000
}
```

**Queries**:
```javascript
// Check last sync time
const eventsMeta = await db.get('cache_metadata', 'events_last_sync');
const hoursSinceSync = (Date.now() - eventsMeta.last_sync) / (1000 * 60 * 60);

// Check if sync is in progress
const syncingMeta = await db.getAll('cache_metadata').then(entries =>
    entries.filter(e => e.sync_status === 'syncing')
);
```

---

## Sync Patterns

### Initial Cache (On First Load)

```javascript
async function cacheInitialData(orgId) {
    const db = await initOfflineDB();

    // Fetch data from backend
    const [events, people, availability, assignments, teams] = await Promise.all([
        authFetch(`/api/events/?org_id=${orgId}`).then(r => r.json()),
        authFetch(`/api/people/?org_id=${orgId}`).then(r => r.json()),
        authFetch(`/api/availability/?org_id=${orgId}`).then(r => r.json()),
        authFetch(`/api/events/assignments?org_id=${orgId}`).then(r => r.json()),
        authFetch(`/api/teams/?org_id=${orgId}`).then(r => r.json())
    ]);

    // Cache to IndexedDB
    const tx = db.transaction(
        ['events', 'people', 'availability', 'assignments', 'teams'],
        'readwrite'
    );

    await Promise.all([
        ...events.map(e => tx.objectStore('events').put({
            ...e,
            cached_at: Date.now(),
            cache_expires_at: Date.now() + (60 * 60 * 1000), // 1 hour
            is_stale: false
        })),
        ...people.map(p => tx.objectStore('people').put({
            ...p,
            cached_at: Date.now(),
            cache_expires_at: Date.now() + (24 * 60 * 60 * 1000), // 24 hours
            is_stale: false
        })),
        ...availability.map(a => tx.objectStore('availability').put({
            ...a,
            is_synced: true,
            cached_at: Date.now()
        })),
        ...assignments.map(a => tx.objectStore('assignments').put({
            ...a,
            cached_at: Date.now(),
            is_stale: false
        })),
        ...teams.map(t => tx.objectStore('teams').put({
            ...t,
            cached_at: Date.now(),
            cache_expires_at: Date.now() + (24 * 60 * 60 * 1000), // 24 hours
            is_stale: false
        }))
    ]);

    await tx.done;

    // Update metadata
    await db.put('cache_metadata', {
        key: 'initial_cache_complete',
        last_sync: Date.now(),
        sync_status: 'idle',
        error_message: null,
        next_sync: null
    });
}
```

### Periodic Sync (Background Refresh)

```javascript
async function periodicSync() {
    if (!navigator.onLine) return;

    const db = await initOfflineDB();

    // Check if sync needed (stale data)
    const eventsMeta = await db.get('cache_metadata', 'events_last_sync');
    const hoursSinceSync = (Date.now() - (eventsMeta?.last_sync || 0)) / (1000 * 60 * 60);

    if (hoursSinceSync < 1) return; // Skip if synced within 1 hour

    // Sync events
    const orgId = JSON.parse(localStorage.getItem('currentOrg')).id;
    const events = await authFetch(`/api/events/?org_id=${orgId}`).then(r => r.json());

    const tx = db.transaction('events', 'readwrite');
    await Promise.all(events.map(e => tx.objectStore('events').put({
        ...e,
        cached_at: Date.now(),
        cache_expires_at: Date.now() + (60 * 60 * 1000),
        is_stale: false
    })));
    await tx.done;

    // Update metadata
    await db.put('cache_metadata', {
        key: 'events_last_sync',
        last_sync: Date.now(),
        sync_status: 'idle',
        error_message: null,
        next_sync: Date.now() + (60 * 60 * 1000)
    });
}

// Register periodic sync (Service Worker)
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'refresh-cache') {
        event.waitUntil(periodicSync());
    }
});
```

### Offline Action Sync (On Reconnect)

```javascript
async function syncPendingActions() {
    const db = await initOfflineDB();
    const pendingActions = await db.getAllFromIndex(
        'pending_actions',
        'status',
        'pending'
    );

    for (const action of pendingActions) {
        try {
            // Mark as syncing
            await db.put('pending_actions', {
                ...action,
                status: 'syncing'
            });

            // Execute action
            const response = await authFetch(action.endpoint, {
                method: action.method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(action.body)
            });

            if (response.ok) {
                // Success - remove from queue
                await db.delete('pending_actions', action.id);

                // Update cached data if needed
                const data = await response.json();
                if (action.action_type === 'add_availability') {
                    await db.put('availability', {
                        ...data,
                        is_synced: true,
                        cached_at: Date.now()
                    });
                }
            } else {
                // Failed - increment retry count
                await db.put('pending_actions', {
                    ...action,
                    status: 'pending',
                    retry_count: action.retry_count + 1,
                    last_error: await response.text()
                });
            }
        } catch (error) {
            // Network error - mark as failed if max retries exceeded
            if (action.retry_count >= action.max_retries) {
                await db.put('pending_actions', {
                    ...action,
                    status: 'failed',
                    last_error: error.message
                });
            } else {
                await db.put('pending_actions', {
                    ...action,
                    status: 'pending',
                    retry_count: action.retry_count + 1,
                    last_error: error.message
                });
            }
        }
    }
}

// Listen for online event
window.addEventListener('online', syncPendingActions);
```

---

## Storage Estimates

| Store | Records | Size/Record | Total Size |
|-------|---------|-------------|------------|
| Events | 200 | 500 bytes | 100 KB |
| People | 50 | 300 bytes | 15 KB |
| Availability | 100 | 200 bytes | 20 KB |
| Assignments | 500 | 250 bytes | 125 KB |
| Teams | 10 | 400 bytes | 4 KB |
| Pending Actions | 50 | 500 bytes | 25 KB |
| Cache Metadata | 10 | 150 bytes | 1.5 KB |
| **Total** | **920** | - | **290.5 KB** |

**Total Offline Storage**: ~290 KB (well within 50MB IndexedDB limit)

---

## Cache Expiration Strategy

| Data Type | Cache Duration | Rationale |
|-----------|---------------|-----------|
| Events | 1 hour | Frequently updated (assignments, changes) |
| People | 24 hours | Rarely changes (names, emails) |
| Availability | 6 hours | Moderately updated (new time-off requests) |
| Assignments | 1 hour | Frequently updated (schedule changes) |
| Teams | 24 hours | Rarely changes (team membership) |

---

## Migration Strategy

**Version 1 → Version 2** (future):
```javascript
export async function migrateV1toV2(db, transaction) {
    // Example: Add new field to events
    const eventsStore = transaction.objectStore('events');
    const events = await eventsStore.getAll();

    for (const event of events) {
        event.is_recurring = false; // New field
        await eventsStore.put(event);
    }
}
```

---

**Last Updated**: 2025-10-23
**Feature**: 018 - Mobile Responsive Design
**Total Storage**: ~290 KB for 920 records
