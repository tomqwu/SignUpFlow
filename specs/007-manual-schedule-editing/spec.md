# Feature Specification: Manual Schedule Editing Interface

**Feature Branch**: `007-manual-schedule-editing`
**Created**: 2025-10-20
**Status**: Draft
**Input**: User description: "Manual schedule editing interface allowing direct manipulation of solver-generated schedules. Admins can drag-and-drop volunteer assignments between time slots, swap volunteers between roles, manually override automated assignments, and add/remove assignments while maintaining fairness metrics. Interface shows real-time constraint violations (availability conflicts, fairness imbalance, coverage gaps) with visual warnings. Changes preserved when solver re-runs but marked as locked assignments. Supports undo/redo for manual edits and provides suggestions for resolving conflicts when manual changes create constraint violations."

## User Scenarios & Testing

### User Story 1 - Drag-and-Drop Assignment Editing (Priority: P1)

Admin users drag volunteer assignments between time slots and roles using visual drag-and-drop interface. Real-time validation shows constraint violations (availability conflicts, fairness issues) as warnings before confirming changes.

**Why this priority**: Core functionality enabling manual schedule adjustments. Solver-generated schedules often need tweaks for last-minute changes or special requests. Without manual editing, admins must regenerate entire schedules or manage changes outside system.

**Independent Test**: Can be fully tested by dragging volunteer from one event to another, viewing real-time conflict warnings, and verifying assignment updates correctly. Delivers immediate value by enabling quick schedule adjustments.

**Acceptance Scenarios**:

1. **Given** schedule with assignments, **When** admin drags volunteer from Event A to Event B, **Then** system validates availability/fairness and updates assignment if valid or shows warning if conflict detected
2. **Given** volunteer unavailable for target slot, **When** admin attempts drag, **Then** interface displays red warning "John unavailable Sun 10am - marked unavailable" before drop
3. **Given** assignment creates fairness imbalance (volunteer assigned 5x vs others 1x), **When** admin completes drag, **Then** interface shows yellow warning "Fairness alert: John now has 5 assignments vs average 2.3" with option to proceed
4. **Given** successful drag-drop edit, **When** change saved, **Then** assignment marked as "locked" (manual override) preventing solver from changing it on re-run
5. **Given** drag-drop in progress, **When** admin hovers over target slot, **Then** interface previews impact with color coding (green=valid, yellow=fairness warning, red=hard constraint violation)

---

### User Story 2 - Real-Time Constraint Validation (Priority: P1)

Interface displays real-time warnings for constraint violations (availability conflicts, coverage gaps, fairness imbalance) as admin makes changes. Visual indicators (colors, icons) show severity: red for hard constraints, yellow for soft constraints.

**Why this priority**: Essential for preventing invalid schedules. Without real-time validation, admins create schedules with unavailable volunteers or coverage gaps, requiring later corrections. Immediate feedback prevents errors at source.

**Independent Test**: Can be fully tested by assigning unavailable volunteer, viewing red availability conflict warning, and attempting to assign volunteer exceeding fairness threshold to see yellow fairness warning. Delivers immediate value by catching errors before save.

**Acceptance Scenarios**:

1. **Given** volunteer marked unavailable for date, **When** admin assigns volunteer to that date, **Then** interface displays red error icon with message "Availability conflict: [Name] unavailable [Date]"
2. **Given** event requires 3 volunteers, **When** admin removes assignment leaving only 1 volunteer, **Then** interface shows yellow warning "Coverage gap: Need 2 more volunteers for [Role]"
3. **Given** editing schedule, **When** fairness imbalance exceeds 30% (some volunteers 3x more assignments than others), **Then** interface displays yellow warning with fairness chart showing distribution
4. **Given** multiple constraint violations present, **When** admin views schedule, **Then** interface displays summary "3 availability conflicts, 2 coverage gaps, 1 fairness warning" with filters to show each type
5. **Given** constraint violation, **When** admin clicks warning, **Then** interface highlights affected assignments and suggests resolution options (swap with available volunteer, remove assignment, mark as exception)

