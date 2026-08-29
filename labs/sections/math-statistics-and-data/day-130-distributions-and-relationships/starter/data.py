"""The samples every exercise in this lab is built from.

Every table here is generated from a fixed `numpy.random.default_rng` seed,
never loaded from a file and never re-seeded per test -- so the same call
produces the same numbers on any machine with the same NumPy version, and a
reader can reproduce every asserted value by running the function directly.

Two constructed pairs carry the lab's two centrepiece demonstrations:

`bimodal_for_binning()` -- exercise 1 and exercise 3. Two normal clusters
close enough together that a coarse 5-bin histogram merges them into one
hump, a well-chosen bin count (Freedman-Diaconis lands on 13 bins here)
recovers two, and 100 bins turns the same 500 points into visual noise.
The same sample is reused for the KDE bandwidth demonstration in
exercise 3, because the story is identical: the bin width and the KDE
bandwidth are the same kind of decision.

`matched_quartile_pair()` -- exercise 5, the day's centrepiece. A bimodal
sample and a unimodal sample, built from two different piecewise-linear
quantile functions, engineered so their five-number summaries agree to
within 0.3 units on identical control points (min, Q1, median, Q3, max
all hand-picked as 10 / 28 / 40 / 52 / 70) while their interior shape is
completely different. A boxplot of either looks identical to the other;
a histogram does not.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# bimodal_for_binning -- exercises 1 and 3.
#
# Two normal clusters, means 40 and 54 (gap 14), sd 8 each, 250 points per
# cluster. Close enough that 5 wide bins wash the gap out into one hump;
# Freedman-Diaconis (13 bins on this draw) recovers two; 100 bins gives
# nothing but sampling noise per bin.
# --------------------------------------------------------------------------


def bimodal_for_binning() -> np.ndarray:
    rng = np.random.default_rng(42)
    low_cluster = rng.normal(40, 8, 250)
    high_cluster = rng.normal(54, 8, 250)
    return np.concatenate([low_cluster, high_cluster])


# --------------------------------------------------------------------------
# skewed_for_bin_rules -- exercise 2. A right-skewed, strictly positive
# sample (log-normal) on which Sturges, Scott and Freedman-Diaconis
# genuinely disagree about the bin count.
# --------------------------------------------------------------------------


def skewed_for_bin_rules() -> np.ndarray:
    rng = np.random.default_rng(123)
    return rng.lognormal(mean=3.0, sigma=0.6, size=400)


# --------------------------------------------------------------------------
# positive_for_kde_boundary -- exercise 4. Strictly positive (an
# exponential), so any density a KDE places below zero is visibly wrong.
# --------------------------------------------------------------------------


def positive_for_kde_boundary() -> np.ndarray:
    rng = np.random.default_rng(9)
    return rng.exponential(scale=5.0, size=400)


# --------------------------------------------------------------------------
# matched_quartile_pair -- exercise 5, the boxplot's blind spot.
#
# Both samples are built from a piecewise-linear quantile function: a
# function from rank (0 to 1) to value, evaluated at 240 evenly spaced
# ranks. Both functions are pinned to pass through the same five control
# points -- (0, 10), (0.25, 28), (0.5, 40), (0.75, 52), (1.0, 70) -- so
# both samples' five-number summaries land within about 0.3 units of
# those targets. Between the control points the two functions diverge
# completely: `_unimodal_quantile` uses a smooth convex curve on each
# side of the median (density highest at the centre, lowest at the
# tails -- one hump); `_bimodal_quantile` inserts extra control points
# that pack a large fraction of the probability mass into two narrow
# bands just above Q1 and just below Q3, with a sparse valley at the
# median and sparse far tails (two humps, a dip in the middle).
# --------------------------------------------------------------------------

_TARGET_MIN, _TARGET_Q1, _TARGET_MED, _TARGET_Q3, _TARGET_MAX = (
    10.0,
    28.0,
    40.0,
    52.0,
    70.0,
)


def _unimodal_quantile(ranks: np.ndarray) -> np.ndarray:
    med = _TARGET_MED
    d3, dmax = _TARGET_Q3 - med, _TARGET_MAX - med
    d1, dmin = med - _TARGET_Q1, med - _TARGET_MIN
    coeff_matrix = np.array([[0.5, 0.25], [1.0, 1.0]])
    a_right, b_right = np.linalg.solve(coeff_matrix, np.array([d3, dmax]))
    a_left, b_left = np.linalg.solve(coeff_matrix, np.array([d1, dmin]))

    out = np.empty_like(ranks)
    on_right = ranks >= 0.5
    u_right = (ranks[on_right] - 0.5) / 0.5
    out[on_right] = med + a_right * u_right + b_right * u_right**2
    u_left = (0.5 - ranks[~on_right]) / 0.5
    out[~on_right] = med - (a_left * u_left + b_left * u_left**2)
    return out


def _bimodal_quantile(ranks: np.ndarray) -> np.ndarray:
    control_ranks = [0.0, 0.15, 0.25, 0.40, 0.50, 0.60, 0.75, 0.85, 1.00]
    control_values = [
        _TARGET_MIN,
        25.0,
        _TARGET_Q1,
        31.0,
        _TARGET_MED,
        49.0,
        _TARGET_Q3,
        55.0,
        _TARGET_MAX,
    ]
    return np.interp(ranks, control_ranks, control_values)


def matched_quartile_pair(n: int = 240) -> tuple[np.ndarray, np.ndarray]:
    ranks = (np.arange(n) + 0.5) / n
    unimodal = _unimodal_quantile(ranks)
    bimodal = _bimodal_quantile(ranks)
    return bimodal, unimodal


def target_five_number_summary() -> np.ndarray:
    """The five control-point values both samples in the matched pair were built to hit."""
    return np.array(
        [_TARGET_MIN, _TARGET_Q1, _TARGET_MED, _TARGET_Q3, _TARGET_MAX]
    )


# --------------------------------------------------------------------------
# normal_for_ecdf -- exercise 6. Odd sample size on purpose: with an odd n
# the median is a single real observation rather than an average of two,
# so the ECDF step and `numpy.median` can be compared for an exact match.
# --------------------------------------------------------------------------


def normal_for_ecdf() -> np.ndarray:
    rng = np.random.default_rng(3)
    return rng.normal(0, 1, 301)


# --------------------------------------------------------------------------
# overplotted_cloud -- exercise 7. 20,000 points from a standard normal in
# both dimensions, deliberately plotted small (3x3 inches at 72 dpi) so a
# meaningful fraction of them land on the very same screen pixel.
# --------------------------------------------------------------------------


def overplotted_cloud(n: int = 20_000) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(11)
    x = rng.normal(0, 1, n)
    y = rng.normal(0, 1, n)
    return x, y


# --------------------------------------------------------------------------
# quadratic_relationship -- exercise 8. x symmetric around 0, y = x^2 plus
# noise: a strong, deterministic relationship with almost no LINEAR
# component (Pearson) and, because the parabola is symmetric, almost no
# MONOTONIC component either (Spearman) -- only fitting or plotting the
# actual shape reveals it. See the lesson and FIELDS.md for why this is a
# sharper example than one where Spearman alone would have caught it.
# --------------------------------------------------------------------------


def quadratic_relationship(n: int = 300) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(5)
    x = rng.uniform(-10, 10, n)
    y = x**2 + rng.normal(0, 3, n)
    return x, y


# --------------------------------------------------------------------------
# discrete_for_jitter -- exercise 9. Integers 1..5, as a five-point Likert
# scale might arrive.
# --------------------------------------------------------------------------


def discrete_for_jitter(n: int = 200) -> np.ndarray:
    rng = np.random.default_rng(17)
    return rng.integers(1, 6, n)
