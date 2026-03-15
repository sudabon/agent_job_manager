"""Submit Python job use case."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from src.app.common.errors import ValidationError
from src.app.dto.job import SubmitPythonJobInput, SubmitPythonJobOutput
from src.app.port.job_queue import JobQueuePort
from src.app.repository.job_repository import JobRepository
from src.domain.entity.api_key import ApiKeyId
from src.domain.entity.job import JOB_ID_PREFIX, Job, JobId, JobStatus, JobType
from src.domain.exceptions import InvalidTimeout
from src.domain.service.job_domain_service import JobDomainService


def _default_ulid_factory() -> str:
    """Return a ULID string, falling back to UUID if the library is unavailable."""
    try:
        from ulid import ULID

        return str(ULID())
    except Exception:
        return uuid4().hex


class SubmitPythonJobUseCase:
    """Create and enqueue Python jobs."""

    def __init__(
        self,
        job_repository: JobRepository,
        queue: JobQueuePort,
        domain_service: JobDomainService,
        *,
        default_timeout_sec: int,
        min_timeout_sec: int,
        max_timeout_sec: int,
        max_code_size_bytes: int,
        ulid_factory: Callable[[], str] = _default_ulid_factory,
        now_provider: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._job_repository = job_repository
        self._queue = queue
        self._domain_service = domain_service
        self._default_timeout_sec = default_timeout_sec
        self._min_timeout_sec = min_timeout_sec
        self._max_timeout_sec = max_timeout_sec
        self._max_code_size_bytes = max_code_size_bytes
        self._ulid_factory = ulid_factory
        self._now_provider = now_provider

    async def execute(self, payload: SubmitPythonJobInput) -> SubmitPythonJobOutput:
        """Persist and enqueue a Python job."""
        timeout_sec = payload.timeout_sec or self._default_timeout_sec
        try:
            self._domain_service.validate_timeout(
                timeout_sec,
                min_timeout_sec=self._min_timeout_sec,
                max_timeout_sec=self._max_timeout_sec,
            )
        except InvalidTimeout as exc:
            raise ValidationError(str(exc)) from exc

        code_size = len(payload.code.encode("utf-8"))
        if code_size > self._max_code_size_bytes:
            raise ValidationError(f"code size must be <= {self._max_code_size_bytes} bytes")

        job = Job(
            job_id=JobId(f"{JOB_ID_PREFIX}{self._ulid_factory()}"),
            api_key_id=ApiKeyId(payload.api_key_id),
            job_type=JobType.PYTHON,
            code=payload.code,
            timeout_sec=timeout_sec,
            metadata=payload.metadata,
            status=JobStatus.QUEUED,
            created_at=self._now_provider(),
        )
        await self._job_repository.add(job)
        await self._queue.enqueue(job.job_id)
        return SubmitPythonJobOutput(job_id=str(job.job_id), status=job.status)
