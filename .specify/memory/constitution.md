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

### Current Validation Policy (2026-09-13)
No CI checks. Run all code review, static analysis, migrations, tests, security
scans and artifact validation locally. Record evidence for the pushed revision;
never recreate hosted checks or require CI statuses. Follow `docs/ROADMAP.md`
and `docs/TESTING.md` over historical specification proposals. Reviewer agents
must not merge; builders require complete local evidence and GitHub mergeability.

### I. Native First
Prefer native Poetry + SQLite setup over Docker for local development.

### II. Test-Driven Implementation
Write the smallest failing regression before implementation. Verify every
change with applicable tests in `tests/`, then run `make test-all` before a PR.

### III. Simplicity & YAGNI
Build exactly what's needed, nothing more.

### IV. Safety & Reliability (CRITICAL)
- **Email/SMS:** Transactional messaging MUST be disabled by default (`EMAIL_ENABLED=false`, `SMS_ENABLED=false` in `.env`) until full user workflows are verified with E2E tests.
- **Payments:** Payment/Billing functions MUST be mocked or disabled for local development to prevent accidental charges.

---

## Autonomy Configuration

### YOLO Mode: DISABLED
### Git Autonomy: SCOPED (Only explicit owned paths; reviewer never merges)

---

## Ralph Loop Scripts

```bash
./scripts/ralph-loop.sh --mode plan --prompt prompt.md --work-item work-item.json
./scripts/ralph-loop.sh --mode build --prompt prompt.md \
  --work-item work-item.json --evidence local-evidence.json
```

Both Claude and Gemini entry points use the same finite runner. One iteration
is the default; the maximum is 20. Auto-approval and automatic model changes are
disabled. See `docs/AGENT_RUNNER.md`.

---

## The Magic Word

When user says "Ralph, start working", provide the terminal command.

---

**Created:** 2026-02-01
**Updated:** 2026-02-01 (Added Principle IV: Safety & Reliability)
