"""Port for enqueueing jobs."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entity.job import JobId


class JobQueuePort(ABC):
    """Queue abstraction for asynchronous execution."""

    @abstractmethod
    async def enqueue(self, job_id: JobId) -> None:
        """Enqueue a job identifier for worker processing."""
