"""Get job details use case."""

from src.app.dto.job import GetJobInput, JobDetailOutput
from src.app.repository.job_repository import JobRepository
from src.app.usecase._job_access import find_owned_job
from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import JobId


class GetJobUseCase:
    """Retrieve a single job if it belongs to the caller."""

    def __init__(self, job_repository: JobRepository) -> None:
        self._job_repository = job_repository

    async def execute(self, payload: GetJobInput) -> JobDetailOutput:
        """Return a job or raise if it does not exist for the API key."""
        job = await find_owned_job(
            self._job_repository,
            JobId(payload.job_id),
            ApiKeyId(payload.api_key_id),
        )
        return JobDetailOutput.from_job(job)
