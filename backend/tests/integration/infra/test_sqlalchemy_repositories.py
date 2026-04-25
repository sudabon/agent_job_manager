"""Persistence integration tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.app.common.errors import JobNotFound
from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import Job, JobId, JobStatus, JobType
from src.infra.persistence.job_repository import SqlAlchemyJobRepository


@pytest.mark.asyncio
async def test_sqlalchemy_job_repository_persists_and_lists_jobs(session_factory) -> None:
    async with session_factory() as session:
        repository = SqlAlchemyJobRepository(session)
        job = Job(
            job_id=JobId("job_persisted"),
            api_key_id=ApiKeyId("ak_test"),
            job_type=JobType.PYTHON,
            code="print('hello')",
            timeout_sec=10,
            status=JobStatus.QUEUED,
            created_at=datetime.now(UTC),
        )
        await repository.add(job)

    async with session_factory() as session:
        repository = SqlAlchemyJobRepository(session)
        persisted = await repository.get(JobId("job_persisted"))
        jobs, total = await repository.list_by_api_key(ApiKeyId("ak_test"), page=1, per_page=10)

    assert persisted is not None
    assert persisted.job_id.value == "job_persisted"
    assert total == 1
    assert jobs[0].job_id.value == "job_persisted"


@pytest.mark.asyncio
async def test_sqlalchemy_job_repository_update_requires_existing_job(session_factory) -> None:
    async with session_factory() as session:
        repository = SqlAlchemyJobRepository(session)
        job = Job(
            job_id=JobId("job_missing_update"),
            api_key_id=ApiKeyId("ak_test"),
            job_type=JobType.PYTHON,
            code="print('hello')",
            timeout_sec=10,
            status=JobStatus.QUEUED,
            created_at=datetime.now(UTC),
        )

        with pytest.raises(JobNotFound):
            await repository.update(job)

        persisted = await repository.get(JobId("job_missing_update"))

    assert persisted is None
