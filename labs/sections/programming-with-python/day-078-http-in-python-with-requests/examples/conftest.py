"""Fixtures for the example suite: one local server for the whole session.

The server is started once, on an ephemeral port, and shut down when the
last test finishes. Starting it per test would be correct but wasteful; the
tests that need a clean counter call `/control/reset` themselves.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from demo_server import CountingServer, base_url, running_server  # noqa: E402


@pytest.fixture(scope="session")
def server() -> Iterator[CountingServer]:
    with running_server() as srv:
        yield srv


@pytest.fixture(scope="session")
def base(server: CountingServer) -> str:
    """The address the local test server actually bound to, this run."""
    return base_url(server)
