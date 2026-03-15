"""Docker-backed job runner."""

from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Any

import docker

from src.app.dto.job import JobExecutionResult
from src.app.port.job_runner import JobRunnerPort
from src.domain.entity.job import ErrorType, Job
from src.infra.config.settings import Settings

LOGGER = logging.getLogger(__name__)


class DockerRunner(JobRunnerPort):
    """Run Python jobs inside isolated Docker containers."""

    def __init__(self, settings: Settings, client: docker.DockerClient | None = None) -> None:
        self._settings = settings
        self._client = client or docker.from_env()

    async def execute(self, job: Job) -> JobExecutionResult:
        """Run job code inside a container and collect execution artifacts."""
        with tempfile.TemporaryDirectory(prefix=f"{job.job_id.value}_") as temp_dir:
            workspace = Path(temp_dir)
            code_path = workspace / "main.py"
            stdout_path = workspace / "stdout.txt"
            stderr_path = workspace / "stderr.txt"
            code_path.write_text(job.code, encoding="utf-8")

            container = await asyncio.to_thread(self._create_container, workspace)
            try:
                await asyncio.to_thread(container.start)
                try:
                    wait_result = await asyncio.wait_for(
                        asyncio.to_thread(container.wait),
                        timeout=job.timeout_sec,
                    )
                    exit_code = int(wait_result.get("StatusCode", 1))
                    stderr_suffix = ""
                    error_type = ErrorType.OOM if exit_code == 137 else None
                except TimeoutError:
                    await asyncio.to_thread(container.kill)
                    exit_code = None
                    stderr_suffix = "\nExecution timed out."
                    error_type = ErrorType.TIMEOUT

                stdout = self._truncate(
                    stdout_path.read_text(encoding="utf-8") if stdout_path.exists() else ""
                )
                stderr_raw = stderr_path.read_text(encoding="utf-8") if stderr_path.exists() else ""
                stderr = self._truncate(f"{stderr_raw}{stderr_suffix}".strip())
                return JobExecutionResult(
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                    error_type=error_type,
                )
            finally:
                await asyncio.to_thread(self._cleanup_container, container, job.job_id.value)

    def _create_container(self, workspace: Path) -> Any:
        """Create a Docker container for job execution."""
        command = (
            'sh -lc "python /workspace/main.py > /workspace/stdout.txt 2> /workspace/stderr.txt"'
        )
        return self._client.containers.create(
            image=self._settings.docker_base_image,
            command=command,
            detach=True,
            working_dir="/workspace",
            network_disabled=True,
            mem_limit=self._settings.docker_memory_limit,
            volumes={str(workspace): {"bind": "/workspace", "mode": "rw"}},
        )

    def _cleanup_container(self, container: Any, job_id: str) -> None:
        """Force-remove a container and log failures."""
        try:
            container.remove(force=True)
        except Exception:
            LOGGER.exception("failed to cleanup container", extra={"job_id": job_id})

    def _truncate(self, value: str) -> str:
        """Apply the configured log truncation rule."""
        encoded = value.encode("utf-8")
        if len(encoded) <= self._settings.max_log_bytes:
            return value
        truncated = encoded[: self._settings.max_log_bytes].decode("utf-8", errors="ignore")
        return f"{truncated}\n...[truncated]"
