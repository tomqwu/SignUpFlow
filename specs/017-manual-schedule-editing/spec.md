# Feature Specification: Manual Schedule Editing Interface

**Feature Branch**: `017-manual-schedule-editing`
**Created**: 2025-10-22
**Status**: Draft
**Type**: User Experience Enhancement (High Value)

---

## Overview

**Purpose**: Provide administrators with intuitive direct manipulation controls to fine-tune solver-generated schedules through drag-and-drop editing, role swapping, and manual overrides while maintaining schedule integrity through real-time constraint validation and conflict detection.

**Business Value**: Reduces time spent making post-solver schedule adjustments by 75% (from navigating multiple forms to direct visual manipulation), increases administrator confidence in automated scheduling by allowing manual corrections when needed, and prevents invalid schedule states through proactive constraint violation warnings before changes commit.

**Target Users**: Organization administrators (pastors, coordinators, event managers) who review and refine solver-generated schedules to address special circumstances, last-minute changes, or volunteer preferences not captured in automated constraints.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Drag-and-Drop Volunteer Assignment Between Time Slots (Priority: P1)

Administrator reassigns volunteer from one event to another by dragging their assignment card and dropping it onto a different time slot, with system immediately validating the change against availability constraints and role requirements before allowing the drop.

**Why this priority**: P1 - This is the core value proposition of manual editing. Direct manipulation is 10x faster than navigating edit forms. Without drag-and-drop, the feature provides minimal value over existing edit workflows.

**Independent Test**: Generate schedule with volunteer assigned to Sunday 10 AM service. Drag their assignment to Sunday 6 PM service. Verify constraint check occurs (availability, role match). If valid, verify assignment moves. If invalid, verify assignment snaps back with error message.

**Acceptance Scenarios**:

1. **Given** administrator views schedule with volunteer assigned to Event A, **When** they drag assignment and drop onto Event B time slot, **Then** system validates availability and role requirements for Event B within 200ms
2. **Given** drag-drop validation passes (volunteer available and role matches), **When** administrator releases mouse, **Then** assignment moves to new event and old event shows vacancy indicator
3. **Given** drag-drop validation fails (volunteer unavailable or wrong role), **When** administrator releases mouse, **Then** assignment snaps back to original position with error message "John Smith unavailable 6-8 PM" or "Role mismatch: needs Greeter, has Usher"
4. **Given** administrator drags assignment over multiple event slots, **When** mouse hovers over each slot, **Then** visual indicator shows valid (green border) or invalid (red border) drop target
5. **Given** successful drag-drop reassignment, **When** change completes, **Then** edit is marked as manual override and logged in change history

---

### User Story 2 - Real-Time Constraint Violation Detection and Visual Warnings (Priority: P1)

System continuously monitors schedule integrity and displays visual warnings (color-coded borders, warning icons, conflict badges) when manual edits create constraint violations such as availability conflicts, unfair workload distribution, or coverage gaps.

**Why this priority**: P1 - Critical safety mechanism preventing administrators from creating invalid schedules. Without real-time validation, manual edits could break volunteer availability or fairness constraints that took hours to configure.

**Independent Test**: Manually assign volunteer to time slot when they marked unavailable. Verify immediate visual warning appears on assignment (red border, warning icon). Verify warning message explains conflict. Remove assignment, verify warning disappears.

**Acceptance Scenarios**:

1. **Given** administrator manually assigns volunteer to event, **When** volunteer marked unavailable for that time, **Then** assignment displays with red border and warning icon within 200ms
2. **Given** assignment has constraint violation, **When** administrator hovers over warning icon, **Then** tooltip shows specific conflict details "Jane Doe marked unavailable 10 AM-12 PM on 2025-11-15"
3. **Given** manual edit creates fairness imbalance (one volunteer with 5 assignments, others with 1), **When** edit completes, **Then** fairness metrics panel shows warning "Workload imbalance detected" with affected volunteers highlighted
4. **Given** administrator removes volunteer from event creating coverage gap (role requirement not met), **When** assignment removed, **Then** event displays warning badge "Missing 1 Greeter"
5. **Given** multiple constraint violations exist, **When** administrator views schedule, **Then** summary panel shows violation count by type (3 availability conflicts, 2 coverage gaps, 1 fairness warning)

---

### User Story 3 - Swap Volunteers Between Roles (Priority: P1)

