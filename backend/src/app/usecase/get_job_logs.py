"""Get job logs use case."""

from src.app.common.errors import JobNotFound
from src.app.dto.job import GetJobLogsInput, GetJobLogsOutput
from src.app.repository.job_repository import JobRepository
from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import JobId


class GetJobLogsUseCase:
    """Retrieve logs for a caller-owned job."""

    def __init__(self, job_repository: JobRepository) -> None:
        self._job_repository = job_repository

    async def execute(self, payload: GetJobLogsInput) -> GetJobLogsOutput:
        """Return stdout and stderr for a job."""
        job = await self._job_repository.get(JobId(payload.job_id))
        if job is None or job.api_key_id != ApiKeyId(payload.api_key_id):
            raise JobNotFound(f"job '{payload.job_id}' was not found")
        return GetJobLogsOutput(job_id=str(job.job_id), stdout=job.stdout, stderr=job.stderr)
