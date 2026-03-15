"""Application layer tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.app.common.errors import JobNotFound, ValidationError
from src.app.dto.job import (
    ExecuteJobInput,
    GetJobInput,
    GetJobLogsInput,
    JobExecutionResult,
    ListJobsInput,
    SubmitPythonJobInput,
)
from src.app.usecase.execute_job import ExecuteJobUseCase
from src.app.usecase.get_job import GetJobUseCase
from src.app.usecase.get_job_logs import GetJobLogsUseCase
from src.app.usecase.list_jobs import ListJobsUseCase
from src.app.usecase.submit_python_job import SubmitPythonJobUseCase
from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import ErrorType, Job, JobId, JobStatus, JobType
from src.domain.service.job_domain_service import JobDomainService


class InMemoryJobRepository:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}

    async def add(self, job: Job) -> None:
        self.jobs[str(job.job_id)] = job

    async def get(self, job_id: JobId) -> Job | None:
        return self.jobs.get(str(job_id))

    async def list_by_api_key(self, api_key_id: ApiKeyId, *, page: int, per_page: int, status=None):
        jobs = [job for job in self.jobs.values() if job.api_key_id == api_key_id]
        if status is not None:
            jobs = [job for job in jobs if job.status == status]
        jobs.sort(key=lambda job: job.created_at, reverse=True)
        start = (page - 1) * per_page
        return jobs[start : start + per_page], len(jobs)

    async def update(self, job: Job) -> None:
        self.jobs[str(job.job_id)] = job


class DummyQueue:
    def __init__(self) -> None:
        self.values: list[str] = []

    async def enqueue(self, job_id: JobId) -> None:
        self.values.append(str(job_id))


class DummyRunner:
    def __init__(self, result: JobExecutionResult) -> None:
        self.result = result

    async def execute(self, _job: Job) -> JobExecutionResult:
        return self.result


def _job(status: JobStatus = JobStatus.QUEUED) -> Job:
    return Job(
        job_id=JobId("job_existing"),
        api_key_id=ApiKeyId("ak_test"),
        job_type=JobType.PYTHON,
        code="print('hello')",
        timeout_sec=30,
        status=status,
        created_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_submit_python_job_use_case_creates_and_enqueues_job() -> None:
    repository = InMemoryJobRepository()
    queue = DummyQueue()
    use_case = SubmitPythonJobUseCase(
        repository,
        queue,
        JobDomainService(),
        default_timeout_sec=30,
        min_timeout_sec=1,
        max_timeout_sec=300,
        max_code_size_bytes=64 * 1024,
        ulid_factory=lambda: "01TEST",
        now_provider=lambda: datetime(2026, 3, 15, tzinfo=UTC),
    )

    payload = await use_case.execute(
        SubmitPythonJobInput(api_key_id="ak_test", code="print('hello')", timeout_sec=10)
    )

    assert payload.job_id == "job_01TEST"
    assert queue.values == ["job_01TEST"]


@pytest.mark.asyncio
async def test_submit_python_job_use_case_rejects_large_code() -> None:
    use_case = SubmitPythonJobUseCase(
        InMemoryJobRepository(),
        DummyQueue(),
        JobDomainService(),
        default_timeout_sec=30,
        min_timeout_sec=1,
        max_timeout_sec=300,
        max_code_size_bytes=4,
    )

    with pytest.raises(ValidationError):
        await use_case.execute(
            SubmitPythonJobInput(api_key_id="ak_test", code="print('too big')", timeout_sec=10)
        )


@pytest.mark.asyncio
async def test_get_job_use_case_raises_for_missing_job() -> None:
    with pytest.raises(JobNotFound):
        await GetJobUseCase(InMemoryJobRepository()).execute(
            GetJobInput(api_key_id="ak_test", job_id="job_missing")
        )


@pytest.mark.asyncio
async def test_list_jobs_use_case_returns_paginated_items() -> None:
    repository = InMemoryJobRepository()
    existing_job = _job()
    await repository.add(existing_job)

    output = await ListJobsUseCase(repository).execute(
        ListJobsInput(api_key_id="ak_test", page=1, per_page=10)
    )

    assert output.pagination.total == 1
    assert output.items[0].job_id == "job_existing"


@pytest.mark.asyncio
async def test_get_job_logs_use_case_returns_logs() -> None:
    repository = InMemoryJobRepository()
    await repository.add(_job())

    output = await GetJobLogsUseCase(repository).execute(
        GetJobLogsInput(api_key_id="ak_test", job_id="job_existing")
    )

    assert output.stdout == ""
    assert output.stderr == ""


@pytest.mark.asyncio
async def test_execute_job_use_case_updates_terminal_state() -> None:
    repository = InMemoryJobRepository()
    await repository.add(_job())
    use_case = ExecuteJobUseCase(
        repository,
        DummyRunner(JobExecutionResult(stdout="hello\n", exit_code=0)),
        JobDomainService(),
        now_provider=lambda: datetime(2026, 3, 15, tzinfo=UTC),
    )

    output = await use_case.execute(ExecuteJobInput(job_id="job_existing"))

    assert output.status == JobStatus.SUCCEEDED
    assert repository.jobs["job_existing"].stdout == "hello\n"


@pytest.mark.asyncio
async def test_execute_job_use_case_marks_infrastructure_error_on_runner_failure() -> None:
    class FailingRunner:
        async def execute(self, _job: Job) -> JobExecutionResult:
            raise RuntimeError("boom")

    repository = InMemoryJobRepository()
    await repository.add(_job())
    use_case = ExecuteJobUseCase(repository, FailingRunner(), JobDomainService())

    output = await use_case.execute(ExecuteJobInput(job_id="job_existing"))

    assert output.status == JobStatus.FAILED
    assert repository.jobs["job_existing"].error_type == ErrorType.INFRASTRUCTURE_ERROR
