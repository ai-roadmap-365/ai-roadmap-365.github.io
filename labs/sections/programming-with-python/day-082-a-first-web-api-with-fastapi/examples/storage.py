"""Storage for the bookmarks API — a Protocol and two implementations.

Day 074 argued that anything crossing a boundary should arrive as an
argument rather than be reached for. This file is that argument applied to
persistence, and the API module never names either class: it asks for a
``Storage`` and FastAPI's ``Depends`` hands one over.

``Storage`` is a ``typing.Protocol`` (Day 075). Neither implementation
inherits from it and neither needs to register anywhere; they satisfy it by
having the right methods with the right signatures. That is what lets the
test suite hand the application an ``InMemoryStorage`` while production runs
``JsonFileStorage``, with no shared base class and no flag inside the
handlers saying "if testing".

Nothing here opens a socket. ``JsonFileStorage`` writes one JSON file;
``InMemoryStorage`` writes nothing at all.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from models import StoredBookmark


class Storage(Protocol):
    """The shape the API needs. Anything with these five methods fits."""

    def add(self, bookmark: StoredBookmark) -> None: ...

    def all(self) -> list[StoredBookmark]: ...

    def get(self, bookmark_id: str) -> StoredBookmark | None: ...

    def replace(self, bookmark: StoredBookmark) -> None: ...

    def delete(self, bookmark_id: str) -> bool: ...


class InMemoryStorage:
    """A dictionary with the Storage shape. What the tests inject.

    This is not a mock library object and nothing is patched. It is a real,
    small, correct implementation of the same contract — which is why tests
    written against it exercise the handlers honestly rather than exercising
    a stub of them.
    """

    def __init__(self, initial: list[StoredBookmark] | None = None) -> None:
        self._items: dict[str, StoredBookmark] = {b.id: b for b in (initial or [])}

    def add(self, bookmark: StoredBookmark) -> None:
        self._items[bookmark.id] = bookmark

    def all(self) -> list[StoredBookmark]:
        return list(self._items.values())

    def get(self, bookmark_id: str) -> StoredBookmark | None:
        return self._items.get(bookmark_id)

    def replace(self, bookmark: StoredBookmark) -> None:
        self._items[bookmark.id] = bookmark

    def delete(self, bookmark_id: str) -> bool:
        return self._items.pop(bookmark_id, None) is not None


class JsonFileStorage:
    """The real one: a JSON file on disk, read and rewritten on every call.

    Rewriting the whole file per call is fine for a few hundred bookmarks and
    wrong for a million; Week 13 replaces it with a database. What matters
    today is that this class is the only thing in the lab that touches the
    filesystem, and the API never mentions it by name.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def _read(self) -> dict[str, StoredBookmark]:
        if not self.path.exists():
            return {}
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return {item["id"]: StoredBookmark.model_validate(item) for item in raw}

    def _write(self, items: dict[str, StoredBookmark]) -> None:
        payload = [json.loads(b.model_dump_json()) for b in items.values()]
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def add(self, bookmark: StoredBookmark) -> None:
        items = self._read()
        items[bookmark.id] = bookmark
        self._write(items)

    def all(self) -> list[StoredBookmark]:
        return list(self._read().values())

    def get(self, bookmark_id: str) -> StoredBookmark | None:
        return self._read().get(bookmark_id)

    def replace(self, bookmark: StoredBookmark) -> None:
        items = self._read()
        items[bookmark.id] = bookmark
        self._write(items)

    def delete(self, bookmark_id: str) -> bool:
        items = self._read()
        if items.pop(bookmark_id, None) is None:
            return False
        self._write(items)
        return True
