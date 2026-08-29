"""A second conftest layer, visible only inside this directory.

The fixtures below print a line every time their body runs, so a run with
`-s` shows exactly how often each scope is created. That is the whole demo:
scope is not documentation, it is an observable number of executions.
"""

import pytest


@pytest.fixture(scope="session")
def session_scoped():
    """Built once for the entire pytest run, however many tests ask for it."""
    print("\n    [session] body ran")
    yield "session-value"
    print("\n    [session] teardown ran")


@pytest.fixture(scope="module")
def module_scoped():
    """Built once per test module that asks for it."""
    print("\n    [module ] body ran")
    yield "module-value"
    print("\n    [module ] teardown ran")


@pytest.fixture(scope="function")
def function_scoped():
    """Built again for every single test — the default, and the safe default."""
    print("\n    [funct  ] body ran")
    yield "function-value"
    print("\n    [funct  ] teardown ran")