---

### User Story 3 - Locked Assignment Preservation (Priority: P1)

Manual edits marked as "locked" to preserve admin changes when scheduling solver re-runs. Locked assignments highlighted visually (lock icon, different color) and solver respects locks treating them as fixed constraints.

**Why this priority**: Critical for maintaining manual overrides. If solver overwrites manual changes on re-run, admins lose work and trust in system. Locked assignments enable hybrid approach: solver handles bulk scheduling while admins fine-tune specific assignments.

**Independent Test**: Can be fully tested by manually editing assignment, locking it, re-running solver, and verifying locked assignment unchanged while solver updates other assignments. Delivers immediate value by protecting manual work.

**Acceptance Scenarios**:

1. **Given** admin manually assigns volunteer, **When** assignment saved, **Then** assignment automatically marked as "locked" with lock icon displayed in schedule view
2. **Given** schedule with 20 assignments (5 locked, 15 unlocked), **When** admin re-runs solver, **Then** solver updates 15 unlocked assignments only, 5 locked assignments unchanged
3. **Given** locked assignment, **When** admin views assignment details, **Then** interface displays "Manual override - locked from solver changes" with option to unlock
4. **Given** admin wants to unlock assignment, **When** admin clicks "Unlock", **Then** system confirms "Allow solver to modify this assignment on next run?" and removes lock if confirmed
5. **Given** solver running with locked assignments present, **When** solver completes, **Then** schedule displays summary "Generated 15 assignments, preserved 5 locked assignments"

---

### User Story 4 - Undo/Redo for Manual Edits (Priority: P2)

Interface provides undo/redo functionality for all manual schedule changes. Admins can reverse accidental edits or explore different scheduling options by undoing/redoing changes rapidly.

**Why this priority**: Reduces fear of mistakes during manual editing. Without undo, admins hesitant to experiment with schedule adjustments worrying they'll break something irreversibly. Undo enables confident exploration and quick error recovery.

**Independent Test**: Can be fully tested by making 3 manual edits, undoing last 2 edits, redoing 1 edit, and verifying schedule state matches expected result at each step. Delivers immediate value by enabling risk-free experimentation.

**Acceptance Scenarios**:

1. **Given** schedule with no changes, **When** admin makes manual edit, **Then** undo button becomes enabled allowing reversal of edit
2. **Given** admin makes 5 manual edits, **When** admin clicks undo 3 times, **Then** last 3 edits reversed in reverse chronological order returning schedule to state after 2nd edit
3. **Given** admin undid 2 edits, **When** admin clicks redo, **Then** most recently undone edit restored
4. **Given** undo/redo history exists, **When** admin views edit history, **Then** interface displays chronological list: "Assigned John to Event A, Removed Sarah from Event B, Swapped Mike and Lisa..."
5. **Given** admin makes new edit after undo, **When** edit saved, **Then** redo history cleared preventing redo of previously undone edits (standard undo/redo behavior)

---

### User Story 5 - Volunteer Swapping (Priority: P2)

Admins swap volunteers between roles/time slots in single operation. Interface validates swap feasibility checking both volunteers' availability and role compatibility before executing swap.

**Why this priority**: Common operation when volunteers request changes. Swapping is faster and less error-prone than removing two assignments and creating two new ones manually. Single atomic operation prevents intermediate invalid states.

**Independent Test**: Can be fully tested by selecting two assignments and swapping volunteers, verifying both volunteers' assignments updated correctly and both availability/role requirements validated. Delivers immediate value by streamlining common adjustment workflow.

**Acceptance Scenarios**:

