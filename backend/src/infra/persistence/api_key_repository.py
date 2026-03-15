"""SQLAlchemy implementation of the API key repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.repository.api_key_repository import ApiKeyRepository
from src.domain.entity.api_key import ApiKey, ApiKeyId
from src.infra.persistence.models import ApiKeyModel


class SqlAlchemyApiKeyRepository(ApiKeyRepository):
    """Persist API keys with SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, api_key: ApiKey) -> None:
        """Persist a new API key."""
        self._session.add(
            ApiKeyModel(
                api_key_id=str(api_key.api_key_id),
                name=api_key.name,
                key_hash=api_key.key_hash,
                is_active=api_key.is_active,
                created_at=api_key.created_at,
            )
        )
        await self._session.commit()

    async def get(self, api_key_id: ApiKeyId) -> ApiKey | None:
        """Fetch an API key by id."""
        model = await self._session.get(ApiKeyModel, str(api_key_id))
        return None if model is None else self._to_domain(model)

    async def get_by_hash(self, key_hash: str) -> ApiKey | None:
        """Fetch an API key by hashed secret."""
        stmt = select(ApiKeyModel).where(ApiKeyModel.key_hash == key_hash)
        model = await self._session.scalar(stmt)
        return None if model is None else self._to_domain(model)

    def _to_domain(self, model: ApiKeyModel) -> ApiKey:
        """Convert an ORM model into a domain entity."""
        return ApiKey(
            api_key_id=ApiKeyId(model.api_key_id),
            name=model.name,
            key_hash=model.key_hash,
            is_active=model.is_active,
            created_at=model.created_at,
        )
