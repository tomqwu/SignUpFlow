# Roster API Documentation

This document describes how to use the Roster scheduling engine programmatically via its Python API.

## Installation

```bash
pip install -e .
# or
poetry install
```

## Quick Start

```python
from datetime import date
from pathlib import Path
from roster_cli.core.loader import load_org, load_people, load_events, load_constraint_files
from roster_cli.core.solver.adapter import SolveContext
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver

# Load workspace
workspace = Path("./my_workspace")
org = load_org(workspace)
people_file = load_people(workspace)
events_file = load_events(workspace)
constraints = load_constraint_files(workspace)

# Create solve context
context = SolveContext(
    org=org,
    people=people_file.people,
    teams=[],
    resources=[],
    events=events_file.events,
    constraints=constraints,
    availability=[],
    holidays=[],
    from_date=date(2025, 9, 1),
    to_date=date(2025, 9, 30),
    mode="strict",
    change_min=False,
)

# Solve
solver = GreedyHeuristicSolver()
solver.build_model(context)
solution = solver.solve()

# Access results
print(f"Assignments: {len(solution.assignments)}")
print(f"Health score: {solution.metrics.health_score}/100")
```

## Core Modules

### 1. Data Loading (`roster_cli.core.loader`)

Load workspace data from YAML/JSON files:

```python
from roster_cli.core.loader import (
    load_org,                    # Load org.yaml
    load_people,                 # Load people.yaml
    load_teams,                  # Load teams.yaml (optional)
    load_resources,              # Load resources.yaml (optional)
    load_events,                 # Load events.yaml
    load_holidays,               # Load holidays.yaml (optional)
    load_availability_files,     # Load availability/*.yaml
    load_constraint_files,       # Load constraints/*.yaml
    load_solution,               # Load solution.json
    save_json,                   # Save JSON data
    save_yaml,                   # Save YAML data
)

# Example
workspace = Path("./workspace")
org = load_org(workspace)
people = load_people(workspace).people
events = load_events(workspace).events
```

### 2. Validation (`roster_cli.core.schema_validators`)

Validate workspace for schema and semantic correctness:

```python
from roster_cli.core.schema_validators import validate_workspace, ValidationError

try:
    validate_workspace(workspace_path, from_date, to_date)
    print("✓ Valid")
except ValidationError as e:
    for error in e.errors:
        print(f"✗ {error}")
```

### 3. Solver (`roster_cli.core.solver`)

#### SolverAdapter Interface

```python
from roster_cli.core.solver.adapter import SolverAdapter, SolveContext

class CustomSolver(SolverAdapter):
    def build_model(self, context: SolveContext) -> None:
        """Build internal model."""
        pass

    def solve(self, timeout_s: int | None = None) -> SolutionBundle:
        """Solve and return solution."""
        pass

    def set_objective(self, weights: dict[str, int]) -> None:
        """Set objective weights."""
        pass

    def enable_change_minimization(self, enabled: bool, weight: int) -> None:
        """Enable change-min."""
        pass

    def incremental_update(self, changes: Patch) -> None:
        """Apply incremental updates."""
        pass
```

#### GreedyHeuristicSolver

Built-in heuristic solver:

```python
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver

solver = GreedyHeuristicSolver()
solver.build_model(context)

# Optional: set custom weights
solver.set_objective({"fairness": 100, "soft": 50})

# Optional: enable change minimization
solver.enable_change_minimization(True, weight_move_published=100)

# Solve
solution = solver.solve(timeout_s=30)
```

### 4. Output Writers

#### JSON

```python
from roster_cli.core.json_writer import write_solution_json, write_metrics_json

write_solution_json(solution, Path("out/solution.json"))
write_metrics_json(solution, Path("out/metrics.json"))
```

#### CSV

```python
from roster_cli.core.csv_writer import write_assignments_csv

write_assignments_csv(
    solution,
    events_list,
    people_list,
    Path("out/assignments.csv")
)
```

#### ICS Calendar

```python
from roster_cli.core.ics_writer import write_calendar_ics

# Organization-wide calendar
write_calendar_ics(solution, events, people, Path("out/calendar.ics"))

# Person-specific calendar
write_calendar_ics(
    solution, events, people,
    Path("out/alice.ics"),
    scope="person",
    scope_id="alice"
)

# Team-specific calendar
write_calendar_ics(
    solution, events, people,
    Path("out/team_a.ics"),
    scope="team",
    scope_id="team_a"
)
```

### 5. Diffing (`roster_cli.core.diffing`)

Compare two solutions:

```python
from roster_cli.core.diffing import diff_solutions

diff = diff_solutions(previous_solution, current_solution)

print(f"Added: {len(diff.added)}")
print(f"Removed: {len(diff.removed)}")
print(f"Total changes: {diff.total_changes}")
print(f"Affected persons: {len(diff.affected_persons)}")
```

