"""Your exercises for Day 130 -- "Pictures of a Distribution".

Nine exercises. Every test below currently calls `pytest.skip(...)` --
replace the skip with real assertions and delete the skip line. Read
`00_brief.md` for the exercise-by-exercise explanation, and `data.py` for
what each fixture actually contains.

Check yourself at any point:

    pytest starter -v

The reference answer key lives in `examples/test_distributions.py` --
read it AFTER you have tried, never before.
"""

import numpy as np
import pandas as pd
import pytest
import seaborn as sns


def count_local_maxima(counts) -> int:
    """A bin is a local maximum if it is strictly taller than its only
    neighbour (an edge bin) or both neighbours (an interior bin)."""
    counts = list(counts)
    n = len(counts)
    maxima = 0
    for i in range(n):
        left = counts[i - 1] if i > 0 else None
        right = counts[i + 1] if i < n - 1 else None
        if left is None and (right is None or counts[i] > right):
            maxima += 1
        elif right is None and counts[i] > left:
            maxima += 1
        elif left is not None and right is not None and counts[i] > left and counts[i] > right:
            maxima += 1
    return maxima


def count_curve_modes(y) -> int:
    """Local maxima of a continuous curve (a KDE line), interior points only."""
    y = list(y)
    return sum(
        1 for i in range(1, len(y) - 1) if y[i] > y[i - 1] and y[i] > y[i + 1]
    )


# --------------------------------------------------------------------------
# Exercise 1 -- bin width changes the story.
# --------------------------------------------------------------------------


def test_01_bin_width_changes_the_story(bimodal_sample):
    pytest.skip(
        "Histogram bimodal_sample at 5 and 100 bins, count local maxima at each, "
        "assert 5 bins gives 1 mode and 100 bins gives more than 10; then assert "
        "numpy.histogram_bin_edges(..., bins='fd') recovers 2 modes"
    )


# --------------------------------------------------------------------------
# Exercise 2 -- the three rules disagree.
# --------------------------------------------------------------------------


def test_02_the_three_rules_disagree(skewed_sample):
    pytest.skip(
        "Get bin counts from 'sturges', 'scott' and 'fd' via "
        "numpy.histogram_bin_edges(skewed_sample, bins=...) and assert all three differ"
    )


# --------------------------------------------------------------------------
# Exercise 3 -- KDE bandwidth.
# --------------------------------------------------------------------------


def test_03_kde_bandwidth(bimodal_sample):
    pytest.skip(
        "Draw sns.kdeplot with bw_adjust=1.0 and bw_adjust=3.0, read each line's y data "
        "off ax.lines[0].get_data(), count_curve_modes on each, assert 2 modes then 1"
    )


# --------------------------------------------------------------------------
# Exercise 4 -- the KDE boundary problem.
# --------------------------------------------------------------------------


def test_04_kde_boundary_problem(positive_sample):
    pytest.skip(
        "Draw the default KDE of positive_sample, confirm x extends below zero, "
        "integrate y[x<0] with numpy.trapezoid, assert the fraction of total mass "
        "below zero is more than 0.03"
    )


# --------------------------------------------------------------------------
# Exercise 5 -- the boxplot's blind spot. The day's centrepiece.
# --------------------------------------------------------------------------


def test_05_boxplot_blind_spot(quartile_pair, quartile_targets):
    pytest.skip(
        "Compute five-number summaries of both samples in quartile_pair with "
        "numpy.percentile(x, [0,25,50,75,100]); assert both are within 0.3 of "
        "quartile_targets (and of each other); histogram both at 15 bins and assert "
        "the bimodal one shows 2 modes while the unimodal one shows 1"
    )


# --------------------------------------------------------------------------
# Exercise 6 -- ECDF is parameter-free.
# --------------------------------------------------------------------------


def test_06_ecdf_is_parameter_free(ecdf_sample):
    pytest.skip(
        "Draw sns.ecdfplot, read x,y off ax.lines[0].get_data(), assert every sorted "
        "observation appears in x, find where y first reaches 0.5 with "
        "numpy.searchsorted and assert that x value equals numpy.median(ecdf_sample) "
        "to within 1e-9"
    )


# --------------------------------------------------------------------------
# Exercise 7 -- overplotting.
# --------------------------------------------------------------------------


def test_07_overplotting(overplot_cloud):
    pytest.skip(
        "Render overplot_cloud as a small scatter (figsize=(3,3), dpi=72), transform "
        "data coordinates to pixel space with ax.transData.transform, round, count "
        "distinct pixel pairs with a set, assert under half the point count; draw a "
        "hexbin of the same data and assert its densest bin holds more than 20 points"
    )


# --------------------------------------------------------------------------
# Exercise 8 -- correlation without shape.
# --------------------------------------------------------------------------


def test_08_correlation_without_shape(quadratic_data):
    pytest.skip(
        "Compute Pearson correlation with pandas' .corr() and assert it is near zero; "
        "compute Spearman yourself as the Pearson correlation of .rank()-ed columns "
        "(scipy is not installed, so method='spearman' will raise) and assert that is "
        "also near zero; fit numpy.polyfit(x, y, 2), compute R^2 by hand, assert it is "
        "above 0.95"
    )


# --------------------------------------------------------------------------
# Exercise 9 -- jitter is distortion.
# --------------------------------------------------------------------------


def test_09_jitter_is_distortion(discrete_sample):
    pytest.skip(
        "Build a jittered copy with numpy.random.default_rng(...).uniform(-w, w, n) "
        "added to discrete_sample, assert every shift is at most w, and assert "
        "discrete_sample itself is unchanged"
    )