Administrator swaps two volunteers assigned to different roles at same event (e.g., swap Greeter and Usher positions) through intuitive drag-onto-drag operation, with system validating both volunteers qualify for their new roles before allowing swap.

**Why this priority**: P1 - Common real-world adjustment when volunteers request to swap duties or when role fit becomes apparent only after schedule generated. Manual form-based swapping requires 4+ clicks; drag-based swapping takes 1 action.

**Independent Test**: Create event with Volunteer A as Greeter and Volunteer B as Usher. Drag Volunteer A's assignment onto Volunteer B's assignment. Verify swap prompt appears. Confirm swap. Verify roles exchanged and both volunteers validated for new roles.

**Acceptance Scenarios**:

1. **Given** two volunteers assigned to different roles at same event, **When** administrator drags one assignment onto the other, **Then** swap confirmation dialog appears "Swap John (Greeter) with Jane (Usher)?"
2. **Given** swap confirmation shown, **When** administrator confirms, **Then** system validates both volunteers qualify for swapped roles (John can be Usher, Jane can be Greeter)
3. **Given** swap validation passes, **When** swap executes, **Then** both assignments update with new roles and change marked as manual override
4. **Given** swap validation fails (one volunteer doesn't qualify for new role), **When** validation completes, **Then** error message displays "Cannot swap: John not qualified for Usher role" and swap cancelled
5. **Given** successful swap, **When** administrator views change history, **Then** log shows "Swapped John Smith (Greeter ↔ Usher) with Jane Doe" with timestamp

---

### User Story 4 - Add and Remove Manual Assignments (Priority: P1)

Administrator manually adds volunteer to unfilled role slot (solver couldn't find assignment) or removes volunteer from assignment (volunteer requested last-minute time off), with system immediately updating coverage indicators and fairness metrics.

**Why this priority**: P1 - Essential for handling situations automated solver cannot address (last-minute availability changes, volunteer special requests, manual coverage adjustments). Without add/remove, manual editing cannot address coverage gaps.

**Independent Test**: Find event with unfilled Greeter role. Click "+ Add Volunteer" button. Select volunteer from list. Verify assignment created and coverage gap resolved. Remove assignment. Verify coverage gap reappears.

**Acceptance Scenarios**:

1. **Given** event has unfilled role slot showing "Missing 1 Greeter", **When** administrator clicks "Add Volunteer" button on empty slot, **Then** volunteer selection dropdown appears showing only volunteers qualified for Greeter role and available at event time
2. **Given** volunteer selected from dropdown, **When** administrator confirms addition, **Then** assignment created, coverage gap resolved, and fairness metrics updated to reflect additional assignment
3. **Given** assignment exists, **When** administrator clicks "Remove" button or drags assignment to trash zone, **Then** confirmation prompt appears "Remove John Smith from Greeter role?" with warning if creates coverage gap
4. **Given** remove confirmation accepted, **When** removal completes, **Then** assignment deleted, event shows coverage gap if role unfilled, and fairness metrics updated to reflect removed assignment
5. **Given** manual addition creates fairness imbalance, **When** assignment added, **Then** fairness warning displays showing affected volunteer now has disproportionate assignments

---

### User Story 5 - Lock Manual Assignments to Preserve Across Solver Re-Runs (Priority: P2)

Administrator marks specific assignments as "locked" indicating they should not be changed when scheduling solver re-runs, preserving manual corrections while allowing solver to optimize remaining unlocked assignments.

**Why this priority**: P2 - Important for protecting manual work, but manual editing (P1) must exist first. Allows iterative refinement where administrators lock satisfactory assignments and re-run solver for problematic areas.

**Independent Test**: Manually edit assignment. Lock it (pin icon). Re-run scheduling solver. Verify locked assignment unchanged. Verify unlocked assignments may have changed.

**Acceptance Scenarios**:

1. **Given** administrator manually edited assignment, **When** they click lock icon on assignment, **Then** assignment displays with lock indicator (padlock icon, different border color) and marked as protected
2. **Given** multiple assignments locked, **When** administrator re-runs scheduling solver, **Then** solver generates new schedule respecting all locked assignments as fixed constraints
3. **Given** locked assignment exists, **When** solver re-runs and would normally assign that volunteer elsewhere, **Then** solver treats locked assignment as unavailable time (volunteer cannot be assigned to conflicting events)
4. **Given** administrator wants to unlock assignment, **When** they click unlock icon, **Then** confirmation prompt appears "Unlock this assignment? Next solver run may reassign." and assignment returned to unlocked state on confirmation
5. **Given** locked assignments create unsolvable constraint set, **When** solver runs, **Then** solver returns error "Cannot generate schedule: locked assignments create conflicts" with details of conflicting locks

---

### User Story 6 - Undo and Redo Manual Edits (Priority: P2)

Administrator reverses recent manual changes through undo button (up to last 20 actions) and restores undone changes through redo button, with visual preview showing what will change before undo/redo executes.

**Why this priority**: P2 - Important safety net for exploratory editing and mistake recovery, but not critical for basic manual editing functionality. Reduces fear of making changes by allowing easy reversal.

**Independent Test**: Make 3 manual edits (drag assignment, remove volunteer, add volunteer). Click undo 3 times. Verify changes reversed in reverse chronological order. Click redo 2 times. Verify 2 changes restored.

**Acceptance Scenarios**:

1. **Given** administrator makes manual edit (drag, add, remove, swap), **When** edit completes, **Then** action added to undo stack and undo button becomes enabled
2. **Given** undo stack not empty, **When** administrator clicks undo button, **Then** preview tooltip shows "Undo: Move John Smith back to 10 AM service" before executing
3. **Given** undo executed, **When** action reverses, **Then** schedule state restored to before that action and action moved to redo stack
4. **Given** redo stack not empty, **When** administrator clicks redo button, **Then** preview tooltip shows "Redo: Move John Smith to 6 PM service" and action re-applies
5. **Given** undo stack contains 20 actions (maximum), **When** administrator makes 21st edit, **Then** oldest action removed from stack and new action added (rolling 20-action history)

---

### User Story 7 - Conflict Resolution Suggestions (Priority: P3)

System analyzes constraint violations and provides actionable suggestions (alternative volunteers, time slot swaps, role reassignments) that would resolve conflicts with minimal schedule disruption.

**Why this priority**: P3 - Nice-to-have assistance feature, but administrators can resolve conflicts manually without suggestions. Improves efficiency but not essential for core functionality.

**Independent Test**: Create availability conflict (assign volunteer to time they're unavailable). Click "Suggest Fix" button. Verify system suggests alternative volunteers available at that time. Select suggestion. Verify conflict resolved.

**Acceptance Scenarios**:

1. **Given** constraint violation exists (availability conflict), **When** administrator clicks "Suggest Fix" button on violated assignment, **Then** suggestion panel shows 3-5 alternative volunteers available at that time qualified for the role
2. **Given** suggestion alternatives displayed, **When** administrator clicks "Apply" on suggestion, **Then** original assignment replaced with suggested volunteer and violation resolved
3. **Given** no simple fix exists (no alternatives available), **When** administrator requests suggestions, **Then** message displays "No qualified alternatives available. Try: 1) Change event time, 2) Add volunteer to team, 3) Mark requirement as optional"
4. **Given** fairness imbalance exists, **When** administrator requests suggestions, **Then** system suggests redistributing assignments from overloaded volunteer to underutilized volunteers with specific swap recommendations

---

### Edge Cases

- **Simultaneous edits (multi-user)**: If two administrators edit same schedule simultaneously, last save wins with warning "Schedule changed by another user - reload to see latest version"
- **Solver re-run during manual editing**: If solver triggered while administrator actively editing, block solver execution with message "Manual editing in progress - save or discard changes before running solver"
- **Locked assignment creates impossible constraint**: When locked assignments make schedule unsolvable, solver error provides conflict details with option to identify and unlock problematic assignments
- **Undo after solver re-run**: Undo stack clears when solver generates new schedule (cannot undo automated changes, only manual changes since last solver run)
- **Drag-drop to filled slot**: When administrator drags assignment to slot already filled, offer choice "Replace existing assignment or swap volunteers?"
- **Assignment drag to incompatible event**: When dragging assignment to event with incompatible role requirements, drop rejected with message "Event requires Greeter role, volunteer assigned as Usher"
- **Mass assignment changes**: When fairness violation affects 10+ volunteers, fairness warning shows top 5 most imbalanced and link to "View all fairness issues"
- **Locked assignment with outdated availability**: If volunteer updates availability making locked assignment invalid, warning displays "Locked assignment conflicts with updated availability - review and unlock if needed"

---

## Requirements *(mandatory)*

### Functional Requirements

#### Drag-and-Drop Interaction

- **FR-001**: System MUST support drag-and-drop of volunteer assignments between event time slots with visual drag preview
- **FR-002**: During drag operation, system MUST highlight valid drop targets (green border) and invalid drop targets (red border) based on real-time constraint validation
- **FR-003**: When assignment dropped on valid target, system MUST move assignment to new event within 300ms and update schedule display
- **FR-004**: When assignment dropped on invalid target, system MUST animate assignment snapping back to original position and display constraint violation message
- **FR-005**: System MUST support touch-based drag-and-drop for tablet users with minimum 44x44px touch targets

#### Real-Time Constraint Validation

- **FR-006**: System MUST validate assignments against volunteer availability constraints within 200ms of edit action
- **FR-007**: System MUST validate assignments against role qualification requirements (volunteer must be qualified for assigned role)
- **FR-008**: System MUST calculate and display fairness metrics (assignment count per volunteer) updated within 500ms of any edit
- **FR-009**: System MUST detect coverage gaps (unfilled role requirements) and display warnings on affected events
- **FR-010**: Constraint violations MUST display with visual indicators: red border for conflicts, yellow for warnings, orange for fairness imbalances
- **FR-011**: Violation tooltips MUST show specific conflict details including volunteer name, time, and reason (e.g., "Jane Doe unavailable 2-4 PM")

#### Volunteer Swapping

- **FR-012**: When assignment dragged onto another assignment at same event, system MUST offer swap confirmation dialog
- **FR-013**: Swap operation MUST validate both volunteers qualify for their new roles before executing swap
- **FR-014**: Successful swap MUST update both assignments atomically (both change or neither changes)
- **FR-015**: Failed swap MUST display specific reason (e.g., "John not qualified for Usher role") and leave assignments unchanged

#### Add and Remove Assignments

- **FR-016**: Empty role slots MUST display "+ Add Volunteer" button visible on hover or tap
- **FR-017**: Add volunteer dropdown MUST filter to only qualified volunteers available at event time
- **FR-018**: Adding assignment MUST update coverage indicators, fairness metrics, and constraint validations within 500ms
- **FR-019**: Remove assignment action MUST display confirmation prompt warning if removal creates coverage gap
- **FR-020**: Removing assignment MUST mark assignment as deleted and update affected metrics

#### Manual Override Tracking

- **FR-021**: System MUST distinguish solver-generated assignments from manually edited assignments with visual indicator
- **FR-022**: All manual edits MUST log to change history with timestamp, administrator name, and action description
- **FR-023**: Change history MUST retain last 100 manual edit actions per schedule
- **FR-024**: Manual edit indicators MUST persist across page refreshes and user sessions

#### Assignment Locking

- **FR-025**: Each assignment MUST have lock/unlock toggle control (pin icon or checkbox)
- **FR-026**: Locked assignments MUST display distinct visual treatment (lock icon, different border color)
- **FR-027**: When solver re-runs, locked assignments MUST be treated as fixed constraints that cannot be changed
- **FR-028**: Solver MUST treat locked assignment times as unavailable for that volunteer (prevent double-booking)
- **FR-029**: Attempting to unlock assignment MUST display confirmation prompt explaining solver may reassign on next run

#### Undo and Redo

- **FR-030**: System MUST maintain undo stack of last 20 manual edit actions with full state for each action
- **FR-031**: Undo button MUST display preview tooltip showing what will reverse before execution
- **FR-032**: Undo operation MUST restore schedule state to before reversed action within 300ms
- **FR-033**: Redo button MUST be enabled when redo stack not empty, disabled otherwise
- **FR-034**: Any new manual edit MUST clear redo stack (cannot redo after making new change)
- **FR-035**: Solver re-run MUST clear both undo and redo stacks (automated changes not reversible)

#### Conflict Resolution

- **FR-036**: Constraint violations MUST display "Suggest Fix" button providing resolution options
- **FR-037**: Suggestion engine MUST analyze violations and propose 3-5 alternative solutions when available
- **FR-038**: Suggestions MUST rank alternatives by minimal disruption (fewest additional changes needed)
- **FR-039**: Applying suggestion MUST execute recommended change and re-validate schedule constraints
- **FR-040**: When no alternatives exist, system MUST display actionable guidance for manual resolution

### Key Entities

- **Manual Edit Action**: Record of administrator's schedule modification
  - Fields: action type (drag, swap, add, remove, lock, unlock), timestamp, administrator ID, affected assignments (before and after state), constraint violations created/resolved
  - Relationships: Belongs to schedule, references volunteer assignments
  - Behavior: Stored in undo stack, logged to change history, can be reversed (undo) or re-applied (redo)

- **Assignment Lock**: Marker indicating assignment protected from solver changes
  - Fields: assignment ID, locked by (administrator ID), locked at (timestamp), lock reason (optional text)
  - Relationships: References volunteer assignment
  - Behavior: Prevents solver from modifying assignment, adds constraint to solver (volunteer unavailable at this time)

- **Constraint Violation**: Detected conflict between assignment and constraints
  - Fields: violation type (availability conflict, role mismatch, fairness imbalance, coverage gap), severity (error, warning), affected assignment IDs, violation message, resolution suggestions
  - Relationships: References assignments causing violation
  - Behavior: Triggers visual warnings, enables suggestion engine, blocks invalid edits at error severity

- **Schedule Edit Session**: Container for all manual edits made between solver runs
  - Fields: session ID, started at (timestamp), last modified, administrator ID, total edits count, undo stack (action history), redo stack (reversed actions)
  - Relationships: Has many manual edit actions, belongs to schedule
  - Behavior: Maintains edit history, supports undo/redo, clears on solver re-run

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Administrators complete manual schedule adjustments (moving 5 volunteers) in under 2 minutes compared to 8 minutes using form-based editing (75% time reduction)
- **SC-002**: Drag-and-drop operations complete within 300ms from drop to UI update (perceived as instant feedback)
- **SC-003**: Constraint validation executes within 200ms providing immediate feedback during drag hover
- **SC-004**: 90% of administrators successfully complete first drag-and-drop edit without training or help documentation
- **SC-005**: Invalid edits (constraint violations) are prevented 100% of the time through real-time validation before commit
- **SC-006**: Manual edits preserved through solver re-runs with 100% fidelity when assignments locked
- **SC-007**: Undo/redo operations restore schedule state with 100% accuracy across all edit types
- **SC-008**: Conflict resolution suggestions resolve violations in 70% of cases with single-click application
- **SC-009**: Support tickets related to "can't fix automated schedule" decrease by 60% after manual editing launch
- **SC-010**: Administrator satisfaction with schedule refinement workflow increases from 6/10 to 9/10
- **SC-011**: Time spent reviewing and correcting solver schedules reduces from 30 minutes to 10 minutes per schedule (65% reduction)
- **SC-012**: Zero instances of invalid schedules created through manual editing (constraint validation prevents all invalid states)

---

## Assumptions

- Administrators review solver-generated schedules before publishing and typically need to make 3-8 manual adjustments per schedule
- Drag-and-drop is familiar interaction pattern for target users (administrators comfortable with modern web interfaces)
- Real-time constraint validation sufficient; administrators do not need "what-if" simulation mode
- Most manual edits are simple (move one volunteer, swap two volunteers); complex multi-step edits are rare
- Undo/redo with 20-action history covers 95% of real-world mistake recovery needs; longer history not required
- Locked assignments typically represent 10-20% of total schedule (not entire schedules locked)
- Manual editing sessions last 5-30 minutes; multi-hour editing sessions with hundreds of edits are rare

---

## Out of Scope

- **Bulk operations**: Multi-select and drag multiple assignments simultaneously (single assignment edits only)
- **Schedule comparison view**: Side-by-side comparison of solver-generated vs manually edited schedules
- **Edit conflict resolution (multi-user)**: Real-time conflict resolution when multiple administrators edit simultaneously (last save wins)
- **Custom constraint creation**: Adding new constraint types during manual editing (use constraint configuration for new constraints)
- **Automated optimization suggestions**: AI-powered suggestions for improving entire schedule (manual editing for specific known issues only)
- **Assignment templates**: Saving and applying recurring assignment patterns across multiple schedules
- **Mobile app support**: Manual editing optimized for desktop/tablet only; phone screens too small for effective drag-and-drop

