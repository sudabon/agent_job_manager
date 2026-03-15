"""Domain service for job state changes."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from src.domain.entity.job import ErrorType, Job, JobStatus
from src.domain.exceptions import InvalidJobStateTransition, InvalidTimeout

_ALLOWED_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.QUEUED: {JobStatus.RUNNING},
    JobStatus.RUNNING: {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.TIMED_OUT},
    JobStatus.SUCCEEDED: set(),
    JobStatus.FAILED: set(),
    JobStatus.TIMED_OUT: set(),
}


class JobDomainService:
    """Encapsulates state transition and timeout rules."""

    def validate_timeout(
        self,
        timeout_sec: int,
        *,
        min_timeout_sec: int,
        max_timeout_sec: int,
    ) -> None:
        """Ensure timeout bounds are respected."""
        if timeout_sec < min_timeout_sec or timeout_sec > max_timeout_sec:
            raise InvalidTimeout(
                f"timeout_sec must be between {min_timeout_sec} and {max_timeout_sec}"
            )

    def ensure_valid_transition(self, current: JobStatus, new: JobStatus) -> None:
        """Ensure a state transition is allowed."""
        if new not in _ALLOWED_TRANSITIONS[current]:
            raise InvalidJobStateTransition(
                f"cannot transition from {current.value} to {new.value}"
            )

    def mark_running(self, job: Job, *, started_at: datetime) -> Job:
        """Move a job from queued to running."""
        self.ensure_valid_transition(job.status, JobStatus.RUNNING)
        return replace(
            job,
            status=JobStatus.RUNNING,
            started_at=started_at,
            finished_at=None,
            exit_code=None,
            error_type=None,
        )

    def mark_finished(
        self,
        job: Job,
        *,
        finished_at: datetime,
        stdout: str,
        stderr: str,
        exit_code: int | None,
        error_type: ErrorType | None,
    ) -> Job:
        """Move a running job to a terminal state and persist execution results."""
        if error_type == ErrorType.TIMEOUT:
            status = JobStatus.TIMED_OUT
        elif exit_code == 0:
            status = JobStatus.SUCCEEDED
        else:
            status = JobStatus.FAILED
            if error_type is None:
                error_type = ErrorType.EXECUTION_ERROR

        self.ensure_valid_transition(job.status, status)
        return replace(
            job,
            status=status,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            finished_at=finished_at,
            error_type=error_type,
        )
