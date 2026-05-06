# Legacy ad-hoc migration scripts

These two Python scripts predate the project's adoption of Alembic and ran
against a single SQLite dev database (`roster.db`). They are preserved here
for historical reference only — do **not** invoke them on a fresh checkout.

| Legacy script                                         | Schema change                                                                      | Canonical Alembic revision                                                                          |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `add_language_to_person.py`                           | Adds `people.language` (`VARCHAR DEFAULT 'en' NOT NULL`)                            | Baked into `alembic/versions/f18c6691c7ab_initial.py` — `people.language` is in the initial schema. |
| `add_recurring_events_schema.py`                      | Creates `recurring_series` + `recurrence_exceptions` tables and adds `events.series_id`, `events.occurrence_sequence`, `events.is_exception`. | Baked into `alembic/versions/f18c6691c7ab_initial.py` — all three columns and both tables are in the initial schema. |

## How to migrate a fresh database now

```bash
poetry run alembic upgrade head
```

This applies `f18c6691c7ab_initial` followed by `7ba388eecd31_add_assignment_status_real`,
producing the same end state as the legacy scripts (and more).

## Why the duplicates remain

If you have a long-lived dev database from before Alembic was adopted, the
legacy scripts may still be the easiest way to bring it up to the
`f18c6691c7ab_initial` baseline without dropping data. New environments
should always use Alembic.
