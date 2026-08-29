"""Setup for the starter suite: import path, a clean slate, and a net guard.

The `clean_slate` fixture exists only because `app.py` currently keeps its
bookmarks in a module-level dictionary. Reaching into another module to
reset a global before every test is exactly the smell Day 074 described,
and Exercise 7 removes the need for it: once storage is injected, each test
constructs its own and this fixture can be deleted.

The `no_network` guard is the same one the reference suite uses. It makes
the week's network rule mechanical rather than a promise.
"""

from __future__ import annotations

import socket
import sys
import warnings
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

warnings.filterwarnings(
    "ignore", message="Using `httpx` with `starlette.testclient` is deprecated"
)


class NetworkAccessAttempted(RuntimeError):
    """Raised if anything in the test run tries to open a connection."""


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(self: socket.socket, address: object) -> None:
        raise NetworkAccessAttempted(f"a test tried to connect to {address!r}")

    def blocked_create(address: object, *a: object, **k: object) -> None:
        raise NetworkAccessAttempted(f"a test tried to connect to {address!r}")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked_create)


@pytest.fixture(autouse=True)
def clean_slate() -> None:
    import app

    app.BOOKMARKS.clear()
