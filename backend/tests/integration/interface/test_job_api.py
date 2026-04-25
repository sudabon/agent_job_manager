"""Interface integration tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.domain.entity.job import Job, JobExecution, JobId, JobStatus
from src.infra.persistence.job_repository import SqlAlchemyJobRepository


def _headers(plain_key: str) -> dict[str, str]:
    return {"X-API-Key": plain_key}


def test_health_endpoints_return_success(client) -> None:
    live = client.get("/health/live")
    ready = client.get("/health/ready")

    assert live.status_code == 200
    assert ready.status_code == 200


def test_submit_python_job_requires_api_key(client) -> None:
    response = client.post("/v1/jobs/python", json={"code": "print('hello')"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_job_endpoints_return_submitted_job(
    client,
    api_key,
    session_factory,
    redis_pool,
) -> None:
    _, plain_key = api_key

    submit_response = client.post(
        "/v1/jobs/python",
        json={"code": "print('hello')", "timeout_sec": 5, "metadata": {"source": "test"}},
        headers=_headers(plain_key),
    )
    assert submit_response.status_code == 200
    job_id = submit_response.json()["job_id"]
    assert redis_pool.enqueued_jobs[0][1]["job_id"] == job_id

    async with session_factory() as session:
        repository = SqlAlchemyJobRepository(session)
        stored_job = await repository.get(JobId(job_id))
        assert stored_job is not None
        completed_job = Job(
            job_id=stored_job.job_id,
            api_key_id=stored_job.api_key_id,
            job_type=stored_job.job_type,
            code=stored_job.code,
            timeout_sec=stored_job.timeout_sec,
            status=JobStatus.SUCCEEDED,
            metadata=stored_job.metadata,
            created_at=stored_job.created_at,
            execution=JobExecution(
                started_at=datetime.now(UTC),
                finished_at=datetime.now(UTC),
                exit_code=0,
                stdout="hello\n",
                stderr="",
                error_type=None,
            ),
        )
        await repository.update(completed_job)

    detail_response = client.get(f"/v1/jobs/{job_id}", headers=_headers(plain_key))
    logs_response = client.get(f"/v1/jobs/{job_id}/logs", headers=_headers(plain_key))
    list_response = client.get("/v1/jobs", headers=_headers(plain_key))

    assert detail_response.status_code == 200
    assert detail_response.json()["status"] == "succeeded"
    assert logs_response.status_code == 200
    assert logs_response.json()["stdout"] == "hello\n"
    assert list_response.status_code == 200
    assert list_response.json()["pagination"]["total"] == 1
