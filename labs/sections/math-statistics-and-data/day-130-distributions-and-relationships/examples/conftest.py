"""Shared fixtures and headless matplotlib setup.

pytest finds this file by itself -- nothing imports it. `matplotlib.use`
must run before `pyplot` is imported anywhere, which is why it happens
here, first. Every test that opens a Figure is responsible for its own
`plt.close()`; `_close_all_figures` below is a backstop, not a substitute.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from data import (
    bimodal_for_binning,
    discrete_for_jitter,
    matched_quartile_pair,
    normal_for_ecdf,
    overplotted_cloud,
    positive_for_kde_boundary,
    quadratic_relationship,
    skewed_for_bin_rules,
    target_five_number_summary,
)


@pytest.fixture
def bimodal_sample():
    return bimodal_for_binning()


@pytest.fixture
def skewed_sample():
    return skewed_for_bin_rules()


@pytest.fixture
def positive_sample():
    return positive_for_kde_boundary()


@pytest.fixture
def quartile_pair():
    return matched_quartile_pair()


@pytest.fixture
def quartile_targets():
    return target_five_number_summary()


@pytest.fixture
def ecdf_sample():
    return normal_for_ecdf()


@pytest.fixture
def overplot_cloud():
    return overplotted_cloud()


@pytest.fixture
def quadratic_data():
    return quadratic_relationship()


@pytest.fixture
def discrete_sample():
    return discrete_for_jitter()


@pytest.fixture(autouse=True)
def _close_all_figures():
    yield
    plt.close("all")
