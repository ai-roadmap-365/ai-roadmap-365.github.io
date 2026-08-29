"""Shared fixtures for every test module in this directory and below.

`conftest.py` is not imported by anything. pytest finds it by *location*: when
it collects a test file it walks up the directory tree collecting every
`conftest.py` it passes, and the fixtures defined in them become available to
that file by name. A fixture defined here is visible to `test_sessions.py`,
to `test_store.py`, and to everything under `scopes/`. A fixture defined in
`scopes/conftest.py` is visible only inside `scopes/`.
"""

from datetime import date

import pytest

from practice_store import PracticeStore, Session

# ---------------------------------------------------------------------------
# Data. Frozen dataclasses cannot be mutated, so one tuple of them is safe to
# share across the whole run — which is why this fixture may be session-scoped
# without any risk of one test corrupting another's data.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def sample_sessions():
    """Three immutable sessions across two topics: 45 + 30 + 60 = 135 minutes."""
    return (
        Session("S-001", date(2026, 5, 4), "python", 45),
        Session("S-002", date(2026, 5, 5), "linear-algebra", 30),
        Session("S-003", date(2026, 5, 6), "python", 60),
    )


# ---------------------------------------------------------------------------
# Files and stores. These are function-scoped on purpose: a store is mutable
# state on disk, and sharing mutable state between tests is how a suite starts
# passing or failing depending on the order it runs in.
# ---------------------------------------------------------------------------


@pytest.fixture
def store_path(tmp_path):
    """A path inside pytest's own per-test temporary directory.

    `tmp_path` is a built-in fixture. pytest creates a fresh directory for
    every test that asks for one, hands it over as a `pathlib.Path`, and keeps
    the last few runs on disk so a failure can be inspected afterwards.
    """
    return tmp_path / "practice.csv"


@pytest.fixture
def empty_store(store_path):
    """An initialised store with a header row and no sessions."""
    return PracticeStore(store_path).initialise()


@pytest.fixture
def loaded_store(empty_store, sample_sessions):
    """A store holding the three sample sessions.

    Note what is happening: a fixture requests two other fixtures by name, and
    pytest builds the whole chain before the test body runs. This is the
    dependency graph that replaces a page of copy-pasted setup.
    """
    for session in sample_sessions:
        empty_store.add(session)
    return empty_store


@pytest.fixture
def audited_store(loaded_store):
    """A loaded store that reports what it looked like on the way out.

    Everything before `yield` is setup; everything after it is teardown, and
    pytest runs the teardown whether the test passed, failed, or raised. That
    guarantee is the reason `yield` fixtures replaced hand-written cleanup.
    """
    before = len(loaded_store.all())
    yield loaded_store
    after = len(loaded_store.all())
    print(f"[audit] sessions before: {before}, after: {after}")
