"""Execute job use case."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from src.app.common.errors import JobNotFound
from src.app.dto.job import ExecuteJobInput, JobDetailOutput, JobExecutionResult
from src.app.port.job_runner import JobRunnerPort
from src.app.repository.job_repository import JobRepository
from src.domain.entity.job import ErrorType, JobId
from src.domain.service.job_domain_service import JobDomainService


class ExecuteJobUseCase:
    """Drive job execution lifecycle for worker processes."""

    def __init__(
        self,
        job_repository: JobRepository,
        runner: JobRunnerPort,
        domain_service: JobDomainService,
        *,
        now_provider: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._job_repository = job_repository
        self._runner = runner
        self._domain_service = domain_service
        self._now_provider = now_provider

    async def execute(self, payload: ExecuteJobInput) -> JobDetailOutput:
        """Run a queued job and persist the final state."""
        job = await self._job_repository.get(JobId(payload.job_id))
        if job is None:
            raise JobNotFound(f"job '{payload.job_id}' was not found")

        running_job = self._domain_service.mark_running(job, started_at=self._now_provider())
        await self._job_repository.update(running_job)

        try:
            execution_result = await self._runner.execute(running_job)
        except Exception as exc:
            execution_result = JobExecutionResult(
                stderr=str(exc),
                error_type=ErrorType.INFRASTRUCTURE_ERROR,
            )

        completed_job = self._domain_service.mark_finished(
            running_job,
            finished_at=self._now_provider(),
            stdout=execution_result.stdout,
            stderr=execution_result.stderr,
            exit_code=execution_result.exit_code,
            error_type=execution_result.error_type,
        )
        await self._job_repository.update(completed_job)
        return JobDetailOutput.from_job(completed_job)
