# Scheduling Constraints

The REST application persists a deliberately small set of person-level scheduling
rules. Every saved rule is validated before storage and mapped to the same
`ConstraintBinding` model used by the CLI solver. Unknown names, extra parameters,
invalid periods, non-positive values, incompatible hard/soft modes, and non-positive
soft weights return `422`; the solver never treats them as no-ops.

## Supported REST Rules

| `predicate` | Type | Required `params` | Optional `params` | Solver action |
| --- | --- | --- | --- | --- |
| `max_assignments` | hard | `period`, `max_count` | `applies_to` | `enforce_cap` |
| `min_gap_hours` | hard | `min_hours` | `applies_to` | `enforce_min_gap_hours` |
| `cooldown` | soft | `cooldown_days` | `applies_to` | `penalize_if: cooldown` |

`period` accepts `P1M` for a calendar month or `P{N}D`, such as `P7D`, for a
rolling N-day window centered on the candidate event date. Positive integers are
required for counts, hours, days, and soft weights. `applies_to` is a non-empty
list of exact event types; omit it to apply the rule to all event types.

The solver always enforces availability, time off, distinct people per role slot,
and no overlapping assignments. Do not save a separate `no_overlap` rule.

## REST Examples

```json
{
  "org_id": "grace-church",
  "key": "two-services-per-week",
  "type": "hard",
  "predicate": "max_assignments",
  "params": {
    "period": "P7D",
    "max_count": 2,
    "applies_to": ["service"]
  }
}
```

```json
{
  "org_id": "city-basketball",
  "key": "prefer-rested-players",
  "type": "soft",
  "weight": 25,
  "predicate": "cooldown",
  "params": {"cooldown_days": 3, "applies_to": ["game", "practice"]}
}
```

## CLI Equivalent

CLI workspaces continue to use the explicit YAML `ConstraintBinding` shape. For
example, the first REST rule maps to:

```yaml
key: two-services-per-week
scope: person
applies_to: [service]
severity: hard
then:
  enforce_cap:
    period: P7D
    max_count: 2
```

CLI JSON solutions include both `assignees` and `assigned_roles`. API solutions
persist the same selected role on every assignment. Existing rows containing old
free-form expressions must be replaced with a supported rule before solving; a
validation response names the invalid rule instead of silently dropping it.

## Recurring Availability

Recurring availability uses iCalendar RRULE text and is separate from saved
scheduling constraints. New RRULE writes are parsed before mutation. If a legacy
database contains malformed RRULE text, solve returns `422` with the availability
record and person identifiers.

## Boundaries

The REST mapper is not an arbitrary expression language. Team eligibility,
safeguarding policy, venue travel, family grouping, and sport tactics need explicit
product rules and tests before support. The CLI retains existing event/schedule
bindings used by checked-in fixtures; REST support is limited to the table above.
