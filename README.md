# Roster CLI

A production-ready local file-driven constraint rostering engine for scheduling cricket leagues, church volunteers, and on-call rotations.

## Features

- **Three Built-in Templates**: Cricket league schedules, church volunteer rosters, on-call rotations
- **Constraint-Based Scheduling**: Hard and soft constraints with pluggable solver architecture
- **SQLite Database Backend**: Persistent storage with SQLAlchemy ORM for all roster data
- **Hash-Based Player IDs**: Secure 12-character hexadecimal identifiers for all entities
- **Change Minimization**: Minimize disruption when re-scheduling with published baselines
- **Rich CLI**: Beautiful terminal output with progress indicators and clear error messages
- **Multiple Export Formats**: JSON, CSV, and ICS calendar files
- **Fairness Tracking**: Automatic load balancing and fairness metrics
- **Simulation**: Test schedule changes before applying them
- **Database Viewer**: Interactive and quick SQL query tools included

## Installation

### With pipx (Recommended)

```bash
pipx install -e .
```

### With Poetry

```bash
poetry install
poetry run roster --help
```

### From Source

```bash
git clone <repo>
cd rostio
make install
make run
```

## Quick Start

### 1. Initialize a Workspace

```bash
# List available templates
roster template list

# Initialize a church volunteer workspace
roster init --dir ./church --template church

cd church
```

### 2. Validate Configuration

```bash
roster validate --dir .
```

### 3. Generate a Schedule

```bash
roster solve --dir . --from 2025-09-01 --to 2025-11-30
```

This creates:
- `out/solution.json` - Complete solution bundle
- `out/assignments.csv` - Human-readable assignments
- `out/calendar.ics` - Calendar file for import
- `out/metrics.json` - Solution metrics and health score

### 4. View Statistics

```bash
roster stats --solution out/solution.json
```

### 5. Export for Specific Person

```bash
roster export --solution out/solution.json --dir . \
  --scope person:alice \
  --ics-out alice_calendar.ics
```

## Templates

### Cricket League

8 teams, round-robin fixtures, ground availability, long weekend rules.

```bash
roster init --dir ./league --template cricket
cd league
roster solve --dir . --from 2025-09-01 --to 2025-10-31
```

### Church Volunteers

Role coverage (kitchen, reception, childcare, AV), cooldown periods, fairness constraints.

```bash
roster init --dir ./church --template church
cd church
roster solve --dir . --from 2025-09-01 --to 2025-11-30
```

### On-Call Rotations

L1/L2/L3 tier coverage, minimum rest gaps, historical rotation fairness.

```bash
roster init --dir ./oncall --template oncall
cd oncall
roster solve --dir . --from 2025-09-01 --to 2025-09-30
```

## Commands

### `init`

Initialize a new workspace from a template.

```bash
roster init --dir PATH --template NAME [--force]
```

### `validate`

Validate workspace files for schema and semantic correctness.

```bash
roster validate --dir PATH
```

### `solve`

Generate a schedule.

```bash
roster solve --dir PATH --from YYYY-MM-DD --to YYYY-MM-DD \
  [--mode strict|relaxed] \
  [--change-min/--no-change-min] \
  [--out PATH]
```

### `diff`

Compare two solutions.

```bash
roster diff --prev FILE --curr FILE [--out FILE]
```

### `publish`

Publish a solution snapshot for change minimization.

```bash
roster publish --solution FILE --tag STRING --dir PATH
```

### `simulate`

Simulate changes with a patch.

```bash
roster simulate --dir PATH --patch FILE --from DATE --to DATE
```

### `stats`

Display solution statistics and metrics.

```bash
roster stats --solution FILE
```

### `explain`

Explain why a person was/wasn't assigned.

```bash
roster explain --solution FILE --dir PATH [--event ID] [--person ID]
```

### `export`

Export solution to ICS/CSV for specific scope.

```bash
roster export --solution FILE --dir PATH \
  --scope org|person:ID|team:ID \
  [--ics-out FILE] [--csv-out FILE]
```

### `template`

Manage templates.

```bash
roster template list
roster template apply TEMPLATE --dir PATH [--force]
```

## Workspace Structure

```
workspace/
  org.yaml                   # Organization config
  people.yaml                # People definitions (hash-based IDs)
  teams.yaml                 # Team definitions (optional)
  resources.yaml             # Resources like grounds/rooms (optional)
  events.yaml                # Events to schedule
  holidays.yaml              # Holiday definitions (optional)
  availability.yaml          # Consolidated availability (vacations + exceptions)
  availability/              # Per-person availability rules (alternative)
    person_alice.yaml
  constraints/               # Constraint definitions
    require_role_coverage.yaml
    min_rest_gap_hours.yaml
  history/                   # Published snapshots
    published_baseline.json
  out/                       # Generated outputs
    solution.json
    assignments.csv
    calendar.ics
    metrics.json
  roster.db                  # SQLite database (when using DB backend)
```

## Constraint DSL

Constraints are defined in YAML with a simple DSL:

```yaml
key: min_rest_gap_hours
scope: person
applies_to: [shift]
severity: hard
params:
  hours: 12
then:
  enforce_min_gap_hours: 12
```

### Built-in Predicates

- `is_long_weekend` - Check if date is part of long weekend
- `is_day_of_week` - Check day of week
- `is_friday_or_monday` - Convenience predicate