1. **Given** schedule with assignments, **When** admin selects "Swap" mode and clicks two assignments, **Then** interface highlights both assignments and displays "Swap [Person A] and [Person B]?" confirmation
2. **Given** swap requested, **When** both volunteers available for swapped slots, **Then** swap executes successfully updating both assignments simultaneously
3. **Given** swap requested, **When** one volunteer unavailable for target slot, **Then** interface displays error "Cannot swap: [Name] unavailable for [Date/Time]" and cancels swap
4. **Given** successful swap, **When** swap completes, **Then** both assignments marked as locked preventing solver from changing on re-run
5. **Given** multi-person swap needed (3+ volunteers rotating), **When** admin initiates swap, **Then** interface supports chained swaps: "Person A → Slot 1, Person B → Slot 2, Person C → Slot 3" executed atomically

---

### User Story 6 - Conflict Resolution Suggestions (Priority: P3)

When manual changes create constraint violations, system suggests resolution options: swap with available volunteer, adjust event timing, mark as exception requiring manual override. Suggestions prioritize maintaining fairness and coverage.

**Why this priority**: Helpful but not essential. Admins can manually resolve conflicts without suggestions. Suggestions improve efficiency and help less experienced admins learn best practices for conflict resolution. Quality-of-life enhancement rather than core functionality.

**Independent Test**: Can be fully tested by creating availability conflict, viewing suggested resolutions (swap with available volunteer, remove assignment), and selecting suggestion to apply automatically. Delivers immediate value by accelerating conflict resolution.

**Acceptance Scenarios**:

1. **Given** admin assigns unavailable volunteer, **When** conflict detected, **Then** interface suggests "Swap with: [List of 3 available volunteers for this slot]" allowing one-click resolution
2. **Given** coverage gap (event needs 2 more volunteers), **When** admin views gap warning, **Then** interface suggests "Available volunteers: [Names with availability confirmed]" for quick assignment
3. **Given** fairness imbalance (volunteer overassigned), **When** admin views fairness warning, **Then** interface suggests "Redistribute: Move 2 assignments from [Overassigned] to [Underassigned volunteers]"
4. **Given** admin selects suggestion, **When** suggestion applied, **Then** system executes resolution automatically (e.g., swap with suggested volunteer) and clears conflict warning
5. **Given** no simple resolution available, **When** admin views conflict, **Then** interface displays "No automatic resolution found" with manual options: "Mark as exception (override constraint)", "Remove assignment", "Edit event requirements"

---

### Edge Cases

- **What happens when admin locks all assignments preventing solver from running?** System displays warning "All assignments locked - solver has no flexibility to optimize. Unlock some assignments for better scheduling." Solver still runs but only validates locked assignments against constraints without making changes.

- **How does system handle undo/redo across solver re-runs?** Undo/redo history applies to manual edits only, not solver-generated changes. When solver re-runs, undo history preserved for manual edits but solver changes not added to undo stack (prevents undoing automated optimizations).

- **What happens when dragging volunteer to slot where they already have assignment?** Interface displays error "Duplicate assignment: [Name] already assigned to [Event] at [Time]" preventing double-booking. Exception: If dragging to different role at same event, system allows (volunteer can have multiple roles per event if configured).

- **How does system handle fairness calculations when assignments locked?** Fairness metrics calculated including locked assignments. If locked assignments create imbalance, fairness warnings displayed but system allows since locked assignments represent admin business decisions overriding fairness optimization.

- **What happens when manual edit conflicts with recurring event series?** System prompts "This event is part of recurring series. Apply change to: (1) This occurrence only (creates exception), (2) All future occurrences (updates series template)." Manual edit creates exception if "this occurrence only" selected.

- **How does system handle rapid successive drags (admin dragging multiple volunteers quickly)?** Interface queues validation requests and debounces conflict checking (validates after 500ms pause in dragging). Prevents performance issues from rapid re-validation while still providing real-time feedback.

- **What happens when admin makes conflicting manual edits (assigns same volunteer to overlapping events)?** System detects overlap on save and displays error "Scheduling conflict: [Name] cannot be assigned to overlapping events [Event A] and [Event B]" forcing admin to resolve before save.

## Requirements

### Functional Requirements

