"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from src.domain.entity.api_key import API_KEY_ID_PREFIX, ApiKey, ApiKeyId
from src.infra.auth.api_key_hasher import hash_api_key
from src.infra.config.settings import Settings
from src.infra.persistence.api_key_repository import SqlAlchemyApiKeyRepository
from src.infra.persistence.base import Base
from src.infra.persistence.session import create_engine, create_session_factory
from src.main import create_app


class FakeRedisPool:
    """Small fake used by tests."""

    def __init__(self) -> None:
        self.enqueued_jobs: list[tuple[str, dict[str, object]]] = []

    async def enqueue_job(self, job_name: str, **kwargs: object) -> None:
        self.enqueued_jobs.append((job_name, kwargs))

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        return None


@pytest.fixture
def test_settings(tmp_path) -> Settings:
    """Return test settings."""
    return Settings(
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'test.db'}",
        redis_url="redis://localhost:6379/15",
        log_level="INFO",
    )


@pytest.fixture
async def engine(test_settings: Settings) -> AsyncIterator[AsyncEngine]:
    """Create a test database."""
    engine = create_engine(test_settings)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine):
    """Create a session factory bound to the test engine."""
    return create_session_factory(engine)


@pytest.fixture
async def api_key(session_factory) -> tuple[ApiKey, str]:
    """Insert a reusable API key."""
    plain = "plain_test_key"
    entity = ApiKey(
        api_key_id=ApiKeyId(f"{API_KEY_ID_PREFIX}test"),
        name="test-key",
        key_hash=hash_api_key(plain),
    )
    async with session_factory() as session:
        await SqlAlchemyApiKeyRepository(session).add(entity)
    return entity, plain


@pytest.fixture
def redis_pool() -> FakeRedisPool:
    """Return a fake redis pool."""
    return FakeRedisPool()


@pytest.fixture
def client(test_settings: Settings, engine: AsyncEngine, redis_pool: FakeRedisPool) -> TestClient:
    """Create a test client."""
    with TestClient(create_app(test_settings, engine=engine, redis_pool=redis_pool)) as test_client:
        yield test_client
