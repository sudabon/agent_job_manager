"""Job domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from src.domain.entity.api_key import ApiKeyId
from src.domain.exceptions import InvalidEntity

JOB_ID_PREFIX = "job_"


class JobStatus(StrEnum):
    """Allowed job statuses."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


class JobType(StrEnum):
    """Supported job types."""

    PYTHON = "python"


class ErrorType(StrEnum):
    """Known job error categories."""

    TIMEOUT = "timeout"
    EXECUTION_ERROR = "execution_error"
    OOM = "oom"
    INFRASTRUCTURE_ERROR = "infrastructure_error"


@dataclass(frozen=True, slots=True)
class JobId:
    """Identifier for jobs."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.startswith(JOB_ID_PREFIX):
            raise InvalidEntity("job_id must start with 'job_'")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Job:
    """Job aggregate root."""

    job_id: JobId
    api_key_id: ApiKeyId
    job_type: JobType
    code: str
    timeout_sec: int
    status: JobStatus = JobStatus.QUEUED
    metadata: dict[str, object] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    finished_at: datetime | None = None
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    error_type: ErrorType | None = None

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise InvalidEntity("code must not be blank")
        if self.timeout_sec < 1:
            raise InvalidEntity("timeout_sec must be positive")
