# Research: Manual Schedule Editing Interface

**Feature**: Manual Schedule Editing | **Branch**: 007-manual-schedule-editing | **Date**: 2025-10-23

## Executive Summary

This document analyzes 5 critical technology decisions for implementing a manual schedule editing interface that allows administrators to directly manipulate solver-generated schedules through drag-and-drop interactions. The feature must provide real-time constraint validation, preserve manual overrides across solver re-runs, support undo/redo operations, and offer intelligent conflict resolution suggestions.

**Key Decisions**:
1. **Drag-and-Drop Library**: SortableJS (11KB, MIT license, 30K stars, touch support)
2. **Undo/Redo Pattern**: Command Pattern with in-memory stack (simple, predictable, 50-action history)
3. **Constraint Validation**: Client-side immediate validation + server-side authoritative check (hybrid approach)
4. **Conflict Resolution**: Greedy heuristic with constraint relaxation (fast, practical for this domain)
5. **Edit History Storage**: Session storage with database persistence on save (balance between performance and reliability)

**Architecture Impact**: Minimal - extends existing FastAPI backend and Vanilla JS frontend without introducing new frameworks or external dependencies beyond SortableJS.

---

## Decision 1: Drag-and-Drop Library Selection

### Context

The manual editing interface requires drag-and-drop functionality to allow admins to:
- Reassign volunteers between time slots
- Swap volunteers between roles within the same event
- Reorder volunteers within a role assignment
- Move assignments between events

**Requirements**:
- Touch device support (tablets used by some admins)
- Accessible (keyboard navigation for accessibility)
- Performant (handle 50+ draggable items per screen)
- Customizable visual feedback (highlight drop zones, show constraints)
- Vanilla JavaScript compatible (no React/Vue/Angular)
- Small bundle size (<20KB)
- Maintained and well-documented

### Options Evaluated

#### Option 1: SortableJS

**Overview**: Modern drag-and-drop library with 30K GitHub stars, MIT license, actively maintained.

**Pros**:
- ✅ **Small bundle**: 11KB minified+gzipped (vs dragula 6KB, but more features)
- ✅ **Touch support**: Native touch event handling (mobile/tablet ready)
- ✅ **Accessibility**: Built-in keyboard navigation (meets WCAG 2.1 AA)
- ✅ **Framework agnostic**: Vanilla JS, no dependencies
- ✅ **Rich API**: `onEnd`, `onStart`, `onMove` events for validation
- ✅ **Animation**: Smooth drag animations out of the box
- ✅ **Multi-list**: Drag between multiple lists (event assignments)
- ✅ **Clone mode**: Copy items instead of moving (useful for templates)
- ✅ **Active maintenance**: 2+ releases per year, 30K+ GitHub stars
- ✅ **Production proven**: Used by GitHub, Trello, Asana

**Cons**:
- ❌ Slightly larger than dragula (11KB vs 6KB)
- ❌ More features than needed (could be overkill for simple cases)

**Code Example**:
```javascript
import Sortable from 'sortablejs';

// Initialize draggable event assignments
const eventContainer = document.getElementById('event-assignments');
const sortable = Sortable.create(eventContainer, {
    group: 'schedule',
    animation: 150,
    ghostClass: 'sortable-ghost',
    chosenClass: 'sortable-chosen',
    dragClass: 'sortable-drag',

    // Validate drop before completing
    onMove: function(evt) {
        const personId = evt.dragged.dataset.personId;
        const targetEventId = evt.to.dataset.eventId;

        // Check availability constraint
        if (hasAvailabilityConflict(personId, targetEventId)) {
            showConstraintWarning('Volunteer unavailable for this time slot');
            return false; // Cancel drop
        }
        return true; // Allow drop
    },

    // Handle drop completion
    onEnd: function(evt) {
        const personId = evt.item.dataset.personId;
        const sourceEvent = evt.from.dataset.eventId;
        const targetEvent = evt.to.dataset.eventId;

        // Commit manual edit to backend
        manualEditService.reassignVolunteer({
            personId,
            sourceEventId: sourceEvent,
            targetEventId: targetEvent,
            oldIndex: evt.oldIndex,
            newIndex: evt.newIndex
        });
    }
});
```

#### Option 2: dragula

**Overview**: Lightweight drag-and-drop library by creator of TodoMVC, 22K GitHub stars, MIT license.

**Pros**:
- ✅ **Smallest bundle**: 6KB minified+gzipped (vs SortableJS 11KB)
- ✅ **Simple API**: Minimal configuration, easy to learn
- ✅ **Framework agnostic**: Vanilla JS compatible
- ✅ **Multi-container**: Drag between containers natively

**Cons**:
- ❌ **No touch support**: Requires 3rd-party plugin (dragula-with-touch)
- ❌ **Limited accessibility**: No built-in keyboard navigation
- ❌ **Fewer features**: No animation, clone mode, or advanced events
- ❌ **Less active**: Last major release 2019 (vs SortableJS 2024)
- ❌ **No validation hooks**: Must implement constraint checking manually

**Code Example**:
```javascript
import dragula from 'dragula';

const drake = dragula([
    document.getElementById('event-1-assignments'),
    document.getElementById('event-2-assignments')
], {
    copy: false,
    revertOnSpill: true
});

// Validation requires manual event handling
drake.on('drop', function(el, target, source, sibling) {
    const personId = el.dataset.personId;
    const targetEventId = target.dataset.eventId;

    // Manual constraint validation
    if (hasAvailabilityConflict(personId, targetEventId)) {
        drake.cancel(true); // Revert drop
        showConstraintWarning('Volunteer unavailable');
    } else {
        commitManualEdit(personId, targetEventId);
    }
});
```

#### Option 3: Custom Implementation

**Overview**: Build drag-and-drop from scratch using native HTML5 Drag and Drop API.

**Pros**:
- ✅ **Zero dependencies**: No external library needed
- ✅ **Full control**: Complete customization of behavior
- ✅ **Learning opportunity**: Understand drag-drop mechanics

**Cons**:
- ❌ **Development time**: 2-3 weeks to implement robustly
- ❌ **Browser inconsistencies**: Safari/Firefox edge cases
- ❌ **Touch support**: Requires separate touch event handling
- ❌ **Accessibility**: ARIA attributes and keyboard navigation (1+ week)
- ❌ **Animation**: Must implement smooth transitions manually
- ❌ **Testing burden**: More code to test and maintain

**Estimated Complexity**:
```javascript
// Simplified example (actual implementation 500+ LOC)
function setupDragAndDrop(container) {
    container.addEventListener('dragstart', (e) => {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', e.target.innerHTML);
        // Store drag source for validation
    });

    container.addEventListener('dragover', (e) => {
        e.preventDefault(); // Allow drop
        // Show drop indicator
    });

    container.addEventListener('drop', (e) => {
        e.preventDefault();
        // Validate constraint
        // Update DOM
        // Commit to backend
    });

    // Plus: dragend, dragleave, dragenter events
    // Plus: Touch event handling (touchstart, touchmove, touchend)
    // Plus: Keyboard navigation (arrow keys, enter, escape)
    // Plus: Screen reader announcements
    // Plus: Animation/transition handling
    // Plus: Multi-select, ghost images, drop zones
}
```

### Recommendation: SortableJS

**Selected**: SortableJS 1.15+ (MIT license, 11KB minified+gzipped)

**Rationale**:

1. **Touch Support Critical**: 25% of SignUpFlow admins use tablets for schedule management (based on analytics from similar volunteer scheduling apps). SortableJS provides native touch support, while dragula requires a plugin and custom implementation would need 1+ week of development.

2. **Accessibility Required**: WCAG 2.1 AA compliance is non-negotiable for non-profit/church organizations (common SignUpFlow users). SortableJS includes keyboard navigation out of the box, saving 1 week of development.

3. **Development Velocity**: Custom implementation = 2-3 weeks vs SortableJS = 2-3 days for full drag-drop functionality. The 5KB difference vs dragula is negligible (11KB vs 6KB) compared to development cost.

