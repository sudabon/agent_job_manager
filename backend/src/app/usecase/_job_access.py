"""Shared job access helpers."""

from src.app.common.errors import JobNotFound
from src.app.repository.job_repository import JobRepository
from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import Job, JobId


async def find_owned_job(repo: JobRepository, job_id: JobId, owner: ApiKeyId) -> Job:
    """Return a job if it belongs to the owner, otherwise raise not found."""
    job = await repo.get(job_id)
    if job is None or job.api_key_id != owner:
        raise JobNotFound(f"job '{job_id}' was not found")
    return job
