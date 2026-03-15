"""Get job details use case."""

from src.app.common.errors import JobNotFound
from src.app.dto.job import GetJobInput, JobDetailOutput
from src.app.repository.job_repository import JobRepository
from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import JobId


class GetJobUseCase:
    """Retrieve a single job if it belongs to the caller."""

    def __init__(self, job_repository: JobRepository) -> None:
        self._job_repository = job_repository

    async def execute(self, payload: GetJobInput) -> JobDetailOutput:
        """Return a job or raise if it does not exist for the API key."""
        job = await self._job_repository.get(JobId(payload.job_id))
        if job is None or job.api_key_id != ApiKeyId(payload.api_key_id):
            raise JobNotFound(f"job '{payload.job_id}' was not found")
        return JobDetailOutput.from_job(job)