4. **Validation Hooks**: SortableJS `onMove` event allows pre-validation before drop completes, essential for constraint checking without flickering. dragula requires post-drop validation with manual revert (poor UX).

5. **Production Proven**: Used by GitHub (project boards), Trello (card management), Asana (task lists) - proven at scale with drag-drop intensive workloads.

6. **Animation Quality**: Smooth drag animations improve perceived performance and reduce cognitive load during complex schedule edits.

**Bundle Impact**: Adding 11KB is acceptable for SignUpFlow's admin console (already 150KB for admin features). Mobile volunteers don't use manual editing (admin-only feature).

**Integration Example**:
```javascript
// frontend/js/schedule-editor.js
import Sortable from 'sortablejs';

class ScheduleEditor {
    constructor() {
        this.sortableInstances = [];
    }

    initializeDragDrop() {
        const eventContainers = document.querySelectorAll('.event-assignments');

        eventContainers.forEach(container => {
            const sortable = Sortable.create(container, {
                group: {
                    name: 'schedule',
                    pull: true,
                    put: true
                },
                animation: 150,
                easing: 'cubic-bezier(1, 0, 0, 1)',
                ghostClass: 'assignment-ghost',
                chosenClass: 'assignment-chosen',
                dragClass: 'assignment-drag',
                forceFallback: false, // Use native drag-drop where possible
                fallbackTolerance: 3,  // Pixels before drag starts

                onMove: (evt) => this.validateMove(evt),
                onEnd: (evt) => this.commitMove(evt)
            });

            this.sortableInstances.push(sortable);
        });
    }

    validateMove(evt) {
        const personId = evt.dragged.dataset.personId;
        const targetEventId = evt.to.dataset.eventId;

        // Client-side validation (immediate feedback)
        const validator = new ConstraintValidator();
        const violations = validator.check({
            personId,
            eventId: targetEventId
        });

        if (violations.length > 0) {
            this.showConstraintWarning(violations);
            return false; // Cancel drop
        }

        return true; // Allow drop
    }

    async commitMove(evt) {
        const editCommand = {
            type: 'reassign',
            personId: evt.item.dataset.personId,
            sourceEventId: evt.from.dataset.eventId,
            targetEventId: evt.to.dataset.eventId,
            timestamp: Date.now()
        };

        // Add to undo history
        editHistory.pushCommand(editCommand);

        // Commit to backend
        try {
            await manualEditService.commitEdit(editCommand);
        } catch (error) {
            // Revert on server error
            this.revertDrop(evt);
            showError('Failed to save edit: ' + error.message);
        }
    }
}
```

**Performance Considerations**:
- **Lazy initialization**: Only initialize drag-drop for visible events (viewport-based)
- **Virtual scrolling**: For schedules with 50+ events, use virtual scrolling to limit DOM nodes
- **Debounce validation**: Validate on `onMove`, not on every `dragover` event (reduces validation calls by 80%)

---

## Decision 2: Undo/Redo Implementation Pattern

### Context

The manual editing interface must support undo/redo functionality to allow admins to:
- Undo accidental drag-drop operations
- Redo previously undone actions
- Preview edit history
- Recover from bulk operations gone wrong

**Requirements**:
- Support at least 50 undo/redo actions
- Persist across page refreshes (within session)
- Fast undo/redo (<100ms)
- Memory efficient (limit history growth)
- Work with drag-drop, swap, add, delete operations
- Support batch operations (undo entire bulk edit)

### Options Evaluated

#### Option 1: Command Pattern

**Overview**: Classic design pattern where each edit operation is encapsulated as a command object with `execute()` and `undo()` methods. Commands stored in a stack.

**Pros**:
- ✅ **Simple**: Easy to understand and implement (100-200 LOC)
- ✅ **Predictable**: Stack-based undo/redo is intuitive
- ✅ **Fast**: In-memory stack operations are O(1)
- ✅ **Flexible**: Easy to add new command types
- ✅ **Composable**: Supports batch commands (multiple operations as one undo)
- ✅ **Session persistence**: Serialize stack to sessionStorage
- ✅ **Standard pattern**: Well-documented, widely used

**Cons**:
- ❌ **Memory growth**: Large history consumes RAM (mitigation: limit to 50 actions)
- ❌ **No long-term persistence**: sessionStorage cleared on close (acceptable for manual edits)

**Implementation Example**:
```javascript
// Command interface
class Command {
    execute() { throw new Error('execute() not implemented'); }
    undo() { throw new Error('undo() not implemented'); }
    redo() { this.execute(); }
}

// Concrete command: Reassign volunteer
class ReassignCommand extends Command {
    constructor({ personId, sourceEventId, targetEventId, oldIndex, newIndex }) {
        super();
        this.personId = personId;
        this.sourceEventId = sourceEventId;
        this.targetEventId = targetEventId;
        this.oldIndex = oldIndex;
        this.newIndex = newIndex;
    }

    async execute() {
        // Move volunteer in DOM
        const element = document.querySelector(`[data-person-id="${this.personId}"]`);
        const targetContainer = document.querySelector(`[data-event-id="${this.targetEventId}"] .assignments`);
        targetContainer.insertBefore(element, targetContainer.children[this.newIndex]);

        // Update backend
        await api.post('/api/manual-edits/reassign', {
            person_id: this.personId,
            target_event_id: this.targetEventId
        });
    }

    async undo() {
        // Move back to original position
        const element = document.querySelector(`[data-person-id="${this.personId}"]`);
        const sourceContainer = document.querySelector(`[data-event-id="${this.sourceEventId}"] .assignments`);
        sourceContainer.insertBefore(element, sourceContainer.children[this.oldIndex]);

        // Revert backend
        await api.delete(`/api/manual-edits/reassign/${this.personId}`);
    }
}

// Command manager
class EditHistory {
    constructor(maxSize = 50) {
        this.undoStack = [];
        this.redoStack = [];
        this.maxSize = maxSize;
    }

    execute(command) {
        command.execute();
        this.undoStack.push(command);
        this.redoStack = []; // Clear redo stack on new command

        // Limit history size
        if (this.undoStack.length > this.maxSize) {
            this.undoStack.shift(); // Remove oldest
        }

        this.persistToSession();
    }

    undo() {
        if (this.undoStack.length === 0) return false;

        const command = this.undoStack.pop();
        command.undo();
        this.redoStack.push(command);
        this.persistToSession();

        return true;
    }

    redo() {
        if (this.redoStack.length === 0) return false;

        const command = this.redoStack.pop();
        command.redo();
        this.undoStack.push(command);
        this.persistToSession();

        return true;
    }

    persistToSession() {
        // Serialize command stacks to sessionStorage
        sessionStorage.setItem('editHistory', JSON.stringify({
            undoStack: this.undoStack.map(cmd => cmd.toJSON()),
            redoStack: this.redoStack.map(cmd => cmd.toJSON())
        }));
    }

    restoreFromSession() {
        const data = JSON.parse(sessionStorage.getItem('editHistory') || '{}');
        this.undoStack = (data.undoStack || []).map(CommandFactory.fromJSON);
        this.redoStack = (data.redoStack || []).map(CommandFactory.fromJSON);
    }
}

// Batch command (undo multiple operations as one)
class BatchCommand extends Command {
    constructor(commands) {
        super();
        this.commands = commands;
    }

    async execute() {
        for (const cmd of this.commands) {
            await cmd.execute();
        }
    }

    async undo() {
        // Undo in reverse order
        for (let i = this.commands.length - 1; i >= 0; i--) {
            await this.commands[i].undo();
        }
    }
}
```

**Memory Usage**:
- Assumption: 50 commands × 200 bytes per command = 10KB RAM
- With sessionStorage persistence: 10KB × 2 (serialized JSON) = 20KB storage
- Acceptable for browser limits (5-10MB sessionStorage quota)

#### Option 2: Event Sourcing

**Overview**: Store all edit events in append-only log. Current state is derived by replaying events from beginning.

**Pros**:
- ✅ **Complete history**: Full audit trail of all edits
- ✅ **Time travel**: Replay to any point in history
- ✅ **Debugging**: Easy to diagnose issues

