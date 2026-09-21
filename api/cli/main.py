"""
SignUpFlow CLI entry point.

Usage:
    signupflow init <workspace>          Create sample workspace with YAML files
    signupflow solve <workspace>         Run solver on a workspace directory
    signupflow solve <workspace> -o out  Save solution to output directory
"""

import json
import os
import re
import sys
from pathlib import Path

import click

from api.core.loader import (
    load_availability_files,
    load_constraint_files,
    load_events,
    load_holidays,
    load_org,
    load_people,
    load_teams,
    save_json,
)
from api.core.solver.adapter import SolveContext
from api.core.solver.heuristics import GreedyHeuristicSolver


@click.group()
@click.version_option(version="1.0.0", prog_name="signupflow")
def cli():
    """SignUpFlow — AI-powered volunteer scheduling from YAML files."""
    pass


@cli.command()
@click.argument("workspace", type=click.Path(exists=False))
def init(workspace: str):
    """Create a sample workspace with YAML configuration files."""
    ws = Path(workspace)
    if ws.exists() and any(ws.iterdir()):
        click.echo(f"Error: {workspace} already exists and is not empty.", err=True)
        sys.exit(1)

    ws.mkdir(parents=True, exist_ok=True)

    _write_sample_org(ws)
    _write_sample_people(ws)
    _write_sample_events(ws)

    click.echo(f"Created workspace at {ws}/")
    click.echo("  org.yaml      — organization config")
    click.echo("  people.yaml   — volunteers and their roles")
    click.echo("  events.yaml   — events to schedule")
    click.echo(f"\nRun: signupflow solve {workspace}")


@cli.command()
@click.argument("workspace", type=click.Path(exists=True, file_okay=False))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=None,
    help="Output directory for solution files (default: <workspace>/output/)",
)
@click.option(
    "--from-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="Start date (default: earliest event)",
)
@click.option(
    "--to-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="End date (default: latest event)",
)
@click.option(
    "--mode", type=click.Choice(["strict", "relaxed"]), default="relaxed", help="Solving mode"
)
@click.option("--json-output", is_flag=True, help="Output solution as JSON to stdout")
def solve(workspace: str, output: str, from_date, to_date, mode: str, json_output: bool):
    """Run the scheduler on a workspace directory."""
    ws = Path(workspace)

    # Load workspace files
    try:
        org = load_org(ws)
    except Exception as e:
        click.echo(f"Error loading org.yaml: {e}", err=True)
        sys.exit(1)

    try:
        people_file = load_people(ws)
    except Exception as e:
        click.echo(f"Error loading people.yaml: {e}", err=True)
        sys.exit(1)

    try:
        events_file = load_events(ws)
    except Exception as e:
        click.echo(f"Error loading events.yaml: {e}", err=True)
        sys.exit(1)

    teams_file = load_teams(ws)
    holidays_file = load_holidays(ws)
    availability = load_availability_files(ws)
    constraints = load_constraint_files(ws)

    people = people_file.people
    events = events_file.events
    teams = teams_file.teams if teams_file else []
    holidays = holidays_file.holidays if holidays_file else []

    if not events:
        click.echo("Error: No events found in events.yaml", err=True)
        sys.exit(1)

    if not people:
        click.echo("Error: No people found in people.yaml", err=True)
        sys.exit(1)

    # Determine date range
    if from_date:
        solve_from = from_date.date()
    else:
        solve_from = min(e.start.date() for e in events)

    if to_date:
        solve_to = to_date.date()
    else:
        solve_to = max(e.end.date() for e in events)

    if not json_output:
        click.echo(f"Workspace: {ws}")
        click.echo(f"People:    {len(people)}")
        click.echo(f"Events:    {len(events)}")
        click.echo(f"Range:     {solve_from} → {solve_to}")
        click.echo(f"Mode:      {mode}")
        click.echo()

    # Build solve context
    context = SolveContext(
        org=org,
        people=people,
        teams=teams,
        resources=[],
        events=events,
        constraints=constraints,
        availability=availability,
        holidays=holidays,
        from_date=solve_from,
        to_date=solve_to,
        mode=mode,
        change_min=False,
    )

    # Solve
    solver = GreedyHeuristicSolver()
    solver.build_model(context)
    solution = solver.solve()

    # Format output
    result = {
        "solve_ms": solution.metrics.solve_ms,
        "health_score": solution.metrics.health_score,
        "hard_violations": solution.metrics.hard_violations,
        "soft_score": solution.metrics.soft_score,
        "assignment_count": len(solution.assignments),
        "fairness_stdev": solution.metrics.fairness.stdev,
        "assignments": [
            {
                "event_id": a.event_id,
                "assignees": a.assignees,
                "assigned_roles": a.assigned_roles,
            }
            for a in solution.assignments
        ],
        "violations": [
            {"key": v.constraint_key, "message": v.message, "entities": v.entities}
            for v in solution.violations.hard + solution.violations.soft
        ],
    }

    if json_output:
        click.echo(json.dumps(result, indent=2, default=str))
        return

    # Human-readable output
    click.echo(f"Solved in {solution.metrics.solve_ms:.0f}ms")
    click.echo(f"Health score: {solution.metrics.health_score:.1f}/100")
    click.echo(f"Assignments:  {len(solution.assignments)}")
    click.echo(
        f"Violations:   {solution.metrics.hard_violations} hard, "
        f"{len(solution.violations.soft)} soft"
    )
    click.echo(f"Fairness:     stdev={solution.metrics.fairness.stdev:.2f}")
    click.echo()

    # Print assignments grouped by event
    person_map = {p.id: p.name for p in people}
    for assignment in solution.assignments:
        names = [person_map.get(pid, pid) for pid in assignment.assignees]
        click.echo(f"  {assignment.event_id}: {', '.join(names)}")

    if solution.violations.hard:
        click.echo()
        click.echo("Hard violations:")
        for v in solution.violations.hard:
            click.echo(f"  - {v.message}")

    # Save output
    out_dir = Path(output) if output else ws / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_json(out_dir / "solution.json", result)
    if not json_output:
        click.echo(f"\nSolution saved to {out_dir}/solution.json")


