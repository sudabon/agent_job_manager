"""Job repository abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import Job, JobId, JobStatus


class JobRepository(ABC):
    """Persistence contract for jobs."""

    @abstractmethod
    async def add(self, job: Job) -> None:
        """Persist a newly created job."""

    @abstractmethod
    async def get(self, job_id: JobId) -> Job | None:
        """Fetch a job by its identifier."""

    @abstractmethod
    async def list_by_api_key(
        self,
        api_key_id: ApiKeyId,
        *,
        page: int,
        per_page: int,
        status: JobStatus | None = None,
    ) -> tuple[list[Job], int]:
        """List jobs belonging to the supplied API key."""

    @abstractmethod
    async def update(self, job: Job) -> None:
        """Persist changes to an existing job."""
