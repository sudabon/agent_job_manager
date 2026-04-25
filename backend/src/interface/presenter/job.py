"""Present application DTOs as job view models."""

from src.app.dto.job import (
    GetJobLogsOutput,
    JobDetailOutput,
    ListJobsOutput,
    SubmitPythonJobOutput,
)
from src.interface.viewmodel.job import (
    JobListViewModel,
    JobLogsViewModel,
    JobViewModel,
    PaginationViewModel,
    SubmitJobResponseViewModel,
)


class JobPresenter:
    """Convert use case DTOs into HTTP view models."""

    def present_submit(self, payload: SubmitPythonJobOutput) -> SubmitJobResponseViewModel:
        """Render a submission response."""
        return SubmitJobResponseViewModel(job_id=payload.job_id, status=payload.status)

    def present_job(self, payload: JobDetailOutput) -> JobViewModel:
        """Render a single job."""
        return JobViewModel(**payload.model_dump())

    def present_job_list(self, payload: ListJobsOutput) -> JobListViewModel:
        """Render a paginated job list."""
        return JobListViewModel(
            items=[self.present_job(item) for item in payload.items],
            pagination=PaginationViewModel(**payload.pagination.model_dump()),
        )

    def present_logs(self, payload: GetJobLogsOutput) -> JobLogsViewModel:
        """Render job logs."""
        return JobLogsViewModel(**payload.model_dump())