### Built-in Actions

- `forbid_if` - Hard constraint to block scheduling
- `require_roles` - Require role coverage
- `enforce_min_gap_hours` - Minimum rest between assignments
- `enforce_cap` - Cap assignments per period
- `penalize_if` - Soft constraint with penalty

## Solver Architecture

The CLI uses a pluggable solver architecture:

- **Heuristic Solver** (default): Fast greedy algorithm for feasible solutions
- **OR-Tools Adapter** (stub): Ready for CP-SAT integration

```python
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver

solver = GreedyHeuristicSolver()
solver.build_model(context)
solution = solver.solve()
```

## Development

### Setup

```bash
make install
```

### Format Code

```bash
make fmt
```

### Lint

```bash
make lint
```

### Run Tests

```bash
make test
```

### Build Binary

```bash
./scripts/build-binary.sh
```

## Configuration Files

### org.yaml

```yaml
org_id: my_org
region: CA-ON
defaults:
  change_min_weight: 100
  fairness_weight: 50
  cooldown_days: 14
```

### people.yaml

```yaml
people:
  - id: alice
    name: Alice Johnson
    roles: [kitchen, reception]
    skills: []
```

### events.yaml

```yaml
events:
  - id: service_2025_09_07
    type: shift
    start: 2025-09-07T09:00:00
    end: 2025-09-07T12:00:00
    resource_id: main_hall
    required_roles:
      - {role: kitchen, count: 2}
      - {role: reception, count: 2}
```

## Metrics

Every solution includes comprehensive metrics:

- **Hard Violations**: Count of unsatisfied hard constraints
- **Soft Score**: Aggregated soft constraint penalties
- **Fairness**: Standard deviation of assignment counts
- **Health Score**: 0-100 score (100 = perfect, 0 = infeasible)
- **Solve Time**: Milliseconds to compute solution
- **Stability**: Change counts vs. published baseline

## Change Minimization

When re-scheduling, minimize disruption:

1. Generate and publish a baseline:
   ```bash
   roster solve --dir . --from 2025-09-01 --to 2025-09-30
   roster publish --solution out/solution.json --tag baseline --dir .
   ```

2. Make changes (update availability, add people, etc.)

3. Re-solve with change minimization:
   ```bash
   roster solve --dir . --from 2025-09-01 --to 2025-09-30 --change-min
   ```

The solver will prefer keeping published assignments and only change what's necessary.

## Simulation

Test the impact of changes before applying:

Create a patch file `patch.yaml`:
```yaml
update_availability:
  - person_id: alice
    vacations:
      - start: 2025-09-15
        end: 2025-09-22
```

Run simulation:
```bash
roster simulate --dir . --patch patch.yaml --from 2025-09-01 --to 2025-09-30
```

This shows how many assignments would change and which people would be affected.

## Performance

Target solve times (with heuristic solver):

- **Cricket** (8 teams, 10 weeks): < 10s
- **Church** (20 volunteers, 12 weeks): < 10s
- **On-call** (12 people, 4 weeks): < 10s

For larger instances, consider implementing the OR-Tools adapter.

## License

MIT License - see LICENSE file.

## Contributing

Contributions welcome! Please:

1. Run `make fmt` before committing
2. Ensure `make lint` passes
3. Add tests for new features
4. Update documentation

## Database Backend

The roster system now includes a SQLite database backend for persistent storage.

### Migrate YAML to Database

```bash
poetry run python -m roster_cli.db.migrate test_data/cricket_custom sqlite:///roster.db
```

### View Database

Quick summary:
```bash
poetry run python show_db.py
```

View specific table:
```bash
poetry run python show_db.py -t people -l 10
poetry run python show_db.py -t teams
```

Run custom SQL queries:
```bash
poetry run python show_db.py -q "SELECT * FROM people WHERE roles LIKE '%captain%'"
poetry run python show_db.py -q "SELECT t.name, COUNT(tm.person_id) as members FROM teams t LEFT JOIN team_members tm ON t.id = tm.team_id GROUP BY t.id"
```

Interactive viewer:
```bash
poetry run python view_db.py
```

### Database Schema

- **organizations** - League/church/company info
- **people** - Players/volunteers with hash-based IDs
- **teams** - Team definitions
- **team_members** - Team membership junction table
- **resources** - Venues/grounds/rooms
- **events** - Matches/shifts/meetings
- **event_teams** - Event-team links
- **availability** - Person availability rules
- **vacation_periods** - Multi-day unavailable periods
- **availability_exceptions** - Single-day unavailable dates
- **holidays** - Organization-wide holidays
- **constraints** - Scheduling constraints
- **solutions** - Generated schedules
- **assignments** - Person-to-event assignments

## Roadmap

- [x] SQLite database backend with SQLAlchemy ORM
- [x] Hash-based player IDs for security
- [x] Consolidated availability (vacations + exceptions)
- [x] Database migration tools
- [x] Interactive database viewer
- [ ] OR-Tools CP-SAT solver implementation
- [ ] Web UI for schedule visualization
- [ ] Email notifications for assignments
- [ ] Import from external calendars (Google, Outlook)
- [ ] Multi-timezone support
- [ ] More constraint templates (academic scheduling, shift work, etc.)
