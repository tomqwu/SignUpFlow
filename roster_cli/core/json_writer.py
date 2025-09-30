"""JSON output writer for solution bundles."""

from pathlib import Path

from roster_cli.core.loader import save_json
from roster_cli.core.models import SolutionBundle


def write_solution_json(solution: SolutionBundle, output_path: Path) -> None:
    """Write solution bundle to JSON."""
    save_json(output_path, solution.model_dump(mode="json"))


def write_metrics_json(solution: SolutionBundle, output_path: Path) -> None:
    """Write metrics to JSON."""
    save_json(output_path, solution.metrics.model_dump(mode="json"))
