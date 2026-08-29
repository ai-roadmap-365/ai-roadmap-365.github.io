"""The three built-in fixtures worth knowing on day one.

You never define these. pytest ships them, and they are available by name in
any test, in any file, with no `conftest.py` involved. `pytest --fixtures`
lists every fixture visible to a given file, built-ins included.
"""

import os

from practice_store import PracticeStore, Session


def config_dir():
    """Ordinary application code that reads the environment."""
    return os.environ.get("PRACTICE_HOME", "/etc/practice")


def describe(store):
    """Ordinary application code that prints."""
    print(f"{len(store.all())} sessions, {store.total_minutes()} minutes")


def test_tmp_path_is_a_fresh_empty_directory(tmp_path):
    """`tmp_path` is a pathlib.Path to a directory nobody else is using."""
    assert list(tmp_path.iterdir()) == []
    store = PracticeStore(tmp_path / "practice.csv").initialise()
    assert store.path.exists()
    assert store.all() == []


def test_capsys_captures_what_was_printed(capsys, loaded_store):
    """`capsys` lets you assert on output without changing the code to return it."""
    describe(loaded_store)
    captured = capsys.readouterr()
    assert captured.out == "3 sessions, 135 minutes\n"
    assert captured.err == ""


def test_monkeypatch_sets_an_environment_variable(monkeypatch, tmp_path):
    """`monkeypatch` changes the world for one test and undoes it afterwards."""
    monkeypatch.setenv("PRACTICE_HOME", str(tmp_path))
    assert config_dir() == str(tmp_path)


def test_the_environment_is_back_to_normal():
    """Proof that the previous test's change did not survive it.

    This is the whole reason to use `monkeypatch` instead of assigning to
    `os.environ` yourself: the undo is not something you have to remember.
    """
    assert config_dir() == "/etc/practice"


def test_a_fixture_and_a_helper_can_coexist(empty_store):
    """A helper function is fine, and often better than a fixture.

    `three_sessions` below is used by exactly one test. Making it a fixture
    would put its definition in another file and its invocation in a parameter
    name — indirection with nothing to show for it.
    """

    def three_sessions(first_number):
        from datetime import date

        return [
            Session(f"S-{first_number + n:03d}", date(2026, 8, n), "pytest", n * 10)
            for n in (1, 2, 3)
        ]

    for session in three_sessions(200):
        empty_store.add(session)
    assert empty_store.total_minutes() == 60
