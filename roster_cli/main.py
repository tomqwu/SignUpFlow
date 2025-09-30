"""Main CLI entry point using Typer."""

import typer
from rich.console import Console

from roster_cli.commands import (
    diff,
    explain,
    export,
    init,
    publish,
    simulate,
    solve,
    stats,
    template,
    validate,
)

app = typer.Typer(
    name="roster",
    help="Local file-driven constraint rostering engine",
    add_completion=False,
)
console = Console()

# Register commands
app.command(name="init")(init.init_command)
app.command(name="validate")(validate.validate_command)
app.command(name="solve")(solve.solve_command)
app.command(name="diff")(diff.diff_command)
app.command(name="publish")(publish.publish_command)
app.command(name="simulate")(simulate.simulate_command)
app.command(name="stats")(stats.stats_command)
app.command(name="explain")(explain.explain_command)
app.command(name="export")(export.export_command)

# Add template subcommand
template_app = typer.Typer(name="template", help="Manage templates")
template_app.command(name="list")(template.list_templates)
template_app.command(name="apply")(template.apply_template)
app.add_typer(template_app, name="template")


if __name__ == "__main__":
    app()
