"""Shared fixtures and headless matplotlib setup.

pytest finds this file by itself -- nothing imports it. `matplotlib.use`
must run before `pyplot` is imported anywhere, which is why it happens
here, first, before the `data` import below pulls in pandas (and,
transitively, nothing that touches matplotlib yet). Every fixture returns
a FRESH copy of its table so one test's accidental mutation can never
leak into the next test, and every test that opens a Figure is
responsible for `plt.close()`-ing it -- `_close_all_figures` below is a
backstop, not a substitute.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from data import build_long_revenue, build_team_scores, build_wide_revenue


@pytest.fixture
def team_scores():
    return build_team_scores()


@pytest.fixture
def wide_revenue():
    return build_wide_revenue()


@pytest.fixture
def long_revenue():
    return build_long_revenue()


@pytest.fixture(autouse=True)
def _close_all_figures():
    yield
    plt.close("all")
