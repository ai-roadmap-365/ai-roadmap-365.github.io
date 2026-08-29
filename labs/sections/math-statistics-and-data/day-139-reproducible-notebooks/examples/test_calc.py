"""Ordinary tests for the module half of the notebook/module split.

No kernel, no notebook, no nbclient anywhere in this file -- which is
the point exercise 8 makes: this is what it looks like when reused logic
lives somewhere pytest can reach it directly.
"""

from calc import clean_mean


def test_clean_mean_drops_none():
    assert clean_mean([1, None, 3]) == 2.0


def test_clean_mean_all_present():
    assert clean_mean([2, 4, 6]) == 4.0


def test_clean_mean_raises_on_empty():
    try:
        clean_mean([None, None])
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for an all-None input")
