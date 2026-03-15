"""API key repository abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entity.api_key import ApiKey, ApiKeyId


class ApiKeyRepository(ABC):
    """Persistence contract for API keys."""

    @abstractmethod
    async def add(self, api_key: ApiKey) -> None:
        """Persist a new API key."""

    @abstractmethod
    async def get(self, api_key_id: ApiKeyId) -> ApiKey | None:
        """Fetch an API key by identifier."""

    @abstractmethod
    async def get_by_hash(self, key_hash: str) -> ApiKey | None:
        """Fetch an API key by hash."""
