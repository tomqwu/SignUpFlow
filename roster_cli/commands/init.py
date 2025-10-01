"""Init command to scaffold workspace."""

import shutil
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def init_command(
    dir: Path = typer.Option(..., help="Workspace directory"),
    template: str = typer.Option(..., help="Template name (cricket|church|oncall)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
) -> None:
    """Initialize a new workspace from template."""
    if dir.exists() and not force:
        if any(dir.iterdir()):
            console.print(f"[red]Error:[/red] Directory {dir} exists and is not empty. Use --force to overwrite.")
            raise typer.Exit(1)

    # Get template source
    template_source = Path(__file__).parent.parent / "templates" / template
    if not template_source.exists():
        console.print(f"[red]Error:[/red] Template '{template}' not found")
        raise typer.Exit(1)

    # Copy template
    dir.mkdir(parents=True, exist_ok=True)

    for item in template_source.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(template_source)
            dest = dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)

    console.print(f"[green]✓[/green] Initialized workspace at {dir} with template '{template}'")
    console.print("\nNext steps:")
    console.print(f"  cd {dir}")
    console.print("  roster validate --dir .")
    console.print("  roster solve --dir . --from 2025-09-01 --to 2025-11-30")
