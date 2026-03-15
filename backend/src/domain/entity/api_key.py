"""API key domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.exceptions import InvalidEntity

API_KEY_ID_PREFIX = "ak_"


@dataclass(frozen=True, slots=True)
class ApiKeyId:
    """Identifier for API keys."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.startswith(API_KEY_ID_PREFIX):
            raise InvalidEntity("api_key_id must start with 'ak_'")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ApiKey:
    """API key aggregate."""

    api_key_id: ApiKeyId
    name: str
    key_hash: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidEntity("name must not be blank")
        if not self.key_hash.strip():
            raise InvalidEntity("key_hash must not be blank")
