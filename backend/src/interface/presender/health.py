"""Present health controller responses."""

from src.interface.viewmodel.health import (
    DependencyStatusViewModel,
    LivenessViewModel,
    ReadinessViewModel,
)


class HealthPresender:
    """Convert health data into HTTP view models."""

    def present_live(self) -> LivenessViewModel:
        """Render liveness."""
        return LivenessViewModel()

    def present_ready(
        self,
        dependencies: dict[str, DependencyStatusViewModel],
    ) -> ReadinessViewModel:
        """Render readiness."""
        status = "ok" if all(item.ok for item in dependencies.values()) else "unavailable"
        return ReadinessViewModel(status=status, dependencies=dependencies)
