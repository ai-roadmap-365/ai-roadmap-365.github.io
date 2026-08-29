"""Five tests that fail on purpose, so you can read a failure report.

    pytest examples/failure-demo

Every failure here is deliberate. The point is the shape of the report: what
pytest prints when a bare `assert` is false, and how much of the comparison it
recovers for you. Compare the same five failures under `--tb=short`, `-q`,
and `-x`.
"""

import pytest


def add(a, b):
    """Deliberately wrong by one, so the arithmetic assertion fails."""
    return a + b + 1


def test_a_simple_number_comparison():
    assert add(1, 2) == 3


def test_a_list_comparison():
    expected = ["the", "cat", "sat", "on", "the", "mat"]
    actual = ["the", "cat", "sat", "on", "a", "mat"]
    assert actual == expected


def test_a_dict_comparison():
    expected = {"words": 12, "unique": 9, "mean_length": 3.83}
    actual = {"words": 12, "unique": 8, "mean_length": 3.83}
    assert actual == expected


def test_a_string_comparison():
    assert "reading time: 4 minutes" == "reading time: 3 minutes"


def test_an_exception_that_was_not_raised():
    with pytest.raises(ValueError):
        int("42")
