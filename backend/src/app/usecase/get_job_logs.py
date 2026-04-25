"""Get job logs use case."""

from src.app.dto.job import GetJobLogsInput, GetJobLogsOutput
from src.app.repository.job_repository import JobRepository
from src.app.usecase._job_access import find_owned_job
from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import JobId


class GetJobLogsUseCase:
    """Retrieve logs for a caller-owned job."""

    def __init__(self, job_repository: JobRepository) -> None:
        self._job_repository = job_repository

    async def execute(self, payload: GetJobLogsInput) -> GetJobLogsOutput:
        """Return stdout and stderr for a job."""
        job = await find_owned_job(
            self._job_repository,
            JobId(payload.job_id),
            ApiKeyId(payload.api_key_id),
        )
        execution = job.execution
        return GetJobLogsOutput(
            job_id=str(job.job_id),
            stdout=execution.stdout if execution else "",
            stderr=execution.stderr if execution else "",
        )
