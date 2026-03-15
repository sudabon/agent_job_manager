"""API key hashing utilities."""

from __future__ import annotations

import hashlib
import hmac


def hash_api_key(value: str) -> str:
    """Hash an API key using SHA-256."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_api_key(value: str, expected_hash: str) -> bool:
    """Verify a plaintext API key against a stored hash."""
    return hmac.compare_digest(hash_api_key(value), expected_hash)
