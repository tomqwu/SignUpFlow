# Spec-Kit Integration Guide

SignUpFlow now uses [GitHub Spec-Kit](https://github.com/github/spec-kit) for **spec-driven development**, where specifications become executable and drive implementation.

## What is Spec-Driven Development?

Instead of writing code first and documentation later, spec-driven development:
1. **Starts with specifications** - Define WHAT you're building before HOW
2. **Makes specs executable** - Specifications directly generate working implementations
3. **Maintains alignment** - Code always matches the spec (single source of truth)
4. **Enables AI collaboration** - AI agents understand specs better than scattered docs

## Quick Start

### Prerequisites

Spec-kit is already installed and initialized! You just need to use the slash commands with Claude Code.

### Available Commands

All spec-kit commands are available as slash commands in Claude Code:

#### Core Workflow (Run in Order)

1. **`/speckit.constitution`** - Establish project principles and development guidelines
   - Defines core values, constraints, and technical standards
   - Creates the "constitution" that guides all development

2. **`/speckit.specify`** - Create baseline specification
   - Detailed requirements and acceptance criteria
   - User stories and feature specifications

3. **`/speckit.plan`** - Create implementation plan
   - Technical architecture and approach
   - Dependency mapping and sequencing

4. **`/speckit.tasks`** - Generate actionable tasks
   - Breakdown plan into concrete implementation tasks
   - Task dependencies and ordering

5. **`/speckit.implement`** - Execute implementation
   - AI-assisted implementation following specs
   - Validates against specifications

#### Optional Enhancement Commands

- **`/speckit.clarify`** (before `/speckit.plan`) - Ask structured questions to de-risk ambiguous areas
- **`/speckit.checklist`** (after `/speckit.plan`) - Generate quality checklists for completeness
- **`/speckit.analyze`** (after `/speckit.tasks`) - Cross-artifact consistency & alignment report

## Example Workflow

### Scenario: Add Password Reset Feature

```bash
# Step 1: Define the feature specification
/speckit.specify

# AI will guide you through:
# - User stories (As a user, I want to...)
# - Acceptance criteria (GIVEN/WHEN/THEN)
# - Edge cases and error handling
# - Security requirements

# Step 2: Create implementation plan
/speckit.plan

# AI will:
# - Design API endpoints
# - Database schema changes
# - Frontend UI components
# - Email integration requirements

# Step 3: Generate tasks
/speckit.tasks

# AI will create:
# - Backend tasks (API, DB, services)
# - Frontend tasks (UI, forms, validation)
# - Testing tasks (E2E, unit, integration)
# - Documentation tasks

# Step 4: Implement
/speckit.implement

# AI will execute tasks one by one:
# - Write code following specs
# - Run tests
# - Verify against acceptance criteria
# - Update documentation
```

## File Organization

Spec-kit creates and maintains files in:

```
SignUpFlow/
├── .claude/
│   ├── commands/                    # Slash command definitions (COMMIT THESE)
│   │   ├── speckit.constitution.md
│   │   ├── speckit.specify.md
│   │   ├── speckit.plan.md
│   │   ├── speckit.tasks.md
│   │   ├── speckit.implement.md
│   │   ├── speckit.clarify.md
│   │   ├── speckit.checklist.md
│   │   └── speckit.analyze.md
│   └── settings.local.json          # Local settings (GITIGNORED)
│
└── specs/                           # Generated specifications (COMMIT THESE)
    ├── constitution.md              # Project principles
    ├── features/                    # Feature specifications
    │   ├── password-reset.md
    │   └── email-invitations.md
    ├── plans/                       # Implementation plans
    │   ├── password-reset-plan.md
    │   └── email-invitations-plan.md
    └── tasks/                       # Task breakdowns
        ├── password-reset-tasks.md
        └── email-invitations-tasks.md
```

## Integration with Existing Workflow

Spec-kit **enhances** our existing workflow, it doesn't replace it:

### Before Spec-Kit
```
User Request → Brainstorm → Implement → Test → Document
```

### With Spec-Kit
```
User Request → /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement
                                                                          ↓
                                                                    Tests + Docs
```

### Benefits

✅ **Better Requirements** - Thorough specification upfront catches issues early
✅ **Consistent Quality** - AI follows specs exactly, no shortcuts
✅ **Living Documentation** - Specs stay updated as implementation evolves
✅ **Team Alignment** - Everyone works from the same source of truth
✅ **AI Efficiency** - AI understands structured specs better than natural language

## Installation (For New Developers)

Spec-kit is already integrated! But if you need to set it up elsewhere:

```bash
# Install uv (Python package installer)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install spec-kit
uv tool install git+https://github.com/github/spec-kit.git

# Initialize in project
specify init --here --ai claude --force
```

## Documentation

- **Spec-Kit Official Docs**: https://github.github.io/spec-kit/
- **GitHub Repository**: https://github.com/github/spec-kit
- **Video Overview**: Check repo README for latest videos

## Best Practices

### DO
✅ Start with `/speckit.specify` for new features
✅ Run `/speckit.analyze` before major implementations
✅ Commit all spec files (`specs/`) to version control
✅ Update specs when requirements change
✅ Use `/speckit.constitution` to establish team standards

### DON'T
❌ Skip specification step and jump to implementation
❌ Manually edit generated task files (use `/speckit.tasks` again)
❌ Commit `settings.local.json` (it's user-specific)
❌ Ignore spec validation warnings from AI

## Troubleshooting

### "Command not found: /speckit.*"

**Problem**: Slash commands not available in Claude Code

**Solution**:
1. Verify files exist in `.claude/commands/`
2. Restart Claude Code
3. Check that you're in the project directory

### "Spec file not found"

**Problem**: Trying to run `/speckit.plan` before `/speckit.specify`

**Solution**: Run commands in order (specify → plan → tasks → implement)

### "Inconsistency detected in spec"

**Problem**: `/speckit.analyze` found mismatches

**Solution**:
1. Review the inconsistency report
2. Update the spec with `/speckit.specify`
3. Re-run `/speckit.plan` and `/speckit.tasks`
4. Then proceed to `/speckit.implement`

## Example: Email Feature (Already Implemented)

The email invitation feature we just completed could have been built with spec-kit:

```markdown
# specs/features/email-invitations.md

## Feature: Email Invitation System

### User Story
As an admin, I want to send email invitations to new users via Mailtrap,
so that they can join the organization without manual account creation.

### Acceptance Criteria
- ✅ Admin can send invitations with email address and role
- ✅ Email sent via SMTP (Mailtrap for dev)
- ✅ Beautiful HTML template with call-to-action button
- ✅ Graceful error handling (email failure doesn't break invitation)
- ✅ Environment variable configuration (no hardcoded credentials)
- ✅ Comprehensive testing (unit + E2E)

### Technical Requirements
- SMTP integration via Mailtrap
- EmailService class with environment variable support
- Integration with POST /api/invitations endpoint
- HTML email template with gradient styling
- Unit tests for email service
- E2E tests for complete workflow
- Documentation for local setup
```

Then the AI would generate the implementation plan, tasks, and code - all following the spec!

## Next Steps

1. **Read `/speckit.constitution` command** to understand project principles workflow
2. **Try a small feature** using the spec-driven approach
3. **Review generated specs** in `specs/` directory
4. **Share with team** to align on the new workflow

---

**Last Updated**: 2025-10-20
**Status**: ✅ Installed and integrated
**Commands Available**: 8 slash commands (constitution, specify, plan, tasks, implement, clarify, checklist, analyze)
