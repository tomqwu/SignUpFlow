"""Validate command."""

from pathlib import Path

import typer
from rich.console import Console

from roster_cli.core.schema_validators import ValidationError, validate_workspace

console = Console()


def validate_command(
    dir: Path = typer.Option(..., help="Workspace directory"),
) -> None:
    """Validate workspace files for schema and semantic correctness."""
    try:
        validate_workspace(dir)
        console.print("[green]✓ Validation passed[/green]")
    except ValidationError as e:
        console.print("[red]Validation errors:[/red]")
        for error in e.errors:
            console.print(f"  • {error}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
