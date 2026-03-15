"""View models for job endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from src.domain.entity.job import ErrorType, JobStatus, JobType


class SubmitJobResponseViewModel(BaseModel):
    """Response returned after job submission."""

    job_id: str
    status: JobStatus


class JobViewModel(BaseModel):
    """Detailed job response."""

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


class PaginationViewModel(BaseModel):
    """Pagination metadata."""

    page: int
    per_page: int
    total: int


class JobListViewModel(BaseModel):
    """Paginated job list response."""

    items: list[JobViewModel]
    pagination: PaginationViewModel


class JobLogsViewModel(BaseModel):
    """Job logs response."""

    job_id: str
    stdout: str
    stderr: str
