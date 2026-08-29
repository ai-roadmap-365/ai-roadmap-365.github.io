"""A second module in the same directory, which is what makes the demo work.

The session fixture does NOT run again here — it was already built. The module
fixture DOES, because this is a different module. And the deliberately failing
test proves the thing you most need to trust about `yield` fixtures: teardown
runs anyway.
"""

import pytest


def test_session_scope_is_not_rebuilt(session_scoped, module_scoped):
    assert session_scoped == "session-value"


@pytest.mark.xfail(strict=True, reason="fails on purpose, to show teardown still runs")
def test_teardown_runs_even_when_the_test_fails(function_scoped):
    assert function_scoped == "this is not the value, so this test fails"
