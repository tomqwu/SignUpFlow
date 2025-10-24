# Feature Progress: [FEATURE_NAME]

**Feature ID**: [FEATURE_ID] (e.g., 011-billing-subscription-system)
**Started**: [DATE]
**Status**: [PHASE] - [STATUS_EMOJI]
**Branch**: `[BRANCH_NAME]`

---

## Current Phase: [PHASE_NAME]

**Progress**: [X]% complete
**Blockers**: [NONE | List blockers]
**Next Action**: [Specific next step]

---

## Workflow Phases

### Phase 1: Specification ✅ | 🔄 | ⏳
**Status**: [COMPLETE | IN_PROGRESS | PENDING]
**Duration**: [Time spent]

- [ ] Create feature branch
- [ ] Run `/speckit.specify "[description]"`
- [ ] Complete User Scenarios (min 3, independent E2E tests)
- [ ] Complete Edge Cases (min 3)
- [ ] Complete Functional Requirements (grouped by category)
- [ ] Define Key Entities (complete field lists)
- [ ] Define Success Criteria (measurable outcomes)
- [ ] Create requirements validation checklist
- [ ] Resolve clarifications (max 3)
- [ ] Validate spec against constitution compliance

**Spec File**: `specs/[FEATURE_ID]/spec.md`
**Checklist**: `specs/[FEATURE_ID]/checklists/requirements.md`

### Phase 2: Planning ✅ | 🔄 | ⏳
**Status**: [COMPLETE | IN_PROGRESS | PENDING]
**Duration**: [Time spent]

- [ ] Run `/speckit.plan`
- [ ] Review generated technical approach
- [ ] Validate architecture decisions
- [ ] Confirm technology choices
- [ ] Review API design
- [ ] Review database schema
- [ ] Approve plan

**Plan File**: `specs/[FEATURE_ID]/plan.md`

### Phase 3: Task Breakdown ✅ | 🔄 | ⏳
**Status**: [COMPLETE | IN_PROGRESS | PENDING]
**Duration**: [Time spent]

- [ ] Run `/speckit.tasks`
- [ ] Review generated task list
- [ ] Validate task dependencies
- [ ] Confirm implementation order
- [ ] Approve tasks

**Tasks File**: `specs/[FEATURE_ID]/tasks.md`

### Phase 4: Implementation ✅ | 🔄 | ⏳
**Status**: [COMPLETE | IN_PROGRESS | PENDING]
**Duration**: [Time spent]

- [ ] Run `/speckit.implement`
- [ ] E2E tests written FIRST (failing)
- [ ] Backend implementation
- [ ] Frontend implementation
- [ ] E2E tests passing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual browser verification
- [ ] Code review
- [ ] Constitution compliance verified

**Implementation**: [Files modified/created]

### Phase 5: Validation ✅ | 🔄 | ⏳
**Status**: [COMPLETE | IN_PROGRESS | PENDING]
**Duration**: [Time spent]

- [ ] All tests passing (100%)
- [ ] No console errors
- [ ] No network errors
- [ ] i18n complete (6 languages)
- [ ] Security validated (RBAC, multi-tenant)
- [ ] Performance acceptable
- [ ] Documentation updated

**Test Coverage**: [X/Y tests passing]

### Phase 6: Merge ✅ | 🔄 | ⏳
**Status**: [COMPLETE | IN_PROGRESS | PENDING]
**Duration**: [Time spent]

- [ ] Branch up to date with main
- [ ] All conflicts resolved
- [ ] Final test run passing
- [ ] Merge to main
- [ ] Delete feature branch

---

## Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **User Stories** | [X/Y] | [Y] | [✅ \| 🔄 \| ⏳] |
| **Requirements** | [X/Y] | [Y] | [✅ \| 🔄 \| ⏳] |
| **Tasks Complete** | [X/Y] | [Y] | [✅ \| 🔄 \| ⏳] |
| **Tests Passing** | [X/Y] | [Y] | [✅ \| 🔄 \| ⏳] |
| **Days Elapsed** | [X] | [Y] | [✅ \| 🔄 \| ⏳] |

---

## Decisions Made

### Decision 1: [Decision Title]
**Context**: [Why this decision was needed]
**Options Considered**: [List alternatives]
**Chosen**: [Selected option]
**Rationale**: [Why this was chosen]
**Date**: [DATE]

---

## Blockers & Risks

### Active Blockers
- **BLOCKER-001**: [Description] - [Impact] - [Mitigation plan]

### Resolved Blockers
- **BLOCKER-001**: [Description] - ✅ RESOLVED [Date] - [How resolved]

### Risks
- **RISK-001**: [Description] - [Probability: HIGH/MEDIUM/LOW] - [Impact: HIGH/MEDIUM/LOW] - [Mitigation]

---

## Constitution Compliance Checklist

- [ ] **E2E Testing First**: E2E tests written before implementation
- [ ] **Security First**: JWT auth, bcrypt, RBAC enforced
- [ ] **Multi-tenant Isolation**: All queries filter by org_id
- [ ] **Test Coverage**: ≥99% pass rate, no failing tests
- [ ] **i18n by Default**: All text in 6 languages
- [ ] **Code Quality**: No TODOs, no mocks, follows patterns
- [ ] **Clear Documentation**: CLAUDE.md, API docs updated

---

## Session Log

### [DATE] - Session [N]
**Duration**: [Time]
**Phase**: [Phase name]
**Completed**:
- [Task 1]
- [Task 2]

**Next Session**:
- [Task 1]
- [Task 2]

**Notes**: [Any important observations]

---

## Quick Reference

**Files**:
- Spec: `specs/[FEATURE_ID]/spec.md`
- Plan: `specs/[FEATURE_ID]/plan.md`
- Tasks: `specs/[FEATURE_ID]/tasks.md`
- Checklist: `specs/[FEATURE_ID]/checklists/requirements.md`
- Progress: `specs/[FEATURE_ID]/progress.md` (this file)

**Commands**:
```bash
# Specification
/speckit.specify "[description]"

# Planning
/speckit.plan

# Tasks
/speckit.tasks

# Implementation
/speckit.implement

# Clarifications
/speckit.clarify

# Validation
/speckit.checklist

# Analysis
/speckit.analyze
```

---

**Last Updated**: [DATE]
**Updated By**: [Claude Code | Human]