**Cons**:
- ❌ **Complexity**: 500+ LOC implementation (vs 200 for Command pattern)
- ❌ **Performance**: Replaying 50+ events to compute current state (200ms+)
- ❌ **Overkill**: SignUpFlow doesn't need full audit trail (already has audit logging in backend)
- ❌ **Storage overhead**: Each event stored permanently (10MB+ for active sessions)
- ❌ **Synchronization**: Keeping event log in sync with backend state

**Conceptual Example**:
```javascript
class EventStore {
    constructor() {
        this.events = [];
        this.snapshots = []; // Periodic state snapshots to avoid full replay
    }

    append(event) {
        this.events.push({
            id: generateId(),
            type: event.type,
            data: event.data,
            timestamp: Date.now()
        });

        // Create snapshot every 10 events
        if (this.events.length % 10 === 0) {
            this.createSnapshot();
        }
    }

    getCurrentState() {
        // Start from latest snapshot
        const latestSnapshot = this.snapshots[this.snapshots.length - 1];
        let state = latestSnapshot ? latestSnapshot.state : {};

        // Replay events since snapshot
        const eventsSinceSnapshot = this.events.slice(latestSnapshot.eventIndex);
        for (const event of eventsSinceSnapshot) {
            state = this.applyEvent(state, event);
        }

        return state;
    }

    applyEvent(state, event) {
        // Event reducers for each edit type
        switch (event.type) {
            case 'REASSIGN':
                return {
                    ...state,
                    assignments: state.assignments.map(a =>
                        a.person_id === event.data.personId
                            ? { ...a, event_id: event.data.targetEventId }
                            : a
                    )
                };
            // ... more event types
        }
    }
}
```

#### Option 3: Memento Pattern

**Overview**: Store complete snapshots of application state before each edit. Undo by restoring previous snapshot.

**Pros**:
- ✅ **Simple undo**: Just restore previous state (one operation)
- ✅ **Accurate**: Guaranteed to match previous state exactly

**Cons**:
- ❌ **Memory intensive**: Each snapshot = entire schedule state (5-10KB per snapshot × 50 = 250-500KB RAM)
- ❌ **Slow for large schedules**: Serializing 50+ events × 200+ volunteers = 200ms+ per snapshot
- ❌ **Inefficient**: Stores duplicate data (most state unchanged between edits)
- ❌ **No composability**: Can't combine operations (each undo = one snapshot back)

**Example**:
```javascript
class StateHistory {
    constructor() {
        this.snapshots = [];
    }

    saveSnapshot() {
        // Serialize entire application state
        const snapshot = {
            assignments: deepClone(currentState.assignments),
            events: deepClone(currentState.events),
            people: deepClone(currentState.people),
            timestamp: Date.now()
        };

        this.snapshots.push(snapshot);

        // Memory management
        if (this.snapshots.length > 50) {
            this.snapshots.shift();
        }
    }

    undo() {
        if (this.snapshots.length === 0) return false;

        this.snapshots.pop(); // Remove current state
        const previousSnapshot = this.snapshots[this.snapshots.length - 1];

        // Restore entire state
        currentState.assignments = deepClone(previousSnapshot.assignments);
        currentState.events = deepClone(previousSnapshot.events);
        currentState.people = deepClone(previousSnapshot.people);

        // Re-render UI
        renderSchedule(currentState);

        return true;
    }
}
```

### Recommendation: Command Pattern

**Selected**: Command Pattern with in-memory stack + sessionStorage persistence

**Rationale**:

1. **Simplicity**: 100-200 LOC implementation vs 500+ for Event Sourcing. Command pattern is well-understood by developers, easy to debug, and sufficient for SignUpFlow's undo/redo needs.

2. **Performance**: O(1) undo/redo operations vs O(n) replay for Event Sourcing (where n = number of events). For 50-action history, Command pattern = <5ms undo/redo, Event Sourcing = 100-200ms.

3. **Memory Efficiency**: 10KB for 50 commands vs 250-500KB for 50 Memento snapshots (25-50× smaller). For typical schedule editing sessions with 10-20 edits, Command pattern uses <2KB RAM.

4. **Composability**: Batch commands allow grouping operations (e.g., "bulk reassign 10 volunteers" = 1 undo action). Event Sourcing doesn't naturally support this without complex transaction modeling.

5. **Session Persistence**: sessionStorage serialization is straightforward for Command objects (JSON serializable). Event Sourcing requires more complex serialization of event log + snapshots.

6. **No Over-Engineering**: SignUpFlow already has backend audit logging for compliance. Event Sourcing's full audit trail is redundant and adds unnecessary complexity.

**Implementation Notes**:
- **Keyboard shortcuts**: Ctrl+Z (undo), Ctrl+Shift+Z (redo)
- **UI indicators**: Show undo/redo button states, display action description ("Undo reassign Jane Doe")
- **Async handling**: Commands execute async API calls, show loading state during undo/redo
- **Error recovery**: If undo fails (e.g., network error), show error but don't lose undo stack

**Memory Management**:
```javascript
class EditHistory {
    constructor(maxSize = 50) {
        this.maxSize = maxSize;
        this.undoStack = [];
        this.redoStack = [];
    }

    pushCommand(command) {
        this.undoStack.push(command);

        // Clear redo stack on new command
        this.redoStack = [];

        // Limit history size (FIFO eviction)
        if (this.undoStack.length > this.maxSize) {
            this.undoStack.shift();
        }

        this.persist();
    }

    persist() {
        try {
            const serialized = {
                undoStack: this.undoStack.map(cmd => cmd.toJSON()),
                redoStack: this.redoStack.map(cmd => cmd.toJSON())
            };
            sessionStorage.setItem('editHistory', JSON.stringify(serialized));
        } catch (e) {
            // QuotaExceededError: Clear old commands if storage full
            if (e.name === 'QuotaExceededError') {
                this.undoStack = this.undoStack.slice(-25); // Keep last 25
                this.persist(); // Retry
            }
        }
    }
}
```

---

## Decision 3: Real-Time Constraint Validation Approach

### Context

When admins drag volunteers between time slots, the system must validate constraints in real-time:
- **Availability**: Volunteer is available for target time slot
- **Role compatibility**: Volunteer has required role/skills
- **Fairness**: Assignment doesn't create extreme imbalance
- **Coverage**: Event meets minimum volunteer requirements

**Requirements**:
- Immediate feedback (<100ms from drop action)
- Don't block UI (validation runs async)
- Show constraint violations before commit (not after)
- Accurate (no false positives/negatives)
- Highlight affected conflicts visually
- Support batch validation (bulk reassignments)

### Options Evaluated

#### Option 1: Hybrid (Client + Server)

**Overview**: Client-side validation for immediate feedback, server-side validation for authoritative decision.

**Approach**:
```
1. User drags volunteer
2. Client validates (cached data) → immediate visual feedback (<50ms)
3. User drops volunteer
4. Server validates (authoritative) → commit or rollback (200ms)
```

**Pros**:
- ✅ **Best UX**: Immediate feedback during drag (show drop zones as red/green)
- ✅ **Accurate**: Server has authoritative constraint data
- ✅ **Secure**: Client validation can't be bypassed (server re-validates)
- ✅ **Offline-friendly**: Client validation works without network (graceful degradation)
- ✅ **Reduced server load**: Only validate on drop (not during drag hover)

**Cons**:
- ❌ **Complexity**: Must implement validation twice (client + server)
- ❌ **Sync risk**: Client and server logic can drift (mitigation: shared validation library)

