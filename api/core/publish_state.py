"""Publish state and lock handling."""

from pathlib import Path

from api.core.loader import load_json, save_json
from api.core.models import SolutionBundle


def publish_solution(solution: SolutionBundle, workspace: Path, tag: str) -> Path:
    """Publish a solution snapshot with tag."""
    history_dir = workspace / "history"
    history_dir.mkdir(exist_ok=True)

    output_path = history_dir / f"published_{tag}.json"
    save_json(output_path, solution.model_dump(mode="json"))

    return output_path


def load_published_solution(workspace: Path, tag: str) -> SolutionBundle | None:
    """Load a published solution by tag."""
    path = workspace / "history" / f"published_{tag}.json"
    if not path.exists():
        return None

    data = load_json(path)
    return SolutionBundle(**data)


def get_latest_published(workspace: Path) -> SolutionBundle | None:
    """Get most recent published solution."""
    history_dir = workspace / "history"
    if not history_dir.exists():
        return None

    published_files = sorted(history_dir.glob("published_*.json"), key=lambda p: p.stat().st_mtime)
    if not published_files:
        return None

    data = load_json(published_files[-1])
    return SolutionBundle(**data)