### 6. Publishing (`roster_cli.core.publish_state`)

Manage published solution snapshots:

```python
from roster_cli.core.publish_state import (
    publish_solution,
    load_published_solution,
    get_latest_published,
)

# Publish a solution
path = publish_solution(solution, workspace, tag="baseline")

# Load published solution
published = load_published_solution(workspace, "baseline")

# Get latest
latest = get_latest_published(workspace)
```

## Data Models

All data models use Pydantic for validation:

### Person

```python
from roster_cli.core.models import Person

person = Person(
    id="alice",
    name="Alice Johnson",
    roles=["kitchen", "reception"],
    skills=["cooking", "hosting"],
    external_ids={"slack": "U123456"}
)
```

### Event

```python
from datetime import datetime
from roster_cli.core.models import Event, RequiredRole

event = Event(
    id="service_001",
    type="shift",
    start=datetime(2025, 9, 1, 9, 0),
    end=datetime(2025, 9, 1, 12, 0),
    resource_id="main_hall",
    required_roles=[
        RequiredRole(role="kitchen", count=2),
        RequiredRole(role="reception", count=1),
    ],
    team_ids=[],
    assignees=[],  # Filled by solver
)
```

### SolutionBundle

```python
from roster_cli.core.models import SolutionBundle

# Access solution data
solution: SolutionBundle = solver.solve()

# Metadata
print(solution.meta.generated_at)
print(solution.meta.solver.name)

# Assignments
for assignment in solution.assignments:
    print(f"Event: {assignment.event_id}")
    print(f"Assignees: {assignment.assignees}")

# Metrics
print(f"Hard violations: {solution.metrics.hard_violations}")
print(f"Soft score: {solution.metrics.soft_score}")
print(f"Health score: {solution.metrics.health_score}")

# Fairness
fairness = solution.metrics.fairness
print(f"Stdev: {fairness.stdev}")
for person_id, count in fairness.per_person_counts.items():
    print(f"  {person_id}: {count} assignments")

# Violations
for violation in solution.violations.hard:
    print(f"Hard: {violation.constraint_key} - {violation.message}")

for violation in solution.violations.soft:
    print(f"Soft: {violation.constraint_key} - {violation.message}")
```

## Advanced Usage

### Custom Constraints

Define constraints in YAML:

```yaml
# constraints/my_constraint.yaml
key: custom_min_gap
scope: person
applies_to: [shift, oncall_shift]
severity: hard
params:
  min_hours: 24
then:
  enforce_min_gap_hours: 24
```

### Simulation with Patches

```python
from roster_cli.core.models import Patch, VacationPeriod
from datetime import date

# Create patch
patch = Patch(
    update_availability=[
        Availability(
            person_id="alice",
            vacations=[
                VacationPeriod(
                    start=date(2025, 9, 15),
                    end=date(2025, 9, 22)
                )
            ]
        )
    ]
)

# Apply patch programmatically
# (Update context and re-solve)
```

### Change Minimization

```python
# Generate baseline
baseline_solution = solver.solve()
publish_solution(baseline_solution, workspace, "baseline")

# Make changes to workspace
# ...

# Re-solve with change minimization
new_context = SolveContext(
    # ... same params ...
    change_min=True,
    published_solution=baseline_solution
)

new_solver = GreedyHeuristicSolver()
new_solver.build_model(new_context)
new_solver.enable_change_minimization(True, weight_move_published=100)
new_solution = new_solver.solve()

# Compare
diff = diff_solutions(baseline_solution, new_solution)
print(f"Moved {diff.total_changes} assignments")
```

## Complete Example

See `examples/api_example.py` for a full working example:

```bash
python examples/api_example.py
```

## Testing

Run the API test suite:

```bash
python test_api.py
```

This tests all three templates (cricket, church, oncall) end-to-end.

## Error Handling

```python
from roster_cli.core.schema_validators import ValidationError

try:
    validate_workspace(workspace)
    solution = solver.solve()

    if solution.metrics.hard_violations > 0:
        print("⚠️ Solution has hard constraint violations")
        for v in solution.violations.hard:
            print(f"  - {v.message}")

except ValidationError as e:
    print("Validation failed:")
    for error in e.errors:
        print(f"  - {error}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance

Expected solve times for heuristic solver:

- **Small** (10 people, 10 events): < 10ms
- **Medium** (50 people, 50 events): < 100ms
- **Large** (100 people, 100 events): < 1s

For larger instances, implement the OR-Tools adapter (see `roster_cli/core/solver/or_tools_adapter.py`).

## Next Steps

1. Review the data models in `roster_cli/core/models.py`
2. Explore template workspaces in `roster_cli/templates/`
3. Run `test_api.py` to see end-to-end examples
4. Implement custom constraints or solvers

## Support

For issues or questions, see the README.md or open an issue on GitHub.
