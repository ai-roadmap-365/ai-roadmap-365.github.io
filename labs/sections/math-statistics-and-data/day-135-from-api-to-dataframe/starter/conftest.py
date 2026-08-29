"""Provided for you, complete. Do not edit -- this is the harness, not the work.

Puts the lab's `examples/` directory on the import path (so you can import
`api_server`), and starts ONE local HTTP server for the whole test session
on an ephemeral port on 127.0.0.1.

Read `examples/api_server.py` once before you start. It is the API you are
writing an ingestion pipeline against, and knowing its dataset -- seven
customers, `loyalty_tier` first appearing on the third page -- makes every
exercise below easier.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

import pytest

LAB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_DIR / "examples"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api_server import CountingServer, base_url, running_server  # noqa: E402


@pytest.fixture(scope="session")
def server() -> Iterator[CountingServer]:
    with running_server() as srv:
        yield srv


@pytest.fixture(scope="session")
def base(server: CountingServer) -> str:
    return base_url(server)
