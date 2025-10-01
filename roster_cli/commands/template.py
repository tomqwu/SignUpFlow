"""Template command."""

import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

TEMPLATES = {
    "cricket": "Cricket league schedule with round-robin fixtures",
    "church": "Church volunteer roster with role coverage",
    "oncall": "On-call rotations with L1/L2/L3 tiers",
}


def list_templates() -> None:
    """List available templates."""
    console.print("\n[bold]Available Templates[/bold]\n")

    table = Table()
    table.add_column("Template", style="cyan")
    table.add_column("Description", style="white")

    for name, description in TEMPLATES.items():
        table.add_row(name, description)

    console.print(table)


def apply_template(
    template: str = typer.Argument(..., help="Template name"),
    dir: Path = typer.Option(..., help="Target directory"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
) -> None:
    """Apply template to directory."""
    if template not in TEMPLATES:
        console.print(f"[red]Error:[/red] Unknown template '{template}'")
        console.print(f"Available templates: {', '.join(TEMPLATES.keys())}")
        raise typer.Exit(1)

    template_source = Path(__file__).parent.parent / "templates" / template
    if not template_source.exists():
        console.print(f"[red]Error:[/red] Template source not found")
        raise typer.Exit(1)

    if dir.exists() and not force:
        if any(dir.iterdir()):
            console.print(
                f"[red]Error:[/red] Directory {dir} exists and is not empty. Use --force to overwrite."
            )
            raise typer.Exit(1)

    dir.mkdir(parents=True, exist_ok=True)

    for item in template_source.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(template_source)
            dest = dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)

    console.print(f"[green]✓[/green] Applied template '{template}' to {dir}")
