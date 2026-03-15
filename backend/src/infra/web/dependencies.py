"""FastAPI dependency providers."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast

from fastapi import Depends, Header, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.common.errors import AuthenticationFailed
from src.app.usecase.get_job import GetJobUseCase
from src.app.usecase.get_job_logs import GetJobLogsUseCase
from src.app.usecase.list_jobs import ListJobsUseCase
from src.app.usecase.submit_python_job import SubmitPythonJobUseCase
from src.domain.entity.api_key import ApiKey
from src.domain.service.job_domain_service import JobDomainService
from src.infra.auth.api_key_hasher import hash_api_key
from src.infra.config.settings import Settings
from src.infra.persistence.api_key_repository import SqlAlchemyApiKeyRepository
from src.infra.persistence.job_repository import SqlAlchemyJobRepository
from src.infra.queue.job_queue import ArqJobQueue
from src.interface.controller.health_controller import HealthController
from src.interface.controller.job_controller import JobController
from src.interface.presender.health import HealthPresender
from src.interface.presender.job import JobPresender


def get_settings(request: Request) -> Settings:
    """Expose app settings."""
    return cast(Settings, request.app.state.settings)


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped DB session."""
    async with request.app.state.session_factory() as session:
        yield session


def get_job_repository(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyJobRepository:
    """Create the job repository implementation."""
    return SqlAlchemyJobRepository(session)


def get_api_key_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SqlAlchemyApiKeyRepository:
    """Create the API key repository implementation."""
    return SqlAlchemyApiKeyRepository(session)


def get_job_controller(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> JobController:
    """Create the job controller."""
    settings: Settings = request.app.state.settings
    job_repository = SqlAlchemyJobRepository(session)
    queue = ArqJobQueue(request.app.state.redis_pool, settings.worker_queue_name)
    presender = JobPresender()
    return JobController(
        SubmitPythonJobUseCase(
            job_repository,
            queue,
            JobDomainService(),
            default_timeout_sec=settings.default_timeout_sec,
            min_timeout_sec=settings.min_timeout_sec,
            max_timeout_sec=settings.max_timeout_sec,
            max_code_size_bytes=settings.max_code_size_bytes,
        ),
        GetJobUseCase(job_repository),
        ListJobsUseCase(job_repository),
        GetJobLogsUseCase(job_repository),
        presender,
    )


async def check_database(request: Request) -> None:
    """Run a database readiness check."""
    async with request.app.state.session_factory() as session:
        await session.execute(text("SELECT 1"))


async def check_redis(request: Request) -> None:
    """Run a Redis readiness check."""
    await request.app.state.redis_pool.ping()


def get_health_controller(request: Request) -> HealthController:
    """Create the health controller."""
    return HealthController(
        database_checker=lambda: check_database(request),
        redis_checker=lambda: check_redis(request),
        presender=HealthPresender(),
    )


async def get_current_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    repository: SqlAlchemyApiKeyRepository = Depends(get_api_key_repository),
) -> ApiKey:
    """Authenticate an API key from the request header."""
    if not x_api_key:
        raise AuthenticationFailed("X-API-Key header is required")

    api_key = await repository.get_by_hash(hash_api_key(x_api_key))
    if api_key is None or not api_key.is_active:
        raise AuthenticationFailed("API key authentication failed")
    return api_key