#### Drag-and-Drop Interface
- **FR-001**: System MUST support drag-and-drop of volunteer assignments between events, roles, and time slots
- **FR-002**: Drag-and-drop MUST provide visual feedback: dragged item follows cursor, valid drop zones highlighted green, invalid zones highlighted red
- **FR-003**: System MUST validate drop target in real-time: check volunteer availability, role compatibility, fairness impact before allowing drop
- **FR-004**: System MUST support multi-select drag: admin selects multiple volunteers and drags all simultaneously to same event
- **FR-005**: Drag-and-drop MUST work on desktop (mouse) and touch devices (finger drag) with consistent behavior

#### Real-Time Constraint Validation
- **FR-006**: System MUST validate availability constraints: display red error if volunteer marked unavailable for assignment date/time
- **FR-007**: System MUST validate coverage constraints: display yellow warning if event has insufficient volunteers for role requirements
- **FR-008**: System MUST calculate fairness metrics: display yellow warning if assignment creates imbalance (volunteer assignments >30% above average)
- **FR-009**: System MUST display constraint violations with severity levels: red (hard constraint blocking), yellow (soft constraint warning), green (valid)
- **FR-010**: Validation MUST complete within 500ms of edit action providing responsive user experience
- **FR-011**: System MUST aggregate violations into summary: "X availability conflicts, Y coverage gaps, Z fairness warnings" with filtering

#### Locked Assignment Management
- **FR-012**: System MUST automatically mark manual edits as "locked" preventing scheduling solver from modifying on re-run
- **FR-013**: Locked assignments MUST display visual indicator (lock icon, distinct background color, border) differentiating from solver-generated assignments
- **FR-014**: System MUST allow admins to unlock assignments enabling solver to modify on next run
- **FR-015**: When solver re-runs, system MUST treat locked assignments as fixed constraints and update unlocked assignments only
- **FR-016**: Locked assignment metadata MUST include: locked by user ID, locked timestamp, lock reason (manual edit, swap, exception)

#### Undo/Redo Functionality
- **FR-017**: System MUST maintain undo history for all manual edits supporting minimum 20 undo steps
- **FR-018**: Undo operation MUST reverse last edit returning schedule to previous state
- **FR-019**: Redo operation MUST restore most recently undone edit
- **FR-020**: System MUST clear redo history when new edit made after undo (standard undo/redo behavior)
- **FR-021**: Undo/redo MUST support all edit types: drag-drop, add assignment, remove assignment, swap, bulk edits
- **FR-022**: System MUST display edit history showing chronological list of edits with timestamps and user IDs

#### Volunteer Swapping
- **FR-023**: System MUST support volunteer swapping: admin selects two assignments and swaps volunteers in single atomic operation
- **FR-024**: Swap operation MUST validate both volunteers' availability for target slots before executing
- **FR-025**: Swap MUST validate role compatibility: ensure both volunteers qualified for swapped roles
- **FR-026**: System MUST support chained swaps: 3+ volunteers rotating assignments (A→B, B→C, C→A) executed atomically
- **FR-027**: Successful swap MUST mark both assignments as locked preserving manual override

#### Conflict Resolution
- **FR-028**: When constraint violation detected, system MUST suggest resolution options: swap with available volunteer, remove assignment, mark as exception
- **FR-029**: Suggestions MUST prioritize maintaining fairness: recommend underassigned volunteers for coverage gaps
- **FR-030**: System MUST allow one-click application of suggestions executing resolution automatically
- **FR-031**: If no automatic resolution available, system MUST provide manual options with clear explanation of trade-offs

#### Integration with Scheduling Solver
- **FR-032**: Manual edits MUST integrate with solver workflow: locked assignments treated as hard constraints during solver optimization
- **FR-033**: System MUST support hybrid scheduling: solver generates initial schedule, admin fine-tunes with manual edits, solver re-runs respecting locks
- **FR-034**: After manual edits, system MUST recalculate fairness metrics across entire schedule including locked assignments
- **FR-035**: System MUST display solver vs manual edit breakdown: "15 solver-generated, 5 manually edited, 2 locked" in schedule summary

