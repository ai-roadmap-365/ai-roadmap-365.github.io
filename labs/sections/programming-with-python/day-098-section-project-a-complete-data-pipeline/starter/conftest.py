"""Test wiring: import paths and one fixture server for the whole session."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

LAB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB / "starter"))
sys.path.insert(0, str(LAB / "examples"))

import fixture_server  # noqa: E402

TOKEN = "demo-token-value"

# The test harness runs this same suite twice: once against the skeleton the
# learner receives, and once against examples/stages_solved.py, so the nine
# exercises are proved achievable rather than merely asserted to be.
if os.environ.get("DAY098_SOLUTION"):
    sys.modules["stages"] = importlib.import_module("stages_solved")


@pytest.fixture(scope="session")
def base_url() -> str:
    """A fixture server on 127.0.0.1, on a port the kernel picks.

    Session-scoped, so bravo's "fail twice then succeed" counter is shared by
    every test in the run. Tests that care about it call
    ``fixture_server.reset_flaky_counter()`` first.
    """
    server, port = fixture_server.start_background_server(token=TOKEN)
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


@pytest.fixture
def token() -> str:
    return TOKEN
