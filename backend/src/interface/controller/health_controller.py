"""Controller for health endpoints."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from src.interface.presenter.health import HealthPresenter
from src.interface.viewmodel.health import (
    DependencyStatusViewModel,
    LivenessViewModel,
    ReadinessViewModel,
)


class HealthController:
    """Coordinate health checks."""

    def __init__(
        self,
        database_checker: Callable[[], Awaitable[None]],
        redis_checker: Callable[[], Awaitable[None]],
        presenter: HealthPresenter,
    ) -> None:
        self._database_checker = database_checker
        self._redis_checker = redis_checker
        self._presenter = presenter

    async def live(self) -> LivenessViewModel:
        """Return liveness information."""
        return self._presenter.present_live()

    async def ready(self) -> ReadinessViewModel:
        """Check readiness dependencies."""
        dependencies: dict[str, DependencyStatusViewModel] = {}
        for name, checker in {
            "database": self._database_checker,
            "redis": self._redis_checker,
        }.items():
            try:
                await checker()
                dependencies[name] = DependencyStatusViewModel(ok=True)
            except Exception as exc:
                dependencies[name] = DependencyStatusViewModel(ok=False, detail=str(exc))
        return self._presenter.present_ready(dependencies)
