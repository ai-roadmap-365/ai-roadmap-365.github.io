"""Provided for you, complete. Do not edit — this is the harness, not the work.

It puts the lab's `examples/` directory on the import path (so you can import
`demo_server` and `fake_session`), and it starts ONE local HTTP server for the
whole test session on an ephemeral port on 127.0.0.1.

Read `examples/demo_server.py` once before you start. It is the thing you are
writing a client against, it is about two hundred lines of standard library,
and knowing what the server does makes every exercise below easier.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

import pytest

LAB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_DIR / "examples"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from demo_server import CountingServer, base_url, running_server  # noqa: E402


@pytest.fixture(scope="session")
def server() -> Iterator[CountingServer]:
    """The local test server. Started once, shut down when the run ends."""
    with running_server() as srv:
        yield srv


@pytest.fixture(scope="session")
def base(server: CountingServer) -> str:
    """The address it actually bound to this run, e.g. http://127.0.0.1:51234"""
    return base_url(server)