def _write_sample_org(ws: Path):
    import yaml

    data = {
        "org_id": "my-org",
        "region": "US",
        "defaults": {
            "change_min_weight": 100,
            "fairness_weight": 50,
            "cooldown_days": 14,
        },
    }
    with open(ws / "org.yaml", "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def _write_sample_people(ws: Path):
    import yaml

    data = {
        "people": [
            {"id": "sarah", "name": "Sarah Chen", "roles": ["musician", "teacher"], "skills": []},
            {"id": "david", "name": "David Kim", "roles": ["musician", "sound_tech"], "skills": []},
            {"id": "maria", "name": "Maria Lopez", "roles": ["teacher", "volunteer"], "skills": []},
            {"id": "james", "name": "James Brown", "roles": ["usher", "volunteer"], "skills": []},
            {
                "id": "emily",
                "name": "Emily Davis",
                "roles": ["musician", "youth_leader"],
                "skills": [],
            },
        ],
    }
    with open(ws / "people.yaml", "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def _write_sample_events(ws: Path):
    from datetime import datetime, timedelta

    import yaml

    base = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=7)
    data = {
        "events": [
            {
                "id": "sunday-worship-1",
                "type": "Sunday Worship",
                "start": (base).isoformat(),
                "end": (base + timedelta(hours=2)).isoformat(),
                "required_roles": [
                    {"role": "musician", "count": 2},
                    {"role": "sound_tech", "count": 1},
                    {"role": "usher", "count": 1},
                ],
            },
            {
                "id": "sunday-worship-2",
                "type": "Sunday Worship",
                "start": (base + timedelta(days=7)).isoformat(),
                "end": (base + timedelta(days=7, hours=2)).isoformat(),
                "required_roles": [
                    {"role": "musician", "count": 2},
                    {"role": "sound_tech", "count": 1},
                    {"role": "usher", "count": 1},
                ],
            },
        ],
    }
    with open(ws / "events.yaml", "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


#: Ambient variables that change how the app starts. Anything set here comes
#: from outside the repository, so a fresh clone cannot make it go away and a
#: contributor has no way to see it without being told to look.
_AMBIENT_VARS = (
    "DATABASE_URL",
    "ENVIRONMENT",
    "SECRET_KEY",
    "REDIS_URL",
    "RATE_LIMIT_STORAGE",
    "RATE_LIMIT_REDIS_URL",
    "APP_URL",
    "FRONTEND_URL",
    "TESTING",
    "TENANCY_GUARD",
    "RELEASE_SHA",
    "SIGNUPFLOW_LOAD_DOTENV",
    "EMAIL_ENABLED",
    "SMS_ENABLED",
    "BILLING_ENABLED",
)

_SECRET_PARTS = ("SECRET", "TOKEN", "PASSWORD", "KEY")


def _redact(name: str, value: str) -> str:
    """Never print a credential, and never print a password inside a URL."""
    if any(part in name for part in _SECRET_PARTS):
        return f"<set, {len(value)} chars>"
    return re.sub(r"://([^:/@]+):[^@]*@", r"://\1:***@", value)


def _dotenv_values(path: Path) -> dict[str, str]:
    """Parse .env well enough to report it, tolerating export and quotes."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        key, sep, value = line.partition("=")
        if not sep:
            continue
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


@cli.command()
def doctor() -> None:
    """Report the environment this machine will actually start the app with.

    A fresh clone cannot reset an exported variable, and python-dotenv will not
    override one, so two people on the same commit can get different behaviour
    with nothing in the repository to explain it. This prints the effective
    value of every input that matters, says where each came from, and exits
    non-zero when one of them will stop the app from starting.
    """
    problems: list[str] = []
    notes: list[str] = []

    click.echo("SignUpFlow environment report")
    click.echo("=" * 60)

    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    supported = (3, 11) <= (sys.version_info.major, sys.version_info.minor) <= (3, 13)
    click.echo(f"\nPython {version} ({sys.executable})")
    if not supported:
        problems.append(f"Python {version} is outside the supported 3.11 to 3.13 range.")

    env_path = Path(".env")
    file_values = _dotenv_values(env_path)
    click.echo(
        f".env: {'present' if env_path.exists() else 'absent (fine; SQLite is the default)'}"
    )

    click.echo("\nEffective configuration")
    click.echo("-" * 60)
    for name in _AMBIENT_VARS:
        shell_value = os.environ.get(name)
        if shell_value is not None:
            source, value = "shell", shell_value
        elif name in file_values:
            source, value = ".env", file_values[name]
        else:
            continue
        click.echo(f"  {name} = {_redact(name, value)}   [from {source}]")
        if name == "DATABASE_URL":
            problems.extend(_database_url_problems(value, source))

    if not any(os.environ.get(n) is not None or n in file_values for n in _AMBIENT_VARS):
        click.echo("  (nothing set; every default applies)")

    if os.environ.get("ENVIRONMENT", file_values.get("ENVIRONMENT", "")) == "production":
        notes.append(
            "ENVIRONMENT=production makes startup fail-closed. It requires an explicit "
            "SECRET_KEY and rejects a SQLite database. Unset it for local development."
        )

    click.echo("\nVerdict")
    click.echo("-" * 60)
    for note in notes:
        click.echo(f"  note: {note}")
    if problems:
        for problem in problems:
            click.echo(f"  problem: {problem}")
        click.echo("\nThe app will not start until the problems above are resolved.")
        sys.exit(1)
    click.echo("  No blocking problems found.")
    if not notes:
        click.echo("  'make setup' then 'make run' should work on this machine.")


def _database_url_problems(value: str, source: str) -> list[str]:
    """Explain a DATABASE_URL that cannot work from the host, if that is the case."""
    host = re.sub(r"^[a-z+]+://(?:[^@/]*@)?", "", value).split("/")[0].split(":")[0]
    if host not in {"db", "redis", "postgres"}:
        return []
    fix = (
        "run 'unset DATABASE_URL' and remove the export from your shell profile"
        if source == "shell"
        else "set DATABASE_URL=sqlite:///./roster.db in .env, or delete .env"
    )
    return [
        f"DATABASE_URL host '{host}' is a docker-compose service name and resolves only "
        f"inside that network. It came from your {source}, so {fix}. "
        "To use a real PostgreSQL server from the host, point at its published port."
    ]


def main():
    cli()


if __name__ == "__main__":
    main()
