"""SQLAlchemy implementation of the job repository."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.common.errors import JobNotFound
from src.app.repository.job_repository import JobRepository
from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import Job, JobId, JobStatus
from src.infra.persistence.mappers.job_mapper import apply_to_model, to_domain, to_model
from src.infra.persistence.models import JobModel


class SqlAlchemyJobRepository(JobRepository):
    """Persist jobs with SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, job: Job) -> None:
        """Persist a newly created job."""
        self._session.add(to_model(job))
        await self._session.commit()

    async def get(self, job_id: JobId) -> Job | None:
        """Fetch a single job."""
        model = await self._session.get(JobModel, str(job_id))
        return None if model is None else to_domain(model)

    async def list_by_api_key(
        self,
        api_key_id: ApiKeyId,
        *,
        page: int,
        per_page: int,
        status: JobStatus | None = None,
    ) -> tuple[list[Job], int]:
        """Return paginated jobs for an API key."""
        filters = [JobModel.api_key_id == str(api_key_id)]
        if status is not None:
            filters.append(JobModel.status == status.value)

        stmt = (
            select(JobModel)
            .where(*filters)
            .order_by(JobModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        items = (await self._session.scalars(stmt)).all()

        total_stmt = select(func.count()).select_from(JobModel).where(*filters)
        total = (await self._session.scalar(total_stmt)) or 0
        return [to_domain(item) for item in items], int(total)

    async def update(self, job: Job) -> None:
        """Persist changes to an existing job."""
        model = await self._session.get(JobModel, str(job.job_id))
        if model is None:
            raise JobNotFound(f"job '{job.job_id}' was not found")
        apply_to_model(job, model)
        await self._session.commit()