### Key Entities

- **ManualEdit**: Record of admin schedule change. Attributes: edit ID, edit type (drag-drop, swap, add, remove), affected assignments (before/after states), edited by user ID, edit timestamp, undo/redo sequence number, constraint violations (list of warnings/errors).

- **LockedAssignment**: Assignment protected from solver changes. Attributes: assignment ID, event ID, volunteer ID, role, locked status (true/false), locked by user ID, locked timestamp, lock reason (manual edit, swap, exception, recurring override), unlock allowed (boolean).

- **ConstraintViolation**: Detected scheduling conflict. Attributes: violation ID, violation type (availability conflict, coverage gap, fairness imbalance, overlap), severity (error or warning), affected assignments, violation message, suggested resolutions (list of resolution options), resolution applied (boolean).

- **EditHistory**: Chronological log of manual edits. Attributes: history entry ID, edit ID, edit description (natural language: "Assigned John to Event A"), edit timestamp, edited by user ID, edit state (active, undone, redone), previous schedule state (for undo), next schedule state (for redo).

- **SwapOperation**: Multi-assignment swap record. Attributes: swap ID, swap type (2-person, 3-person chain, bulk), participating assignments (list with before/after mappings), swap timestamp, swapped by user ID, validation results (availability checks, role compatibility), swap status (pending, completed, failed).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Admin users complete schedule adjustments in under 3 minutes on average, 70% faster than re-running solver for small changes
- **SC-002**: Drag-and-drop interface provides real-time validation feedback within 500ms of drop action 95% of the time
- **SC-003**: Locked assignments preserved with 100% reliability: 0% of locked assignments modified by solver on re-run
- **SC-004**: Constraint violation detection catches 100% of availability conflicts and 95% of fairness imbalances before admin saves schedule
- **SC-005**: Undo/redo functionality supports 20+ edit steps with 100% accuracy in state restoration
- **SC-006**: Volunteer swapping completes in single operation reducing time by 60% vs manual remove/add workflow
- **SC-007**: Conflict resolution suggestions resolve 70% of violations automatically without requiring manual intervention
- **SC-008**: User satisfaction: 80% of admins report manual editing "significantly improves" schedule quality in post-deployment survey
- **SC-009**: Manual editing reduces solver re-runs by 50%: admins make quick adjustments instead of regenerating schedules
- **SC-010**: Interface maintains performance with 100+ assignments: drag-and-drop and validation remain responsive <1 second

## Assumptions

1. **Desktop-First Interface**: We assume manual schedule editing primarily used on desktop/laptop (mouse and keyboard). Rationale: Complex scheduling tasks require large screen and precise pointing. Mobile support secondary. Touch gestures provided for tablets but desktop is primary use case.

2. **Single Admin Editing**: We assume one admin edits schedule at a time (no concurrent editing). Rationale: Prevents edit conflicts and simplifies implementation. If multiple admins need access, last-save-wins with conflict warning when save attempted. Real-time collaborative editing out of scope.

3. **Fairness Threshold**: We assume 30% above average is threshold for fairness warnings. Rationale: Allows some flexibility (volunteers with different availability naturally vary) while flagging significant imbalances. Threshold configurable per organization.

4. **Undo History Limit**: We assume 20-step undo history is sufficient. Rationale: Balances memory usage with practical undo needs. Most edits involve recent changes. Undo history cleared on page refresh (not persisted across sessions).

5. **Lock Persistence**: We assume locked assignments remain locked indefinitely until explicitly unlocked. Rationale: Admin decisions should persist. If solver constraints change (volunteer becomes unavailable), locked assignment flagged as violation but not automatically unlocked.

6. **Validation Performance**: We assume validation checks complete within 500ms for schedules up to 200 assignments. Rationale: Provides responsive UI experience. For larger schedules, validation may be debounced or run asynchronously with progress indicator.

