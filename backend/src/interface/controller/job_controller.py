"""Controller for job endpoints."""

from src.app.dto.job import GetJobInput, GetJobLogsInput, ListJobsInput, SubmitPythonJobInput
from src.app.usecase.get_job import GetJobUseCase
from src.app.usecase.get_job_logs import GetJobLogsUseCase
from src.app.usecase.list_jobs import ListJobsUseCase
from src.app.usecase.submit_python_job import SubmitPythonJobUseCase
from src.domain.entity.job import JobStatus
from src.interface.presender.job import JobPresender
from src.interface.viewmodel.job import (
    JobListViewModel,
    JobLogsViewModel,
    JobViewModel,
    SubmitJobResponseViewModel,
)


class JobController:
    """Coordinate HTTP job requests and application use cases."""

    def __init__(
        self,
        submit_job_use_case: SubmitPythonJobUseCase,
        get_job_use_case: GetJobUseCase,
        list_jobs_use_case: ListJobsUseCase,
        get_job_logs_use_case: GetJobLogsUseCase,
        presender: JobPresender,
    ) -> None:
        self._submit_job_use_case = submit_job_use_case
        self._get_job_use_case = get_job_use_case
        self._list_jobs_use_case = list_jobs_use_case
        self._get_job_logs_use_case = get_job_logs_use_case
        self._presender = presender

    async def submit_python_job(
        self,
        *,
        api_key_id: str,
        code: str,
        timeout_sec: int | None,
        metadata: dict[str, object] | None,
    ) -> SubmitJobResponseViewModel:
        """Submit a Python job."""
        output = await self._submit_job_use_case.execute(
            SubmitPythonJobInput(
                api_key_id=api_key_id,
                code=code,
                timeout_sec=timeout_sec,
                metadata=metadata,
            )
        )
        return self._presender.present_submit(output)

    async def get_job(self, *, api_key_id: str, job_id: str) -> JobViewModel:
        """Return a job detail response."""
        output = await self._get_job_use_case.execute(
            GetJobInput(api_key_id=api_key_id, job_id=job_id)
        )
        return self._presender.present_job(output)

    async def list_jobs(
        self,
        *,
        api_key_id: str,
        page: int,
        per_page: int,
        status: JobStatus | None,
    ) -> JobListViewModel:
        """Return a job list response."""
        output = await self._list_jobs_use_case.execute(
            ListJobsInput(api_key_id=api_key_id, page=page, per_page=per_page, status=status)
        )
        return self._presender.present_job_list(output)

    async def get_job_logs(self, *, api_key_id: str, job_id: str) -> JobLogsViewModel:
        """Return job logs."""
        output = await self._get_job_logs_use_case.execute(
            GetJobLogsInput(api_key_id=api_key_id, job_id=job_id)
        )
        return self._presender.present_logs(output)
