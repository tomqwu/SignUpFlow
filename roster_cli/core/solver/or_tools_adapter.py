"""OR-Tools solver adapter (stub for future implementation)."""

from roster_cli.core.models import Patch, SolutionBundle
from roster_cli.core.solver.adapter import SolveContext, SolverAdapter


class ORToolsSolver(SolverAdapter):
    """OR-Tools CP-SAT solver adapter."""

    def build_model(self, context: SolveContext) -> None:
        """Build internal model from context."""
        # TODO: Implement OR-Tools model construction
        # - Create CP-SAT model
        # - Define decision variables for assignments
        # - Add hard constraints as model constraints
        # - Build objective function from soft constraints and fairness
        raise NotImplementedError("OR-Tools adapter not yet implemented")

    def solve(self, timeout_s: int | None = None) -> SolutionBundle:
        """Solve and return solution bundle."""
        # TODO: Implement OR-Tools solving
        # - Set solver parameters (timeout, threads, etc.)
        # - Run solver
        # - Extract solution from model
        # - Build SolutionBundle with assignments and metrics
        raise NotImplementedError("OR-Tools adapter not yet implemented")

    def set_objective(self, weights: dict[str, int]) -> None:
        """Set objective function weights."""
        # TODO: Update objective function with custom weights
        raise NotImplementedError("OR-Tools adapter not yet implemented")

    def enable_change_minimization(self, enabled: bool, weight_move_published: int) -> None:
        """Enable/disable change minimization."""
        # TODO: Add penalties for changing published assignments
        # - Load published solution
        # - Add soft constraints penalizing deviations
        raise NotImplementedError("OR-Tools adapter not yet implemented")

    def incremental_update(self, changes: Patch) -> None:
        """Apply incremental changes to model."""
        # TODO: Implement incremental model updates
        # - Add/remove decision variables
        # - Update constraints
        # - Avoid full model rebuild
        raise NotImplementedError("OR-Tools adapter not yet implemented")