7. **Conflict Priority**: We assume availability conflicts (hard constraints) take precedence over fairness issues (soft constraints) in warnings. Rationale: Unavailable volunteers cannot be assigned (physical impossibility) while fairness imbalances are suboptimal but valid.

8. **Swap Role Compatibility**: We assume swapped volunteers must be qualified for target roles (role requirements validated). Rationale: Prevents assigning volunteers to roles they cannot perform. Exception: Admin can override with explicit confirmation for special circumstances.

9. **Solver Integration**: We assume solver treats locked assignments as hard constraints (never violates). Rationale: Manual overrides represent business decisions that solver must respect. If locked assignments create unsolvable constraints, solver fails with clear error message.

10. **Edit History Retention**: We assume edit history retained for current session only (not persisted to database). Rationale: Undo/redo is session-specific feature. Historical edit tracking (audit logging) handled separately in security feature.

## Dependencies

1. **Existing Scheduling Solver**: Manual editing extends solver-generated schedules. Dependency: Solver must support locked assignment constraints and hybrid solver-manual workflow. Solver API must accept locked assignments as input.

2. **Schedule Display Interface**: Drag-and-drop requires visual schedule representation (calendar, list, grid). Dependency: Existing schedule view must be enhanced to support drag-and-drop interactions and real-time visual feedback.

3. **Constraint Validation Engine**: Real-time validation requires checking availability, role requirements, fairness. Dependency: Validation logic from solver must be exposed as API for frontend real-time checking.

4. **Assignment Data Model**: Locked assignments require data model extension. Dependency: Assignment entity must support locked status, locked by user, locked timestamp fields.

5. **Drag-and-Drop Library**: Complex drag-drop interactions benefit from library support. Dependency: May use frontend library (react-beautiful-dnd, HTML5 drag-and-drop API, or custom implementation) for consistent drag-drop behavior.

## Out of Scope

1. **Concurrent Editing**: Multiple admins editing same schedule simultaneously excluded. Feature assumes single-admin editing with last-save-wins conflict resolution. Real-time collaborative editing adds significant complexity and is rarely needed for volunteer scheduling.

2. **Version History**: Full schedule version history (snapshots at each edit) excluded. Feature provides session-based undo/redo only. Comprehensive version control with branching/merging can be added as separate feature if needed.

3. **Advanced Optimization Suggestions**: AI-powered schedule optimization suggestions (machine learning predictions, pattern recognition) excluded. Feature focuses on manual control with simple rule-based suggestions. Advanced AI features can be added separately.

4. **Bulk Import/Export**: Importing assignments from external files (CSV, Excel) or exporting edited schedules excluded from manual editing scope. Import/export handled as separate data management feature.

5. **Custom Validation Rules**: User-defined constraint rules beyond availability, coverage, fairness excluded. Feature uses standard built-in constraints. Custom constraint engine can be added as advanced feature for power users.

6. **Schedule Templates**: Saving manual edit patterns as reusable templates excluded. Feature focuses on one-time edits. Template functionality overlaps with recurring events and can be added separately if usage patterns emerge.

7. **Mobile App Drag-and-Drop**: Native mobile app drag-and-drop excluded (desktop web only). Mobile users can view schedules and make edits through simplified forms rather than drag-and-drop. Full mobile editing can be added based on usage patterns.

8. **Conflict Auto-Resolution**: Fully automatic conflict resolution without admin confirmation excluded. System provides suggestions but requires admin approval. Autonomous resolution risks unexpected changes and reduced admin control.

9. **Scheduling Rules Engine**: Complex scheduling rules (if-then logic, conditional assignments, multi-step workflows) excluded. Feature provides direct manual editing only. Rules engine can be added as separate automation feature.

10. **External Calendar Integration**: Syncing manual edits with external calendars (Google Calendar, Outlook) excluded from manual editing scope. Calendar integration handled as separate feature.
