"""Job persistence mapping helpers."""

from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import ErrorType, Job, JobExecution, JobId, JobStatus, JobType
from src.infra.persistence.models import JobModel


def to_model(job: Job) -> JobModel:
    """Convert a domain entity to an ORM model."""
    model = JobModel()
    apply_to_model(job, model)
    return model


def apply_to_model(job: Job, model: JobModel) -> None:
    """Apply a domain job's fields to an existing ORM model."""
    model.job_id = str(job.job_id)
    model.api_key_id = str(job.api_key_id)
    model.job_type = job.job_type.value
    model.code = job.code
    model.timeout_sec = job.timeout_sec
    model.status = job.status.value
    model.created_at = job.created_at
    execution = job.execution
    model.started_at = execution.started_at if execution else None
    model.finished_at = execution.finished_at if execution else None
    model.exit_code = execution.exit_code if execution else None
    model.stdout = execution.stdout if execution else ""
    model.stderr = execution.stderr if execution else ""
    model.error_type = execution.error_type.value if execution and execution.error_type else None
    model.metadata_json = job.metadata


def to_domain(model: JobModel) -> Job:
    """Convert an ORM model to a domain entity."""
    execution = None
    if (
        model.started_at is not None
        or model.finished_at is not None
        or model.exit_code is not None
        or model.stdout
        or model.stderr
        or model.error_type is not None
    ):
        execution = JobExecution(
            started_at=model.started_at,
            finished_at=model.finished_at,
            exit_code=model.exit_code,
            stdout=model.stdout,
            stderr=model.stderr,
            error_type=ErrorType(model.error_type) if model.error_type else None,
        )

    return Job(
        job_id=JobId(model.job_id),
        api_key_id=ApiKeyId(model.api_key_id),
        job_type=JobType(model.job_type),
        code=model.code,
        timeout_sec=model.timeout_sec,
        status=JobStatus(model.status),
        metadata=model.metadata_json,
        created_at=model.created_at,
        execution=execution,
    )