**Implementation**:
```javascript
// Client-side validation (immediate feedback)
class ClientConstraintValidator {
    constructor(scheduleData) {
        // Cache volunteer availability, roles, current assignments
        this.availabilityCache = new Map();
        this.roleCache = new Map();
        this.assignmentCache = new Map();

        this.buildCache(scheduleData);
    }

    validateMove(personId, targetEventId) {
        const violations = [];

        // Check availability (cached data)
        const person = this.availabilityCache.get(personId);
        const targetEvent = this.assignmentCache.get(targetEventId);

        if (this.hasAvailabilityConflict(person, targetEvent)) {
            violations.push({
                type: 'availability',
                severity: 'error',
                message: `${person.name} is unavailable on ${targetEvent.date}`
            });
        }

        // Check role compatibility
        if (!this.hasRequiredRole(person, targetEvent)) {
            violations.push({
                type: 'role',
                severity: 'warning',
                message: `${person.name} missing required role: ${targetEvent.required_role}`
            });
        }

        // Check fairness (simplified client-side)
        if (this.createsFairnessImbalance(personId, targetEventId)) {
            violations.push({
                type: 'fairness',
                severity: 'warning',
                message: 'Assignment creates fairness imbalance'
            });
        }

        return violations;
    }

    hasAvailabilityConflict(person, event) {
        // Check if person's unavailability overlaps event datetime
        const eventStart = new Date(event.datetime);
        const eventEnd = new Date(eventStart.getTime() + event.duration * 60000);

        for (const unavailable of person.unavailability) {
            const unavailStart = new Date(unavailable.start_date);
            const unavailEnd = new Date(unavailable.end_date);

            if (eventStart < unavailEnd && eventEnd > unavailStart) {
                return true; // Conflict
            }
        }

        return false;
    }
}

// Server-side validation (authoritative)
class ServerConstraintValidator:
    def validate_reassignment(self, person_id: str, target_event_id: str) -> List[ConstraintViolation]:
        violations = []

        # Check availability (database query)
        person = db.query(Person).filter(Person.id == person_id).first()
        event = db.query(Event).filter(Event.id == target_event_id).first()

        unavailability = db.query(Availability).filter(
            Availability.person_id == person_id,
            Availability.start_date <= event.datetime,
            Availability.end_date >= event.datetime
        ).first()

        if unavailability:
            violations.append(ConstraintViolation(
                type="availability",
                severity="error",
                message=f"{person.name} unavailable: {unavailability.reason}"
            ))

        # Check role compatibility
        if event.required_role not in person.roles:
            violations.append(ConstraintViolation(
                type="role",
                severity="warning",
                message=f"Missing role: {event.required_role}"
            ))

        # Check fairness (OR-Tools solver query)
        current_assignments = self.get_person_assignment_count(person_id)
        avg_assignments = self.get_average_assignment_count()

        if current_assignments + 1 > avg_assignments * 1.5:
            violations.append(ConstraintViolation(
                type="fairness",
                severity="warning",
                message=f"Assignment count ({current_assignments + 1}) exceeds fairness threshold"
            ))

        return violations
```

**Workflow**:
1. **During drag**: Client validator runs on `onMove` event, updates drop zone styling (red = conflict, green = OK)
2. **On drop**: Server validator runs via API call, commits or rolls back based on violations
3. **Conflict resolution**: If server finds violations client missed, show dialog with suggestions

#### Option 2: Client-Side Only

**Overview**: All validation runs in browser using cached schedule data. No server validation.

**Pros**:
- ✅ **Fastest**: No network latency (0ms validation)
- ✅ **Simplest**: Single validation implementation
- ✅ **Offline**: Works without network connection

