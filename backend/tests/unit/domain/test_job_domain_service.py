"""Domain layer tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import ErrorType, Job, JobId, JobStatus, JobType
from src.domain.exceptions import InvalidJobStateTransition, InvalidTimeout
from src.domain.service.job_domain_service import JobDomainService


def _job(status: JobStatus = JobStatus.QUEUED) -> Job:
    return Job(
        job_id=JobId("job_test"),
        api_key_id=ApiKeyId("ak_test"),
        job_type=JobType.PYTHON,
        code="print('hello')",
        timeout_sec=30,
        status=status,
    )


def test_job_domain_service_mark_running_allows_transition() -> None:
    service = JobDomainService()
    running_job = service.mark_running(_job(), started_at=datetime.now(UTC))
    assert running_job.status == JobStatus.RUNNING
    assert running_job.execution is not None
    assert running_job.execution.started_at is not None


def test_job_domain_service_mark_finished_rejects_invalid_transition() -> None:
    service = JobDomainService()
    with pytest.raises(InvalidJobStateTransition):
        service.mark_finished(
            _job(JobStatus.QUEUED),
            finished_at=datetime.now(UTC),
            stdout="",
            stderr="",
            exit_code=0,
            error_type=None,
        )


def test_job_domain_service_mark_finished_marks_timeout() -> None:
    service = JobDomainService()
    finished_job = service.mark_finished(
        _job(JobStatus.RUNNING),
        finished_at=datetime.now(UTC),
        stdout="",
        stderr="Execution timed out.",
        exit_code=None,
        error_type=ErrorType.TIMEOUT,
    )
    assert finished_job.status == JobStatus.TIMED_OUT
    assert finished_job.execution is not None
    assert finished_job.execution.error_type == ErrorType.TIMEOUT


def test_job_domain_service_validate_timeout_rejects_out_of_range_value() -> None:
    service = JobDomainService()
    with pytest.raises(InvalidTimeout):
        service.validate_timeout(0, min_timeout_sec=1, max_timeout_sec=300)
