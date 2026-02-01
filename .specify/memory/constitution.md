# SignUpFlow Constitution

> A roster and scheduling system with email/SMS notifications.

## Version
1.1.0

---

## 🔍 Context Detection

### Context A: Ralph Loop (Implementation Mode)

You are in a Ralph loop if:
- Started by `ralph-loop.sh`
- Prompt mentions "implement spec"

**In this mode:**
- Focus on implementation
- Pick highest priority incomplete spec (from `specs/`)
- Complete ALL acceptance criteria
- Output `<promise>DONE</promise>` when 100% complete

### Context B: Interactive Chat

When not in a Ralph loop:
- Be helpful and conversational
- Create specs for new features

---

## Core Principles

### I. Native First
Prefer native Poetry + SQLite setup over Docker for local development.

### II. Test-Driven Implementation
Always verify changes with existing tests in `tests/`. Add new tests if acceptance criteria require it.

### III. Simplicity & YAGNI
Build exactly what's needed, nothing more.

### IV. Safety & Reliability (CRITICAL)
- **Email/SMS:** Transactional messaging MUST be disabled by default (`EMAIL_ENABLED=false`, `SMS_ENABLED=false` in `.env`) until full user workflows are verified with E2E tests.
- **Payments:** Payment/Billing functions MUST be mocked or disabled for local development to prevent accidental charges.

---

## Autonomy Configuration

### YOLO Mode: DISABLED
### Git Autonomy: ENABLED (Commit changes when done)

---

## Ralph Loop Scripts

```bash
./scripts/ralph-loop.sh           # Build mode
./scripts/ralph-loop.sh 20        # Max 20 iterations
```

---

## The Magic Word

When user says "Ralph, start working", provide the terminal command.

---

**Created:** 2026-02-01
**Updated:** 2026-02-01 (Added Principle IV: Safety & Reliability)