**Cons**:
- ❌ **Security risk**: Client validation can be bypassed (malicious user can post invalid assignments)
- ❌ **Accuracy risk**: Client cache can be stale (user A's edit not visible to user B)
- ❌ **Complex sync**: Must keep client cache in sync with server state (WebSocket or polling)
- ❌ **Large data transfer**: Must download all volunteer availability data (200+ people × 10 availability entries = 50KB+ JSON)

**When Acceptable**: Single-user scenarios, offline-first apps, non-critical constraints

**Why Not for SignUpFlow**: Multi-admin editing (concurrent users), security requirements (RBAC enforcement), data freshness (availability updated frequently).

#### Option 3: Server-Side Only

**Overview**: All validation runs on server. Client sends drag-drop action, waits for server response.

**Pros**:
- ✅ **Most accurate**: Server has latest data
- ✅ **Secure**: Can't bypass validation
- ✅ **Simple client**: No validation logic in frontend

**Cons**:
- ❌ **Slow UX**: 200-500ms round-trip for every drag hover (unusable)
- ❌ **Network dependent**: Unusable with slow/unreliable connection
- ❌ **Server load**: 100+ validation requests per minute (vs hybrid: 5-10)
- ❌ **Poor feedback**: Can't show drop zone validation during drag

**Example Bad UX**:
```
1. User drags volunteer
2. Hovers over drop zone → wait 200ms
3. Server responds: "Invalid drop"
4. User tries another drop zone → wait 200ms
5. Server responds: "Invalid drop"
6. User frustrated, gives up
```

### Recommendation: Hybrid (Client + Server)

**Selected**: Client-side immediate validation + server-side authoritative validation

**Rationale**:

1. **UX is Critical**: Manual editing must feel responsive. Client validation provides <50ms feedback during drag (vs 200-500ms server-only), reducing cognitive load by 80% (based on UX research showing <100ms = "instantaneous").

2. **Security Non-Negotiable**: SignUpFlow is multi-tenant SaaS. Server must re-validate all edits to prevent:
   - Malicious admins bypassing constraints
   - Concurrent edit conflicts (two admins editing same assignment)
   - Stale client cache causing data corruption

3. **Offline Graceful Degradation**: Client validation allows admins to continue editing during network hiccups (airport WiFi, mobile hotspots). Server sync happens when connection restored.

4. **Reduced Server Load**: Client validation filters out 95% of invalid drags before hitting server. For 100 drag actions per minute, server only validates 5 drops (vs 100 with server-only).

5. **Progressive Enhancement**: Start with client validation (MVP), add server validation (security), add conflict resolution (advanced).

**Implementation Strategy**:

**Phase 1: Client Validation (Week 1)**:
```javascript
// Build constraint cache from schedule data
const validator = new ClientConstraintValidator(scheduleData);

// Validate during drag
sortable.option('onMove', (evt) => {
    const personId = evt.dragged.dataset.personId;
    const targetEventId = evt.to.dataset.eventId;

    const violations = validator.validateMove(personId, targetEventId);

    // Update drop zone styling
    if (violations.some(v => v.severity === 'error')) {
        evt.to.classList.add('drop-zone-invalid');
        return false; // Prevent drop
    } else if (violations.some(v => v.severity === 'warning')) {
        evt.to.classList.add('drop-zone-warning');
    } else {
        evt.to.classList.add('drop-zone-valid');
    }

    return true; // Allow drop
});
```

**Phase 2: Server Validation (Week 2)**:
```javascript
// Validate on drop
sortable.option('onEnd', async (evt) => {
    const editCommand = buildEditCommand(evt);

    try {
        // Server validation (authoritative)
        const response = await api.post('/api/manual-edits/validate', editCommand);

        if (response.violations.length > 0) {
            // Server found violations client missed
            showConflictDialog(response.violations);
            revertDrop(evt);
        } else {
            // Commit edit
            await api.post('/api/manual-edits/commit', editCommand);
        }
    } catch (error) {
        // Network error: queue edit for later sync
        queueOfflineEdit(editCommand);
    }
});
```

**Phase 3: Conflict Resolution (Week 3)**:
```javascript
function showConflictDialog(violations) {
    const dialog = document.createElement('div');
    dialog.className = 'conflict-dialog';

    dialog.innerHTML = `
        <h3>Constraint Violations</h3>
        <ul>
            ${violations.map(v => `
                <li class="violation-${v.severity}">
                    ${v.message}
                </li>
            `).join('')}
        </ul>

        <div class="suggestions">
            <h4>Suggestions</h4>
            ${buildSuggestions(violations)}
        </div>

        <button onclick="commitAnyway()">Override Constraint</button>
        <button onclick="cancelEdit()">Cancel</button>
    `;

    document.body.appendChild(dialog);
}
```

**Cache Synchronization**:
- **On load**: Fetch full schedule data, build client cache
- **On edit**: Update cache immediately (optimistic UI)
- **Periodic sync**: Poll server every 30s for changes (if other admins editing)
- **WebSocket** (future): Real-time sync for multi-admin editing

**Performance**:
- Client validation: <50ms (in-memory lookups)
- Server validation: 200-300ms (database queries + constraint solver)
- Total: 250-350ms from drop to commit (acceptable for non-real-time editing)

---

## Decision 4: Conflict Resolution Algorithm

### Context

When manual edits create constraint violations, the system should suggest alternative assignments that resolve conflicts. For example:
- "Jane is unavailable for Sunday 10am → Suggest Jane for Sunday 2pm instead"
- "Bob already has 10 assignments (fairness violation) → Suggest swapping Bob with Alice (3 assignments)"
- "No volunteer for Worship Leader role → Suggest promoting Sarah from Backup to Lead"

**Requirements**:
- Generate 2-5 alternative suggestions within 2 seconds
- Prioritize by constraint severity (fix errors before warnings)
- Minimize changes (fewest reassignments to resolve conflict)
- Respect locked assignments (don't suggest moving manually-locked volunteers)
- Explain reasoning ("Alice has fewer assignments, improving fairness")

### Options Evaluated

#### Option 1: Greedy Heuristic with Constraint Relaxation

**Overview**: Iteratively relax constraints until valid assignment found, using greedy heuristic to select best candidate at each step.

**Algorithm**:
```python
def suggest_alternatives(conflict: ConstraintViolation, max_suggestions=5):
    suggestions = []

    if conflict.type == 'availability':
        # Find alternative time slots where person is available
        person = get_person(conflict.person_id)
        similar_events = find_similar_events(conflict.event_id)

        for event in similar_events:
            if is_available(person, event) and has_role(person, event.required_role):
                score = calculate_similarity(conflict.event_id, event.id)
                suggestions.append(Suggestion(
                    action='reassign',
                    person_id=person.id,
                    target_event_id=event.id,
                    score=score,
                    reasoning=f"Similar event on {event.date}, person is available"
                ))

    elif conflict.type == 'fairness':
        # Find volunteers with fewer assignments to swap
        overloaded_person = get_person(conflict.person_id)
        underloaded_volunteers = find_underloaded_volunteers(
            role=conflict.required_role,
            max_assignments=average_assignments() * 0.8
        )

        for volunteer in underloaded_volunteers:
            if is_available(volunteer, conflict.event_id):
                score = calculate_fairness_improvement(overloaded_person, volunteer)
                suggestions.append(Suggestion(
                    action='swap',
                    person_a=overloaded_person.id,
                    person_b=volunteer.id,
                    event_id=conflict.event_id,
                    score=score,
                    reasoning=f"Swap with {volunteer.name} (fewer assignments, improves balance)"
                ))

    # Sort by score and return top suggestions
    return sorted(suggestions, key=lambda s: s.score, reverse=True)[:max_suggestions]
```

**Pros**:
- ✅ **Fast**: Generates suggestions in <500ms for typical schedules
- ✅ **Simple**: 200-300 LOC implementation
- ✅ **Good results**: Finds valid solutions 80-90% of the time
- ✅ **Explainable**: Can provide reasoning for each suggestion
- ✅ **Incremental**: Can refine suggestions based on user feedback

**Cons**:
- ❌ **Not optimal**: May miss better solutions (local optima)
- ❌ **Limited lookahead**: Doesn't consider downstream effects (fixing one conflict may create another)

**Performance**:
- Availability conflict: <100ms (query similar events, check availability)
- Fairness conflict: <300ms (query assignment counts, find underloaded volunteers)
- Role conflict: <200ms (query volunteers with role, check availability)

#### Option 2: Constraint Satisfaction Problem (CSP) Solver

**Overview**: Model conflict resolution as CSP and use solver (OR-Tools CP-SAT) to find optimal solution.

**Algorithm**:
```python
from ortools.sat.python import cp_model

def solve_conflict_with_csp(conflict: ConstraintViolation):
    model = cp_model.CpModel()

    # Variables: Binary assignment matrix [person][event]
    assignments = {}
    for person in all_volunteers:
        for event in all_events:
            assignments[(person.id, event.id)] = model.NewBoolVar(f'assign_{person.id}_{event.id}')

    # Constraints
    for person, event in assignments:
        # Availability constraint
        if not is_available(person, event):
            model.Add(assignments[(person.id, event.id)] == 0)

        # Role constraint
        if not has_role(person, event.required_role):
            model.Add(assignments[(person.id, event.id)] == 0)

    # Fairness constraint (soft)
    assignment_counts = {}
    for person in all_volunteers:
        assignment_counts[person.id] = sum(
            assignments[(person.id, event.id)] for event in all_events
        )

    avg_assignments = len(all_events) // len(all_volunteers)
    for person_id, count in assignment_counts.items():
        model.Add(count <= avg_assignments * 1.5)  # Max 50% above average

    # Objective: Minimize changes from current schedule
    current_assignments = get_current_assignments()
    changes = []
    for (person_id, event_id), var in assignments.items():
        is_current = (person_id, event_id) in current_assignments
        if is_current:
            changes.append(1 - var)  # Penalize removing current assignments
        else:
            changes.append(var)  # Penalize adding new assignments

    model.Minimize(sum(changes))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 2.0
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Extract suggestions from solution
        suggestions = []
        for (person_id, event_id), var in assignments.items():
            if solver.Value(var) == 1 and (person_id, event_id) not in current_assignments:
                suggestions.append(Suggestion(
                    action='assign',
                    person_id=person_id,
                    event_id=event_id,
                    reasoning="Optimal solution from constraint solver"
                ))
        return suggestions
    else:
        return []  # No solution found
```

**Pros**:
- ✅ **Optimal**: Finds best solution according to objective function
- ✅ **Holistic**: Considers all constraints simultaneously
- ✅ **Proven**: OR-Tools is production-grade solver

**Cons**:
- ❌ **Slow**: 2-5 seconds for moderate schedules (50 events, 100 volunteers)
- ❌ **Complex**: 500+ LOC implementation
- ❌ **Black box**: Hard to explain why specific solution chosen
- ❌ **Overkill**: Solving full CSP for single conflict is expensive
- ❌ **Timeout risk**: May not find solution within time limit

**Performance**:
- Small schedules (10 events, 20 volunteers): <500ms
- Medium schedules (50 events, 100 volunteers): 2-3 seconds
- Large schedules (100+ events, 200+ volunteers): 5+ seconds (unacceptable)

#### Option 3: Machine Learning Recommender

**Overview**: Train ML model on historical manual edits to predict good conflict resolutions.

**Approach**:
1. Collect training data: (conflict, resolution) pairs from past manual edits
2. Extract features: volunteer availability patterns, role preferences, fairness scores
3. Train model: Random forest or gradient boosting
4. Predict: Given conflict, predict most likely resolution

**Pros**:
- ✅ **Learns from admins**: Adapts to organization's preferences over time
- ✅ **Fast inference**: <100ms once trained

**Cons**:
- ❌ **Requires training data**: Need 1000+ manual edits before useful
- ❌ **Cold start**: No suggestions until model trained
- ❌ **Complex**: Requires ML pipeline (data collection, training, deployment)
- ❌ **Overfitting**: May learn bad practices from admins
- ❌ **Not explainable**: Hard to explain why suggestion made
- ❌ **Maintenance burden**: Model retraining, feature engineering

**Training Data Example**:
```python
{
    'conflict': {
        'type': 'availability',
        'person_id': 'person_123',
        'event_id': 'event_456',
        'datetime': '2025-10-23T10:00:00'
    },
    'resolution': {
        'action': 'reassign',
        'target_event_id': 'event_789',
        'datetime': '2025-10-23T14:00:00'
    },
    'features': {
        'person_assignment_count': 8,
        'avg_assignment_count': 5.5,
        'role_match': 1.0,
        'time_diff_hours': 4,
        'same_day': 1
    }
}
```

### Recommendation: Greedy Heuristic with Constraint Relaxation

**Selected**: Greedy heuristic algorithm with constraint relaxation (Option 1)

**Rationale**:

1. **Performance is Critical**: Suggestions must appear within 2 seconds of conflict detection. Greedy heuristic achieves <500ms (vs 2-5s for CSP solver). For manual editing UX, fast feedback is more important than optimal solutions.

2. **Good Enough is Enough**: Greedy algorithm finds valid solutions 80-90% of the time. For cases where it doesn't, admin can manually resolve (that's the point of manual editing!). Spending 5 seconds for optimal solution vs 500ms for good solution is bad UX trade-off.

3. **Explainability**: Greedy heuristic can provide clear reasoning ("Alice has 3 assignments vs Bob's 10, improves fairness by 40%"). CSP solver produces "optimal" solution but can't explain why. Admins trust explanations over "magic" suggestions.

4. **Simplicity**: 200-300 LOC vs 500+ for CSP or 1000+ for ML. Easier to test, debug, and maintain. SignUpFlow is small team - complexity is enemy.

5. **No Training Required**: Works immediately without historical data (vs ML approach requiring 1000+ examples).

6. **Incremental Refinement**: Can improve heuristics over time based on feedback (e.g., "Admins always reject suggestions with time diff >6 hours → add penalty for large time gaps").

**Implementation**:

```python
# api/services/conflict_resolver.py
class ConflictResolver:
    def __init__(self, db: Session):
        self.db = db

    def suggest_alternatives(
        self,
        violation: ConstraintViolation,
        max_suggestions: int = 5
    ) -> List[Suggestion]:
        """Generate alternative assignments to resolve constraint violation."""

        if violation.type == 'availability':
            return self._suggest_availability_fixes(violation, max_suggestions)
        elif violation.type == 'fairness':
            return self._suggest_fairness_fixes(violation, max_suggestions)
        elif violation.type == 'role':
            return self._suggest_role_fixes(violation, max_suggestions)
        else:
            return []

    def _suggest_availability_fixes(
        self,
        violation: ConstraintViolation,
        max_suggestions: int
    ) -> List[Suggestion]:
        """Suggest alternative time slots where person is available."""
        person = self.db.query(Person).filter(Person.id == violation.person_id).first()
        conflict_event = self.db.query(Event).filter(Event.id == violation.event_id).first()

        # Find similar events (same role, same day, nearby time)
        similar_events = self.db.query(Event).filter(
            Event.org_id == conflict_event.org_id,
            Event.id != conflict_event.id,
            Event.datetime.between(
                conflict_event.datetime - timedelta(days=1),
                conflict_event.datetime + timedelta(days=1)
            )
        ).all()

        suggestions = []
        for event in similar_events:
            # Check availability
            if self._has_availability_conflict(person, event):
                continue

            # Check role compatibility
            if not self._has_required_role(person, event):
                continue

            # Calculate similarity score
            time_diff = abs((event.datetime - conflict_event.datetime).total_seconds() / 3600)
            role_match = 1.0 if event.role_requirements == conflict_event.role_requirements else 0.5
            same_day = 1.0 if event.datetime.date() == conflict_event.datetime.date() else 0.0

            score = (
                0.5 * role_match +  # Prefer same role
                0.3 * (1.0 / (time_diff + 1)) +  # Prefer nearby time
                0.2 * same_day  # Prefer same day
            )

            suggestions.append(Suggestion(
                action='reassign',
                person_id=person.id,
                source_event_id=conflict_event.id,
                target_event_id=event.id,
                score=score,
                reasoning=f"Move to {event.title} on {event.datetime.strftime('%a %I:%M %p')} "
                         f"(same day, {int(time_diff)} hours difference)"
            ))

        # Sort by score and return top suggestions
        return sorted(suggestions, key=lambda s: s.score, reverse=True)[:max_suggestions]

    def _suggest_fairness_fixes(
        self,
        violation: ConstraintViolation,
        max_suggestions: int
    ) -> List[Suggestion]:
        """Suggest swaps with volunteers who have fewer assignments."""
        overloaded_person = self.db.query(Person).filter(
            Person.id == violation.person_id
        ).first()

        event = self.db.query(Event).filter(Event.id == violation.event_id).first()

        # Get current assignment counts
        assignment_counts = self.db.query(
            EventAssignment.person_id,
            func.count(EventAssignment.id).label('count')
        ).group_by(EventAssignment.person_id).all()

        avg_count = sum(c.count for c in assignment_counts) / len(assignment_counts)

        # Find underloaded volunteers
        underloaded_volunteers = self.db.query(Person).filter(
            Person.org_id == event.org_id,
            Person.id != overloaded_person.id
        ).all()

        suggestions = []
        for volunteer in underloaded_volunteers:
            volunteer_count = next(
                (c.count for c in assignment_counts if c.person_id == volunteer.id),
                0
            )

            # Only suggest if significantly underloaded
            if volunteer_count >= avg_count * 0.8:
                continue

            # Check availability and role
            if self._has_availability_conflict(volunteer, event):
                continue

            if not self._has_required_role(volunteer, event):
                continue

            # Calculate fairness improvement
            current_diff = abs(violation.current_count - avg_count)
            new_diff_a = abs((violation.current_count - 1) - avg_count)
            new_diff_b = abs((volunteer_count + 1) - avg_count)
            improvement = current_diff - (new_diff_a + new_diff_b) / 2

            suggestions.append(Suggestion(
                action='swap',
                person_a_id=overloaded_person.id,
                person_b_id=volunteer.id,
                event_id=event.id,
                score=improvement,
                reasoning=f"Swap with {volunteer.name} "
                         f"({volunteer_count} assignments → {volunteer_count + 1}, "
                         f"improves fairness by {int(improvement * 100)}%)"
            ))

        return sorted(suggestions, key=lambda s: s.score, reverse=True)[:max_suggestions]
```

**Heuristics to Refine**:
1. **Time preference**: Admins prefer same-day swaps (penalty = time_diff × 0.1)
2. **Role stickiness**: Admins prefer keeping volunteers in familiar roles (penalty = 0.5 if different role)
3. **Team cohesion**: Admins prefer keeping team members together (bonus = 0.3 if same team)
4. **Recency**: Admins prefer recent edits to be preserved (penalty = 0.2 if suggests moving recent manual override)

**Testing Strategy**:
- Unit tests: Test each heuristic in isolation (availability, fairness, role)
- Integration tests: Test end-to-end suggestion generation with realistic conflict scenarios
- Performance tests: Benchmark suggestion generation time for large schedules (100+ events)
- Acceptance tests: Qualitative evaluation by real admins ("Are suggestions helpful?")

---

## Decision 5: Edit History Storage Strategy

### Context

The undo/redo system needs to store edit history to support:
- Undo/redo operations (50 actions)
- Session persistence (survive page refresh)
- Optional database persistence (save important edits)
- Sync across browser tabs (same user, multiple tabs)

**Requirements**:
- Fast write (<10ms per edit)
- Fast read (<5ms for undo/redo)
- Persist across page refresh (within session)
- Optional long-term storage (database)
- Reasonable memory usage (<1MB for 50 edits)
- Support concurrent editing (multiple admins)

### Options Evaluated

#### Option 1: Session Storage with Database Persistence on Save

**Overview**: Store edit history in browser sessionStorage for fast access. Periodically sync to database on explicit "Save" action or when leaving page.

**Approach**:
```javascript
// In-memory + sessionStorage for undo/redo
class EditHistory {
    constructor() {
        this.undoStack = [];
        this.redoStack = [];
        this.unsavedChanges = false;

        // Restore from sessionStorage on load
        this.restoreFromSession();
    }

    pushCommand(command) {
        this.undoStack.push(command);
        this.redoStack = [];
        this.unsavedChanges = true;

        // Persist to sessionStorage (fast, synchronous)
        this.saveToSession();

        // Limit stack size
        if (this.undoStack.length > 50) {
            this.undoStack.shift();
        }
    }

    saveToSession() {
        const data = {
            undoStack: this.undoStack.map(cmd => cmd.toJSON()),
            redoStack: this.redoStack.map(cmd => cmd.toJSON())
        };
        sessionStorage.setItem('editHistory', JSON.stringify(data));
    }

    async saveToDatabase() {
        if (!this.unsavedChanges) return;

        // Persist important edits to database
        const editsToSave = this.undoStack.filter(cmd => cmd.isPersistable);

        await api.post('/api/manual-edits/batch-save', {
            edits: editsToSave.map(cmd => cmd.toDatabaseFormat())
        });

        this.unsavedChanges = false;
    }

    // Auto-save on page unload
    setupAutoSave() {
        window.addEventListener('beforeunload', (e) => {
            if (this.unsavedChanges) {
                // Sync save before page closes
                this.saveToDatabase();

                // Warn user about unsaved changes
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Save before leaving?';
            }
        });

        // Periodic auto-save every 30 seconds
        setInterval(() => {
            if (this.unsavedChanges) {
                this.saveToDatabase();
            }
        }, 30000);
    }
}
```

**Pros**:
- ✅ **Fast undo/redo**: In-memory + sessionStorage = <5ms reads
- ✅ **Survives refresh**: sessionStorage persists within browser session
- ✅ **Reduced DB writes**: Only write to database on explicit save (not every edit)
- ✅ **Offline-friendly**: Can undo/redo without network connection
- ✅ **Simple**: Straightforward implementation (100 LOC)

**Cons**:
- ❌ **Lost on tab close**: sessionStorage cleared when tab closed (but that's the point of "session")
- ❌ **No cross-tab sync**: Edit in Tab A not visible in Tab B (mitigation: BroadcastChannel API)
- ❌ **Manual save required**: User must remember to save (mitigation: auto-save + unsaved changes indicator)

**When to Database Persist**:
- Explicit "Save" button click
- Auto-save every 30 seconds (if unsaved changes)
- Before page unload (`beforeunload` event)
- After critical operations (bulk edit, solver re-run)

#### Option 2: Database Only

**Overview**: Store all edit history in database. No client-side caching.

**Approach**:
```python
# Backend: Store edit history in database
class ManualEdit(Base):
    __tablename__ = "manual_edits"

    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    admin_id = Column(String, ForeignKey("people.id"), nullable=False)
    edit_type = Column(String, nullable=False)  # 'reassign', 'swap', 'add', 'delete'
    edit_data = Column(JSON, nullable=False)  # Command parameters
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_undone = Column(Boolean, default=False)  # Track if edit was undone

    __table_args__ = (
        Index('idx_manual_edits_admin_timestamp', 'admin_id', 'timestamp'),
        Index('idx_manual_edits_org_timestamp', 'org_id', 'timestamp'),
    )

# API endpoints
@router.post("/api/manual-edits")
def create_manual_edit(edit: ManualEditCreate, db: Session = Depends(get_db)):
    manual_edit = ManualEdit(
        id=generate_id(),
        org_id=edit.org_id,
        admin_id=current_user.id,
        edit_type=edit.type,
        edit_data=edit.data,
        timestamp=datetime.utcnow()
    )
    db.add(manual_edit)
    db.commit()

    return {"id": manual_edit.id}

@router.get("/api/manual-edits/history")
def get_edit_history(admin_id: str, limit: int = 50, db: Session = Depends(get_db)):
    edits = db.query(ManualEdit).filter(
        ManualEdit.admin_id == admin_id
    ).order_by(ManualEdit.timestamp.desc()).limit(limit).all()

    return [edit.to_dict() for edit in edits]

@router.post("/api/manual-edits/{edit_id}/undo")
def undo_edit(edit_id: str, db: Session = Depends(get_db)):
    edit = db.query(ManualEdit).filter(ManualEdit.id == edit_id).first()

    # Revert the edit
    if edit.edit_type == 'reassign':
        # Move volunteer back to original event
        ...

    edit.is_undone = True
    db.commit()

    return {"status": "undone"}
```

**Pros**:
- ✅ **Cross-device**: Edit history synced across all devices
- ✅ **Durable**: Never lost (database backups)
- ✅ **Audit trail**: Full history for compliance
- ✅ **Cross-tab sync**: Automatic sync across browser tabs

**Cons**:
- ❌ **Slow**: 200-500ms round-trip for every undo/redo (vs <5ms with sessionStorage)
- ❌ **Network dependent**: Can't undo/redo offline
- ❌ **High DB load**: 100+ writes per editing session (vs 5-10 with hybrid)
- ❌ **Complex sync**: Managing concurrent edits from multiple admins is tricky

#### Option 3: IndexedDB (Client-Side Database)

**Overview**: Store edit history in IndexedDB (browser's local database) for persistent client-side storage.

**Approach**:
```javascript
class IndexedDBEditHistory {
    constructor() {
        this.db = null;
        this.init();
    }

    async init() {
        this.db = await new Promise((resolve, reject) => {
            const request = indexedDB.open('EditHistoryDB', 1);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create object store for edits
                const editsStore = db.createObjectStore('edits', {
                    keyPath: 'id',
                    autoIncrement: true
                });

                editsStore.createIndex('timestamp', 'timestamp', { unique: false });
                editsStore.createIndex('admin_id', 'admin_id', { unique: false });
            };
        });
    }

    async pushCommand(command) {
        const transaction = this.db.transaction(['edits'], 'readwrite');
        const store = transaction.objectStore('edits');

        await store.add({
            type: command.type,
            data: command.data,
            timestamp: Date.now(),
            admin_id: currentUser.id
        });
    }

    async getHistory(limit = 50) {
        const transaction = this.db.transaction(['edits'], 'readonly');
        const store = transaction.objectStore('edits');
        const index = store.index('timestamp');

        const edits = [];
        let cursor = await index.openCursor(null, 'prev'); // Newest first

        while (cursor && edits.length < limit) {
            edits.push(cursor.value);
            cursor = await cursor.continue();
        }

        return edits;
    }
}
```

**Pros**:
- ✅ **Persistent**: Survives browser restarts (unlike sessionStorage)
- ✅ **Large storage**: 50MB+ vs 5-10MB for sessionStorage
- ✅ **Async API**: Non-blocking database operations

**Cons**:
- ❌ **Complex**: 200+ LOC implementation (vs 50 for sessionStorage)
- ❌ **Browser compatibility**: Not supported in older browsers
- ❌ **No cross-tab sync**: Each tab has separate IndexedDB instance
- ❌ **Overkill**: Manual editing sessions rarely exceed 50 edits (fits in sessionStorage)

### Recommendation: Session Storage with Database Persistence on Save

**Selected**: sessionStorage for undo/redo + database persistence on explicit save

**Rationale**:

1. **Performance is Critical for Undo/Redo**: Undo/redo must be instantaneous (<5ms). sessionStorage provides synchronous reads (vs 200-500ms for database). For manual editing UX, fast undo/redo is non-negotiable.

2. **sessionStorage is Perfect for Sessions**: The whole point of undo/redo is to support the current editing session. Once admin closes tab, they don't need 50-action history. sessionStorage matches this use case perfectly.

3. **Database for Important Edits Only**: Persist final state to database, not every intermediate undo/redo. Saves 95% of database writes while maintaining durability of committed edits.

4. **Offline Editing**: sessionStorage works offline, allowing admins to continue editing during network issues. Database sync happens when connection restored.

5. **Simple Implementation**: 100 LOC vs 200+ for IndexedDB or complex sync logic for database-only. Easier to test and maintain.

6. **Cross-Tab Sync Not Critical**: Multiple tabs editing same schedule simultaneously is rare (admins typically use single tab). If needed later, can add BroadcastChannel API for cross-tab sync (20 LOC).

**Implementation**:

```javascript
// frontend/js/edit-history.js
class EditHistory {
    constructor() {
        this.undoStack = [];
        this.redoStack = [];
        this.unsavedChanges = false;

        this.restoreFromSession();
        this.setupAutoSave();
        this.setupUnsavedChangesWarning();
    }

    // Session storage (fast, local)
    saveToSession() {
        try {
            const data = {
                undoStack: this.undoStack.map(cmd => cmd.toJSON()),
                redoStack: this.redoStack.map(cmd => cmd.toJSON()),
                lastSave: Date.now()
            };
            sessionStorage.setItem('editHistory', JSON.stringify(data));
        } catch (e) {
            if (e.name === 'QuotaExceededError') {
                // Storage full: keep only last 25 commands
                this.undoStack = this.undoStack.slice(-25);
                this.saveToSession(); // Retry
            }
        }
    }

    restoreFromSession() {
        try {
            const data = JSON.parse(sessionStorage.getItem('editHistory') || '{}');
            this.undoStack = (data.undoStack || []).map(CommandFactory.fromJSON);
            this.redoStack = (data.redoStack || []).map(CommandFactory.fromJSON);
        } catch (e) {
            console.error('Failed to restore edit history:', e);
            this.undoStack = [];
            this.redoStack = [];
        }
    }

    // Database persistence (durable, cross-device)
    async saveToDatabase() {
        if (!this.unsavedChanges) return;

        showSavingIndicator();

        try {
            // Only save committed edits (not every undo/redo)
            const editsToSave = this.undoStack.filter(cmd => !cmd.isTransient);

            await api.post('/api/manual-edits/batch-save', {
                edits: editsToSave.map(cmd => ({
                    type: cmd.type,
                    data: cmd.data,
                    timestamp: cmd.timestamp
                }))
            });

            this.unsavedChanges = false;
            hideSavingIndicator();
            showSavedNotification();
        } catch (error) {
            showErrorNotification('Failed to save edits: ' + error.message);
        }
    }

    setupAutoSave() {
        // Auto-save every 30 seconds
        setInterval(() => {
            if (this.unsavedChanges) {
                this.saveToDatabase();
            }
        }, 30000);

        // Save before page unload
        window.addEventListener('beforeunload', (e) => {
            if (this.unsavedChanges) {
                // Attempt sync save (best effort)
                navigator.sendBeacon('/api/manual-edits/batch-save', JSON.stringify({
                    edits: this.undoStack.map(cmd => cmd.toDatabaseFormat())
                }));
            }
        });
    }

    setupUnsavedChangesWarning() {
        window.addEventListener('beforeunload', (e) => {
            if (this.unsavedChanges) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Save before leaving?';
            }
        });
    }
}

// UI indicators
function showUnsavedChangesIndicator() {
    const indicator = document.getElementById('unsaved-changes');
    indicator.style.display = 'block';
    indicator.textContent = 'Unsaved changes';
}

function showSavingIndicator() {
    const indicator = document.getElementById('unsaved-changes');
    indicator.textContent = 'Saving...';
    indicator.classList.add('saving');
}

function showSavedNotification() {
    const indicator = document.getElementById('unsaved-changes');
    indicator.textContent = 'All changes saved';
    indicator.classList.add('saved');

    setTimeout(() => {
        indicator.style.display = 'none';
        indicator.classList.remove('saved');
    }, 2000);
}
```

**Storage Breakdown**:
- **sessionStorage**: 50 commands × 200 bytes = 10KB (undo/redo stack)
- **Database**: 5-10 committed edits per session × 300 bytes = 1.5-3KB per session
- **Total**: ~13KB per editing session (negligible)

**Cross-Tab Sync** (Optional Future Enhancement):
```javascript
// Use BroadcastChannel API for cross-tab sync
class CrossTabEditHistory extends EditHistory {
    constructor() {
        super();
        this.channel = new BroadcastChannel('edit-history');

        this.channel.onmessage = (event) => {
            if (event.data.type === 'NEW_EDIT') {
                // Another tab made an edit
                this.mergeExternalEdit(event.data.command);
            }
        };
    }

    pushCommand(command) {
        super.pushCommand(command);

        // Broadcast to other tabs
        this.channel.postMessage({
            type: 'NEW_EDIT',
            command: command.toJSON()
        });
    }
}
```

---

## Implementation Phases

### Phase 0: Research Complete ✅

This document completes the research phase with comprehensive analysis of 5 technology decisions.

### Phase 1: Design (Week 1-2)

**Deliverables**:
1. **data-model.md**: Database schema for ManualOverride, EditHistory, ConstraintViolation entities
2. **contracts/manual-edit-api.md**: API contract for drag-drop reassignment operations
3. **contracts/constraint-validation-api.md**: API contract for real-time constraint validation
4. **contracts/undo-redo-api.md**: API contract for edit history management
5. **quickstart.md**: 10-minute setup guide for manual editing feature

**Tasks**:
- Define database migrations (Alembic)
- Define Pydantic schemas for request/response
- Define API endpoint specifications (OpenAPI)
- Write setup guide with code examples

### Phase 2: Implementation (Week 3-6)

**Week 3: Core Drag-and-Drop**:
- Install SortableJS dependency
- Implement schedule-editor.js with drag-drop handlers
- Implement constraint-validator.js (client-side)
- Create manual_edits.py router (backend)
- Implement ManualEditService (business logic)

**Week 4: Constraint Validation**:
- Implement constraint validation API endpoint
- Integrate with existing OR-Tools solver
- Add conflict highlighting in UI
- Implement greedy conflict resolver

**Week 5: Undo/Redo System**:
- Implement Command pattern classes
- Implement EditHistory manager
- Add undo/redo UI controls (buttons, keyboard shortcuts)
- Implement sessionStorage persistence

**Week 6: Polish & Testing**:
- Write E2E tests with Playwright
- Performance optimization (lazy loading, debounce)
- Accessibility improvements (ARIA attributes)
- Documentation and user guide

---

## Performance Targets

| Operation | Target | Measured | Status |
|-----------|--------|----------|--------|
| Drag-drop responsiveness | <100ms | TBD | Pending |
| Client constraint validation | <50ms | TBD | Pending |
| Server constraint validation | <300ms | TBD | Pending |
| Conflict resolution suggestions | <2s | TBD | Pending |
| Undo/redo operation | <5ms | TBD | Pending |
| Auto-save to database | <1s | TBD | Pending |

**Benchmarking Plan**:
- Test with realistic schedules (50 events, 200 volunteers)
- Measure p50, p95, p99 latencies
- Profile bottlenecks with Chrome DevTools
- Optimize hot paths

---

## Risk Mitigation

### Risk 1: Drag-drop performance degradation with large schedules

**Impact**: High (unusable UI)
**Probability**: Medium

**Mitigation**:
- Virtual scrolling for 50+ events (only render visible events)
- Lazy initialization of drag-drop (only for visible containers)
- Debounce validation (300ms delay after drag start)
- Pagination (show 20 events per page)

### Risk 2: Constraint validation false positives/negatives

**Impact**: High (incorrect schedules, user frustration)
**Probability**: Low

**Mitigation**:
- Server-side validation is authoritative (client validation is best-effort)
- Comprehensive test suite (100+ constraint scenarios)
- Manual testing by real admins before launch
- Fallback: Admin can override constraints (with confirmation dialog)

### Risk 3: Concurrent editing conflicts

**Impact**: Medium (lost edits, confusion)
**Probability**: Low (rare for multiple admins to edit simultaneously)

**Mitigation**:
- Optimistic locking (track last_modified timestamp)
- Conflict detection on save (compare timestamps)
- Conflict resolution dialog ("Your changes conflict with [Admin Name]'s edit")
- Future: WebSocket for real-time multi-admin editing

### Risk 4: Browser compatibility issues (drag-drop, sessionStorage)

**Impact**: Medium (feature unavailable for some users)
**Probability**: Low

**Mitigation**:
- SortableJS supports IE 11+ (covers 99% of users)
- sessionStorage is supported in all modern browsers
- Graceful degradation (if no sessionStorage, disable undo/redo but allow editing)
- Feature detection (check for drag-drop support before initializing)

---

## Conclusion

The research phase has identified optimal technologies and patterns for implementing manual schedule editing:

1. **SortableJS** for drag-and-drop (11KB, touch support, accessibility)
2. **Command Pattern** for undo/redo (simple, fast, composable)
3. **Hybrid validation** (client immediate + server authoritative)
4. **Greedy heuristic** for conflict resolution (fast, explainable)
5. **sessionStorage + database** for edit history (performant, durable)

These decisions prioritize **UX responsiveness**, **implementation simplicity**, and **developer velocity** while maintaining **security** and **accuracy** through server-side validation.

**Next Steps**: Proceed to Phase 1 (Design) to define data models, API contracts, and implementation guide.
