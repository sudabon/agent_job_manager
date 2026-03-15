"""Job routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from src.domain.entity.api_key import ApiKey
from src.domain.entity.job import JobStatus
from src.infra.web.dependencies import get_current_api_key, get_job_controller
from src.interface.controller.job_controller import JobController
from src.interface.viewmodel.job import (
    JobListViewModel,
    JobLogsViewModel,
    JobViewModel,
    SubmitJobResponseViewModel,
)


class SubmitPythonJobRequest(BaseModel):
    """HTTP request body for Python job submission."""

    code: str = Field(min_length=1)
    timeout_sec: int | None = None
    metadata: dict[str, object] | None = None


def create_jobs_router() -> APIRouter:
    """Build the jobs router."""
    router = APIRouter(prefix="/v1/jobs", tags=["jobs"])

    @router.post("/python", response_model=SubmitJobResponseViewModel)
    async def submit_python_job(
        payload: SubmitPythonJobRequest,
        current_api_key: ApiKey = Depends(get_current_api_key),
        controller: JobController = Depends(get_job_controller),
    ) -> SubmitJobResponseViewModel:
        return await controller.submit_python_job(
            api_key_id=str(current_api_key.api_key_id),
            code=payload.code,
            timeout_sec=payload.timeout_sec,
            metadata=payload.metadata,
        )

    @router.get("", response_model=JobListViewModel)
    async def list_jobs(
        page: int = Query(default=1, ge=1),
        per_page: int = Query(default=20, ge=1, le=100),
        status: JobStatus | None = Query(default=None),
        current_api_key: ApiKey = Depends(get_current_api_key),
        controller: JobController = Depends(get_job_controller),
    ) -> JobListViewModel:
        return await controller.list_jobs(
            api_key_id=str(current_api_key.api_key_id),
            page=page,
            per_page=per_page,
            status=status,
        )

    @router.get("/{job_id}", response_model=JobViewModel)
    async def get_job(
        job_id: str,
        current_api_key: ApiKey = Depends(get_current_api_key),
        controller: JobController = Depends(get_job_controller),
    ) -> JobViewModel:
        return await controller.get_job(api_key_id=str(current_api_key.api_key_id), job_id=job_id)

    @router.get("/{job_id}/logs", response_model=JobLogsViewModel)
    async def get_job_logs(
        job_id: str,
        current_api_key: ApiKey = Depends(get_current_api_key),
        controller: JobController = Depends(get_job_controller),
    ) -> JobLogsViewModel:
        return await controller.get_job_logs(
            api_key_id=str(current_api_key.api_key_id),
            job_id=job_id,
        )

    return router
