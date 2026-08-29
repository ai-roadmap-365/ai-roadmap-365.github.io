"""Make the tool importable in-process.

Which copy is tested is chosen by the NOTES_DIR environment variable, so the
same suite can be pointed at examples/ (the reference) or at starter/ (your
work) without editing a line. `bash tests/run_tests.sh` sets it for you.

Importing the module rather than launching a process is the whole point of
the in-process tests: they exercise `parse_args(argv)` with an explicit list
and `main(argv, streams)` with io.StringIO streams, which is only possible
because neither function reaches for sys.argv or sys.stdout on its own.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

LAB_DIR = Path(__file__).resolve().parent.parent
NOTES_DIR = LAB_DIR / os.environ.get("NOTES_DIR", "examples")

sys.path.insert(0, str(NOTES_DIR))


@pytest.fixture(scope="session")
def notes_module():
    """The module under test, imported once per session."""
    import notes

    return notes


@pytest.fixture()
def store(tmp_path) -> Path:
    """A fresh, empty store path inside pytest's own temporary directory."""
    return tmp_path / "notes.json"
