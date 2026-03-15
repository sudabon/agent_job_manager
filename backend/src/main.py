"""FastAPI application bootstrap."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from src.infra.config.settings import Settings, get_settings
from src.infra.logging.config import configure_logging
from src.infra.persistence.session import create_engine, create_session_factory
from src.infra.queue.job_queue import create_redis_pool_from_settings
from src.infra.web.middleware.error_handling import ErrorHandlingMiddleware
from src.infra.web.middleware.request_id import RequestIdMiddleware
from src.infra.web.routers.health import create_health_router
from src.infra.web.routers.jobs import create_jobs_router


def create_app(
    settings: Settings | None = None,
    *,
    engine: AsyncEngine | None = None,
    redis_pool: object | None = None,
) -> FastAPI:
    """Create the FastAPI application."""
    app_settings = settings or get_settings()
    configure_logging(app_settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = app_settings
        app.state.engine = engine or create_engine(app_settings)
        app.state.session_factory = create_session_factory(app.state.engine)
        app.state.redis_pool = redis_pool or await create_redis_pool_from_settings(app_settings)
        try:
            yield
        finally:
            close = getattr(app.state.redis_pool, "aclose", None)
            if callable(close):
                await close()
            await app.state.engine.dispose()

    app = FastAPI(title=app_settings.app_name, lifespan=lifespan)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestIdMiddleware, header_name=app_settings.request_id_header_name)
    app.include_router(create_jobs_router())
    app.include_router(create_health_router())
    return app


app = create_app()
