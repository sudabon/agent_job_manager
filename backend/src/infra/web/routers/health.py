"""Health routes."""

from fastapi import APIRouter, Depends, Response, status

from src.infra.web.dependencies import get_health_controller
from src.interface.controller.health_controller import HealthController
from src.interface.viewmodel.health import LivenessViewModel, ReadinessViewModel


def create_health_router() -> APIRouter:
    """Build the health router."""
    router = APIRouter(prefix="/health", tags=["health"])

    @router.get("/live", response_model=LivenessViewModel)
    async def live(
        controller: HealthController = Depends(get_health_controller),
    ) -> LivenessViewModel:
        return await controller.live()

    @router.get("/ready", response_model=ReadinessViewModel)
    async def ready(
        response: Response,
        controller: HealthController = Depends(get_health_controller),
    ) -> ReadinessViewModel:
        payload = await controller.ready()
        if payload.status != "ok":
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return payload

    return router
