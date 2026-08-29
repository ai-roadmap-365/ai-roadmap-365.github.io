"""Shared pytest setup for the reference suite.

Two jobs:

1. Put this directory on ``sys.path`` so ``import api`` works no matter
   where pytest was started from.
2. Prove the week's network rule mechanically. An autouse fixture replaces
   the two functions that actually reach the network — ``socket.socket``'s
   ``connect`` and ``socket.create_connection`` — with functions that raise.
   If any test in this suite tried to open a connection to anything, it
   would fail with ``NetworkAccessAttempted`` naming the address. Nothing
   here has to be trusted: the guard is armed for every test, and the suite
   is green, so nothing connected.

``TestClient`` passes through this guard untouched, because it never opens a
connection. It hands the request object straight to the ASGI application in
the same process.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))


class NetworkAccessAttempted(RuntimeError):
    """Raised if anything in the test run tries to open a connection."""


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Arm the network guard for every test in this directory."""

    def blocked_connect(self: socket.socket, address: object) -> None:
        raise NetworkAccessAttempted(f"a test tried to connect to {address!r}")

    def blocked_create_connection(address: object, *args: object, **kwargs: object) -> None:
        raise NetworkAccessAttempted(f"a test tried to connect to {address!r}")

    monkeypatch.setattr(socket.socket, "connect", blocked_connect)
    monkeypatch.setattr(socket, "create_connection", blocked_create_connection)
