# Roster API Quick Start

## 1. Basic Solve (5 lines)

```python
from datetime import date
from pathlib import Path
from roster_cli.core.loader import *
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver
from roster_cli.core.solver.adapter import SolveContext

workspace = Path("./my_workspace")

# Load
org = load_org(workspace)
people = load_people(workspace).people
events = load_events(workspace).events
constraints = load_constraint_files(workspace)

# Solve
context = SolveContext(org=org, people=people, teams=[], resources=[],
                       events=events, constraints=constraints, availability=[],
                       holidays=[], from_date=date(2025,9,1), to_date=date(2025,9,30),
                       mode="strict", change_min=False)
solver = GreedyHeuristicSolver()
solver.build_model(context)
solution = solver.solve()

# Results
print(f"Health: {solution.metrics.health_score}/100")
print(f"Assignments: {len(solution.assignments)}")
```

## 2. Save Outputs

```python
from roster_cli.core.json_writer import write_solution_json
from roster_cli.core.csv_writer import write_assignments_csv
from roster_cli.core.ics_writer import write_calendar_ics

out = workspace / "out"
out.mkdir(exist_ok=True)

write_solution_json(solution, out / "solution.json")
write_assignments_csv(solution, events, people, out / "assignments.csv")
write_calendar_ics(solution, events, people, out / "calendar.ics")
```

## 3. Validate Before Solving

```python
from roster_cli.core.schema_validators import validate_workspace, ValidationError

try:
    validate_workspace(workspace)
except ValidationError as e:
    for error in e.errors:
        print(error)
    exit(1)
```

## 4. Export Person Calendar

```python
write_calendar_ics(
    solution, events, people,
    Path("alice_calendar.ics"),
    scope="person",
    scope_id="alice"
)
```

## 5. Compare Solutions

```python
from roster_cli.core.diffing import diff_solutions

diff = diff_solutions(old_solution, new_solution)
print(f"Changes: {diff.total_changes}")
print(f"Affected: {len(diff.affected_persons)} people")
```

## 6. Access Assignment Data

```python
for assignment in solution.assignments:
    event = next(e for e in events if e.id == assignment.event_id)
    people_names = [next(p.name for p in people if p.id == pid)
                    for pid in assignment.assignees]
    print(f"{event.start.date()}: {', '.join(people_names)}")
```

## 7. Check Violations

```python
if solution.metrics.hard_violations > 0:
    print("⚠️  Hard constraint violations:")
    for v in solution.violations.hard:
        print(f"  {v.constraint_key}: {v.message}")
```

## 8. Fairness Analysis

```python
counts = solution.metrics.fairness.per_person_counts
sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

for person_id, count in sorted_counts:
    person = next(p for p in people if p.id == person_id)
    print(f"{person.name}: {count} shifts")
```

## Complete Minimal Example

```python
#!/usr/bin/env python3
from datetime import date
from pathlib import Path
from roster_cli.core.loader import *
from roster_cli.core.solver.heuristics import GreedyHeuristicSolver
from roster_cli.core.solver.adapter import SolveContext
from roster_cli.core.json_writer import write_solution_json

workspace = Path("./workspace")

# Load
org = load_org(workspace)
people = load_people(workspace).people
events = load_events(workspace).events
constraints = load_constraint_files(workspace)

# Solve
ctx = SolveContext(org=org, people=people, teams=[], resources=[],
                   events=events, constraints=constraints, availability=[],
                   holidays=[], from_date=date(2025,9,1), to_date=date(2025,9,30),
                   mode="strict", change_min=False)

solver = GreedyHeuristicSolver()
solver.build_model(ctx)
solution = solver.solve()

# Save
write_solution_json(solution, workspace / "solution.json")

print(f"✓ Health: {solution.metrics.health_score:.0f}/100")
print(f"✓ Created {len(solution.assignments)} assignments")
```

## Running Examples

```bash
# Run complete API test
python test_api.py

# Run usage example
python examples/api_example.py
```

## Key Objects

- **SolveContext**: Input configuration for solver
- **SolutionBundle**: Complete solution with assignments, metrics, violations
- **Assignment**: Event → People mapping
- **Metrics**: Health score, fairness, violations, solve time
- **Person/Event/Team/Resource**: Entity models

## Next Steps

1. Read full API docs: `API.md`
2. Explore templates: `roster_cli/templates/`
3. Review test suite: `test_api.py`
