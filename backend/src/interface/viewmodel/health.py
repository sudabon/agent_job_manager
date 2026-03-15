"""View models for health endpoints."""

from pydantic import BaseModel


class LivenessViewModel(BaseModel):
    """Liveness response."""

    status: str = "ok"


class DependencyStatusViewModel(BaseModel):
    """Status of an external dependency."""

    ok: bool
    detail: str | None = None


class ReadinessViewModel(BaseModel):
    """Readiness response."""

    status: str
    dependencies: dict[str, DependencyStatusViewModel]
