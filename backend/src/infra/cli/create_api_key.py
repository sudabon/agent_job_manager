"""CLI for creating API keys."""

from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from src.domain.entity.api_key import API_KEY_ID_PREFIX, ApiKey, ApiKeyId
from src.infra.auth.api_key_hasher import hash_api_key
from src.infra.config.settings import get_settings
from src.infra.persistence.api_key_repository import SqlAlchemyApiKeyRepository
from src.infra.persistence.session import create_engine, create_session_factory


def _new_identifier() -> str:
    """Create a unique id suffix."""
    try:
        from ulid import ULID

        return str(ULID())
    except Exception:
        return uuid4().hex


async def _create_api_key(name: str) -> str:
    """Create and persist an API key, returning the plaintext secret."""
    settings = get_settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    secret = f"ajm_{_new_identifier()}"
    api_key = ApiKey(
        api_key_id=ApiKeyId(f"{API_KEY_ID_PREFIX}{_new_identifier()}"),
        name=name,
        key_hash=hash_api_key(secret),
        created_at=datetime.now(UTC),
    )
    async with session_factory() as session:
        repository = SqlAlchemyApiKeyRepository(session)
        await repository.add(api_key)
    await engine.dispose()
    return secret


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Create a new API key")
    parser.add_argument("--name", required=True, help="Logical name for the API key")
    args = parser.parse_args()
    secret = asyncio.run(_create_api_key(args.name))
    print(secret)


if __name__ == "__main__":
    main()
