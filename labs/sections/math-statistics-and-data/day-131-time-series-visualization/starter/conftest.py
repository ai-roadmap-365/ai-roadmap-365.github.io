"""Shared fixtures and headless matplotlib setup.

pytest finds this file by itself -- nothing imports it. `matplotlib.use`
must run before `pyplot` is imported anywhere, which is why it happens
here, first, before the `data` import below pulls in pandas. Every
fixture returns a FRESH copy of its table so one test's accidental
mutation can never leak into the next test, and every test that opens a
Figure is responsible for `plt.close()`-ing it -- `_close_all_figures`
below is a backstop, not a substitute.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from data import (
    build_aliasing_signal,
    build_daily_1to90,
    build_full_series,
    build_gapped_series,
    build_hourly_utc,
    build_linear_growth_series,
    build_many_series,
    build_pct_growth_series,
    build_series_with_a_missing_row,
    build_series_with_an_explicit_nan,
    build_single_peak_series,
    build_two_year_daily,
)


@pytest.fixture
def gapped_series():
    return build_gapped_series()


@pytest.fixture
def daily_1to90():
    return build_daily_1to90()


@pytest.fixture
def aliasing_signal():
    return build_aliasing_signal()


@pytest.fixture
def single_peak_series():
    return build_single_peak_series()


@pytest.fixture
def full_series():
    return build_full_series()


@pytest.fixture
def series_with_a_missing_row():
    return build_series_with_a_missing_row()


@pytest.fixture
def series_with_an_explicit_nan():
    return build_series_with_an_explicit_nan()


@pytest.fixture
def pct_growth_series():
    return build_pct_growth_series()


@pytest.fixture
def linear_growth_series():
    return build_linear_growth_series()


@pytest.fixture
def two_year_daily():
    return build_two_year_daily()


@pytest.fixture
def many_series():
    return build_many_series()


@pytest.fixture
def hourly_utc():
    def _build(start, end):
        return build_hourly_utc(start, end)

    return _build


@pytest.fixture(autouse=True)
def _close_all_figures():
    yield
    plt.close("all")
