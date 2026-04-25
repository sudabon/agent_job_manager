"""Identifier helper tests."""

from __future__ import annotations

import builtins

from src.infra.identity.identifier import new_id


def test_new_id_returns_non_empty_string_with_ulid_available() -> None:
    value = new_id()

    assert isinstance(value, str)
    assert value


def test_new_id_falls_back_to_uuid_when_ulid_is_unavailable(monkeypatch) -> None:
    original_import = builtins.__import__

    def fake_import(
        name: str,
        globals_: dict[str, object] | None = None,
        locals_: dict[str, object] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        if name == "ulid":
            raise ImportError("ulid unavailable")
        return original_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    value = new_id()

    assert isinstance(value, str)
    assert value
    assert len(value) == 32
