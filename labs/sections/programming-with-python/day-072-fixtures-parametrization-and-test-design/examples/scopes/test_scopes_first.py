"""Three tests, each requesting all three scopes. Run this with -s to watch."""


def test_first(session_scoped, module_scoped, function_scoped):
    assert (session_scoped, module_scoped, function_scoped) == (
        "session-value",
        "module-value",
        "function-value",
    )


def test_second(session_scoped, module_scoped, function_scoped):
    assert session_scoped == "session-value"


def test_third(session_scoped, module_scoped, function_scoped):
    assert function_scoped == "function-value"
