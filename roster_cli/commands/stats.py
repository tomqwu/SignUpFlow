"""Stats command."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from roster_cli.core.loader import load_solution

console = Console()


def stats_command(
    solution: Path = typer.Option(..., help="Solution file"),
) -> None:
    """Display statistics and metrics for a solution."""
    try:
        sol = load_solution(solution)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load solution: {e}")
        raise typer.Exit(1)

    console.print("\n[bold]Solution Statistics[/bold]")

    # Summary table
    table = Table(title="Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Generated at", sol.meta.generated_at.isoformat())
    table.add_row("Date range", f"{sol.meta.range_start} to {sol.meta.range_end}")
    table.add_row("Mode", sol.meta.mode)
    table.add_row("Change min", "Yes" if sol.meta.change_min else "No")
    table.add_row("Solver", f"{sol.meta.solver.name} ({sol.meta.solver.strategy})")

    console.print(table)

    # Metrics table
    metrics_table = Table(title="Metrics")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="magenta")

    metrics_table.add_row("Solve time", f"{sol.metrics.solve_ms:.0f} ms")
    metrics_table.add_row("Hard violations", str(sol.metrics.hard_violations))
    metrics_table.add_row("Soft score", f"{sol.metrics.soft_score:.2f}")
    metrics_table.add_row("Fairness (stdev)", f"{sol.metrics.fairness.stdev:.2f}")
    metrics_table.add_row("Health score", f"{sol.metrics.health_score:.1f}/100")

    console.print(metrics_table)

    # Fairness breakdown
    if sol.metrics.fairness.per_person_counts:
        console.print("\n[bold]Fairness Breakdown[/bold]")
        counts = sol.metrics.fairness.per_person_counts
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

        fairness_table = Table()
        fairness_table.add_column("Person", style="cyan")
        fairness_table.add_column("Assignments", style="magenta")

        for person_id, count in sorted_counts[:10]:
            fairness_table.add_row(person_id, str(count))

        if len(sorted_counts) > 10:
            fairness_table.add_row("...", "...")

        console.print(fairness_table)

    # Violations
    if sol.violations.hard:
        console.print("\n[bold red]Hard Violations[/bold red]")
        for v in sol.violations.hard[:10]:
            console.print(f"  • [{v.constraint_key}] {v.message}")
        if len(sol.violations.hard) > 10:
            console.print(f"  ... and {len(sol.violations.hard) - 10} more")

    if sol.violations.soft:
        console.print("\n[bold yellow]Soft Violations (sample)[/bold yellow]")
        for v in sol.violations.soft[:5]:
            console.print(f"  • [{v.constraint_key}] {v.message}")
