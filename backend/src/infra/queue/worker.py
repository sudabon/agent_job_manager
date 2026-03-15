"""arq worker configuration."""

from __future__ import annotations

from typing import Any

from src.app.dto.job import ExecuteJobInput
from src.app.usecase.execute_job import ExecuteJobUseCase
from src.domain.service.job_domain_service import JobDomainService
from src.infra.config.settings import Settings, get_settings
from src.infra.persistence.job_repository import SqlAlchemyJobRepository
from src.infra.persistence.session import create_engine, create_session_factory
from src.infra.queue.job_queue import redis_settings_from_url
from src.infra.runner.docker_runner import DockerRunner


async def startup(ctx: dict[str, Any]) -> None:
    """Create worker-scoped resources."""
    settings = get_settings()
    engine = create_engine(settings)
    ctx["settings"] = settings
    ctx["engine"] = engine
    ctx["session_factory"] = create_session_factory(engine)
    ctx["runner"] = DockerRunner(settings)


async def shutdown(ctx: dict[str, Any]) -> None:
    """Dispose worker resources."""
    await ctx["engine"].dispose()


async def execute_job(ctx: dict[str, Any], *, job_id: str) -> None:
    """Worker handler for executing jobs."""
    session_factory = ctx["session_factory"]
    runner = ctx["runner"]
    async with session_factory() as session:
        repository = SqlAlchemyJobRepository(session)
        use_case = ExecuteJobUseCase(repository, runner, JobDomainService())
        await use_case.execute(ExecuteJobInput(job_id=job_id))


class WorkerSettings:
    """arq worker settings."""

    settings: Settings = get_settings()
    functions = [execute_job]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = redis_settings_from_url(settings.redis_url)
    job_timeout = settings.max_timeout_sec + 10
