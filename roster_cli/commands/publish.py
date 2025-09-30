"""Publish command."""

from pathlib import Path

import typer
from rich.console import Console

from roster_cli.core.loader import load_solution
from roster_cli.core.publish_state import publish_solution

console = Console()


def publish_command(
    solution: Path = typer.Option(..., help="Solution file to publish"),
    tag: str = typer.Option(..., help="Tag for this publish"),
    dir: Path = typer.Option(..., help="Workspace directory"),
) -> None:
    """Publish a solution snapshot for change minimization."""
    try:
        sol = load_solution(solution)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load solution: {e}")
        raise typer.Exit(1)

    output_path = publish_solution(sol, dir, tag)
    console.print(f"[green]✓[/green] Published solution to {output_path}")
    console.print(f"Tag: {tag}")
