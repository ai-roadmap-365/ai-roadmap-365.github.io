"""Test configuration for the starter exercises.

Two jobs, both small.

1. Put the lab's `examples/` directory on `sys.path`, so `queries.py` and the
   tests can import `models`, `library` and `counting` without any packaging
   ceremony. Those three modules are shared infrastructure — the domain, the
   fixed seed data and the statement counter — and copying them into
   `starter/` would mean two versions to keep in step.

2. Arm a guard that turns any attempt to open a network socket into a loud
   failure. Installing SQLAlchemy needs the network once. Nothing in this lab
   does, and a test that quietly reaches the internet is a test that fails in
   a tunnel for reasons nobody can reproduce.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_DIR / "examples"))
sys.path.insert(0, str(Path(__file__).resolve().parent))


class NetworkAccessAttempted(RuntimeError):
    """Raised if anything in this lab tries to open a connection."""


def _refuse(*args, **kwargs):
    raise NetworkAccessAttempted(
        "This lab runs entirely offline against in-memory and temporary SQLite "
        "databases. Something tried to open a network connection."
    )


socket.socket.connect = _refuse
socket.create_connection = _refuse
