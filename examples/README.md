# Rostio Examples

This directory contains example scripts demonstrating different use cases for the Rostio roster scheduling system.

## Available Examples

### Cricket League Scheduling

#### Basic Example
**File:** `cricket_basic_example.py`

Demonstrates generating a cricket league fixture schedule using the built-in cricket template.

```bash
poetry run python examples/cricket_basic_example.py
```

**Features:**
- 8 teams with 40 players
- Multiple grounds
- Team-based roster display with squad lists
- Holiday constraints
- Player statistics and fairness metrics

#### Custom Example
**File:** `cricket_custom_example.py`

Uses customizable YAML data for more control over the scheduling scenario.

```bash
poetry run python examples/cricket_custom_example.py
```

**Features:**
- Hash-based player IDs for security
- Individual player availability tracking
- Vacation periods and exception dates
- Data validation with detailed error reporting
- Customizable test data in `test_data/cricket_custom/`

**Customizing:** Edit the YAML files in `test_data/cricket_custom/` to modify teams, players, fixtures, and constraints.

### Church Volunteer Scheduling

**File:** `church_volunteer_example.py`

Generates a church volunteer roster for multiple services.

```bash
poetry run python examples/church_volunteer_example.py
```

**Features:**
- Multiple volunteer roles (kitchen, reception, childcare, av_tech)
- Role-based assignment
- Fairness distribution across volunteers
- Service calendar generation

### API Testing

**File:** `api_usage_example.py`

Comprehensive test suite demonstrating the Rostio API across all templates.

```bash
poetry run python examples/api_usage_example.py
```

**Tests:**
- Cricket template end-to-end
- Church template end-to-end
- On-call template end-to-end
- Validation, solving, and output generation

## Output Files

All examples generate output files in `/tmp/` directories:

- `solution.json` - Complete solution with all assignments and metrics
- `assignments.csv` or `fixtures.csv` - Spreadsheet-friendly format
- `calendar.ics` - iCalendar format for importing to calendar apps
- `metrics.json` - Detailed performance and quality metrics

## Database

The cricket example includes a pre-generated SQLite database:

**File:** `cricket_roster.db`

View the database contents using the tools in the `tools/` directory:

```bash
# Quick viewer
poetry run python tools/db_viewer.py examples/cricket_roster.db

# Interactive viewer
poetry run python tools/db_interactive.py examples/cricket_roster.db
```

## Next Steps

1. Run the examples to see how the system works
2. Examine the generated output files
3. Customize the YAML data in `test_data/cricket_custom/`
4. Use the database tools to explore the data model
5. Adapt the examples for your own use case

For more information, see the main [README.md](../README.md) and [API documentation](../docs/API.md).
