"""SQLAlchemy implementation of the job repository."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.repository.job_repository import JobRepository
from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import ErrorType, Job, JobId, JobStatus, JobType
from src.infra.persistence.models import JobModel


class SqlAlchemyJobRepository(JobRepository):
    """Persist jobs with SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, job: Job) -> None:
        """Persist a newly created job."""
        self._session.add(self._to_model(job))
        await self._session.commit()

    async def get(self, job_id: JobId) -> Job | None:
        """Fetch a single job."""
        model = await self._session.get(JobModel, str(job_id))
        return None if model is None else self._to_domain(model)

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
        return [self._to_domain(item) for item in items], int(total)

    async def update(self, job: Job) -> None:
        """Persist changes to an existing job."""
        model = await self._session.get(JobModel, str(job.job_id))
        if model is None:
            model = self._to_model(job)
            self._session.add(model)
        else:
            model.api_key_id = str(job.api_key_id)
            model.job_type = job.job_type.value
            model.code = job.code
            model.timeout_sec = job.timeout_sec
            model.status = job.status.value
            model.created_at = job.created_at
            model.started_at = job.started_at
            model.finished_at = job.finished_at
            model.exit_code = job.exit_code
            model.stdout = job.stdout
            model.stderr = job.stderr
            model.error_type = job.error_type.value if job.error_type else None
            model.metadata_json = job.metadata
        await self._session.commit()

    def _to_model(self, job: Job) -> JobModel:
        """Convert a domain entity to an ORM model."""
        return JobModel(
            job_id=str(job.job_id),
            api_key_id=str(job.api_key_id),
            job_type=job.job_type.value,
            code=job.code,
            timeout_sec=job.timeout_sec,
            status=job.status.value,
            created_at=job.created_at,
            started_at=job.started_at,
            finished_at=job.finished_at,
            exit_code=job.exit_code,
            stdout=job.stdout,
            stderr=job.stderr,
            error_type=job.error_type.value if job.error_type else None,
            metadata_json=job.metadata,
        )

    def _to_domain(self, model: JobModel) -> Job:
        """Convert an ORM model to a domain entity."""
        return Job(
            job_id=JobId(model.job_id),
            api_key_id=ApiKeyId(model.api_key_id),
            job_type=JobType(model.job_type),
            code=model.code,
            timeout_sec=model.timeout_sec,
            status=JobStatus(model.status),
            metadata=model.metadata_json,
            created_at=model.created_at,
            started_at=model.started_at,
            finished_at=model.finished_at,
            exit_code=model.exit_code,
            stdout=model.stdout,
            stderr=model.stderr,
            error_type=ErrorType(model.error_type) if model.error_type else None,
        )
