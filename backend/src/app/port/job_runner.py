"""Port for executing jobs."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.app.dto.job import JobExecutionResult
from src.domain.entity.job import Job


class JobRunnerPort(ABC):
    """Execution backend abstraction."""

    @abstractmethod
    async def execute(self, job: Job) -> JobExecutionResult:
        """Run a job and return its execution result."""
