"""Application DTOs for job workflows."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.entity.job import ErrorType, Job, JobStatus, JobType


class SubmitPythonJobInput(BaseModel):
    """Input payload for creating a Python job."""

    api_key_id: str
    code: str = Field(min_length=1)
    timeout_sec: int | None = None
    metadata: dict[str, object] | None = None


class SubmitPythonJobOutput(BaseModel):
    """Response after creating a job."""

    job_id: str
    status: JobStatus


class GetJobInput(BaseModel):
    """Lookup input for a single job."""

    api_key_id: str
    job_id: str


class ExecuteJobInput(BaseModel):
    """Worker input for executing a job."""

    job_id: str


class JobDetailOutput(BaseModel):
    """Detailed job representation."""

    job_id: str
    job_type: JobType
    status: JobStatus
    timeout_sec: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    exit_code: int | None
    error_type: ErrorType | None
    metadata: dict[str, object] | None

    @classmethod
    def from_job(cls, job: Job) -> JobDetailOutput:
        """Convert a domain entity into a DTO."""
        return cls(
            job_id=str(job.job_id),
            job_type=job.job_type,
            status=job.status,
            timeout_sec=job.timeout_sec,
            created_at=job.created_at,
            started_at=job.started_at,
            finished_at=job.finished_at,
            exit_code=job.exit_code,
            error_type=job.error_type,
            metadata=job.metadata,
        )


class ListJobsInput(BaseModel):
    """List query parameters."""

    api_key_id: str
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    status: JobStatus | None = None


class PaginationOutput(BaseModel):
    """Pagination metadata."""

    page: int
    per_page: int
    total: int


class ListJobsOutput(BaseModel):
    """Paginated job list."""

    items: list[JobDetailOutput]
    pagination: PaginationOutput


class GetJobLogsInput(BaseModel):
    """Lookup input for job logs."""

    api_key_id: str
    job_id: str


class GetJobLogsOutput(BaseModel):
    """Job log response."""

    job_id: str
    stdout: str
    stderr: str


class JobExecutionResult(BaseModel):
    """Runner output payload."""

    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    error_type: ErrorType | None = None
