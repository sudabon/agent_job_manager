"""Application settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables."""

    app_name: str = "agent-job-manager"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_job_manager"
    redis_url: str = "redis://localhost:6379/0"
    docker_base_image: str = "python:3.12-slim"
    default_timeout_sec: int = 30
    min_timeout_sec: int = 1
    max_timeout_sec: int = 300
    max_code_size_bytes: int = 64 * 1024
    max_log_bytes: int = 1024 * 1024
    docker_memory_limit: str = "256m"
    worker_queue_name: str = "execute_job"
    api_key_header_name: str = "X-API-Key"
    request_id_header_name: str = "X-Request-Id"
    log_level: str = "INFO"
    readiness_timeout_sec: int = Field(default=3, ge=1)

    model_config = SettingsConfigDict(
        env_prefix="AJM_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
