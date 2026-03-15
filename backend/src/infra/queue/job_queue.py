"""Redis queue implementation."""

from __future__ import annotations

from urllib.parse import urlparse

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from src.app.port.job_queue import JobQueuePort
from src.domain.entity.job import JobId
from src.infra.config.settings import Settings


def redis_settings_from_url(url: str) -> RedisSettings:
    """Translate a Redis URL into arq RedisSettings."""
    parsed = urlparse(url)
    database = int((parsed.path or "/0").lstrip("/"))
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=database,
        password=parsed.password,
    )


async def create_redis_pool_from_settings(settings: Settings) -> ArqRedis:
    """Create an arq redis pool."""
    return await create_pool(redis_settings_from_url(settings.redis_url))


class ArqJobQueue(JobQueuePort):
    """Enqueue job ids into arq."""

    def __init__(self, redis_pool: ArqRedis, job_name: str) -> None:
        self._redis_pool = redis_pool
        self._job_name = job_name

    async def enqueue(self, job_id: JobId) -> None:
        """Queue a job identifier for execution."""
        await self._redis_pool.enqueue_job(self._job_name, job_id=str(job_id))
