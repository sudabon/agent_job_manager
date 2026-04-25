"""Identifier generation helpers."""

from __future__ import annotations

from uuid import uuid4


def new_id() -> str:
    """Return a ULID string, falling back to UUID if the library is unavailable."""
    try:
        from ulid import ULID
    except ImportError:
        return uuid4().hex

    return str(ULID())
