"""List jobs use case."""

from src.app.dto.job import JobDetailOutput, ListJobsInput, ListJobsOutput, PaginationOutput
from src.app.repository.job_repository import JobRepository
from src.domain.entity.api_key import ApiKeyId


class ListJobsUseCase:
    """List jobs for an API key."""

    def __init__(self, job_repository: JobRepository) -> None:
        self._job_repository = job_repository

    async def execute(self, payload: ListJobsInput) -> ListJobsOutput:
        """Return paginated jobs for the caller."""
        jobs, total = await self._job_repository.list_by_api_key(
            ApiKeyId(payload.api_key_id),
            page=payload.page,
            per_page=payload.per_page,
            status=payload.status,
        )
        return ListJobsOutput(
            items=[JobDetailOutput.from_job(job) for job in jobs],
            pagination=PaginationOutput(
                page=payload.page,
                per_page=payload.per_page,
                total=total,
            ),
        )
