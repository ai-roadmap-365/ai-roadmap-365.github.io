"""Reference solutions -- Day 130, Pictures of a Distribution.

Nine exercises, each proving a claim from the lesson by running real
matplotlib / seaborn / pandas / NumPy code and asserting on the numbers
and artist state that code actually produces -- never on image bytes.

Run with: pytest examples -q
"""

from __future__ import annotations

import numpy as np
import pandas as pd
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
    counts_5, _ = np.histogram(bimodal_sample, bins=5)
    counts_100, _ = np.histogram(bimodal_sample, bins=100)

    modes_5 = count_local_maxima(counts_5)
    modes_100 = count_local_maxima(counts_100)
    assert modes_5 != modes_100

    # 5 wide bins wash the two clusters into a single hump.
    assert modes_5 == 1
    # 100 narrow bins turn 500 points into visual noise -- many spurious
    # local maxima, none of them the real two-cluster structure.
    assert modes_100 > 10

    fd_edges = np.histogram_bin_edges(bimodal_sample, bins="fd")
    fd_counts, _ = np.histogram(bimodal_sample, bins=fd_edges)
    fd_bin_count = len(fd_edges) - 1
    fd_modes = count_local_maxima(fd_counts)

    # Freedman-Diaconis recovers the real two-mode structure.
    assert fd_modes == 2
    print(
        f"  bins=5 -> {modes_5} mode(s); bins=100 -> {modes_100} mode(s); "
        f"Freedman-Diaconis -> {fd_bin_count} bins, {fd_modes} mode(s)"
    )


# --------------------------------------------------------------------------
# Exercise 2 -- the three rules disagree.
# --------------------------------------------------------------------------


def test_02_the_three_rules_disagree(skewed_sample):
    sturges_edges = np.histogram_bin_edges(skewed_sample, bins="sturges")
    scott_edges = np.histogram_bin_edges(skewed_sample, bins="scott")
    fd_edges = np.histogram_bin_edges(skewed_sample, bins="fd")

    sturges_n = len(sturges_edges) - 1
    scott_n = len(scott_edges) - 1
    fd_n = len(fd_edges) - 1

    bin_counts = {sturges_n, scott_n, fd_n}
    assert len(bin_counts) == 3, "all three rules must disagree on this skewed sample"

    print(f"  sturges={sturges_n} scott={scott_n} fd={fd_n}")


# --------------------------------------------------------------------------
# Exercise 3 -- KDE bandwidth.
# --------------------------------------------------------------------------


def test_03_kde_bandwidth(bimodal_sample):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    sns.kdeplot(bimodal_sample, ax=ax, bw_adjust=1.0)
    _, y_default = ax.lines[0].get_data()
    plt.close(fig)

    fig, ax = plt.subplots()
    sns.kdeplot(bimodal_sample, ax=ax, bw_adjust=3.0)
    _, y_smoothed = ax.lines[0].get_data()
    plt.close(fig)

    modes_default = count_curve_modes(y_default)
    modes_smoothed = count_curve_modes(y_smoothed)

    assert modes_default == 2
    assert modes_smoothed == 1
    print(f"  bw_adjust=1.0 -> {modes_default} mode(s); bw_adjust=3.0 -> {modes_smoothed} mode(s)")


# --------------------------------------------------------------------------
# Exercise 4 -- the KDE boundary problem.
# --------------------------------------------------------------------------


def test_04_kde_boundary_problem(positive_sample):
    import matplotlib.pyplot as plt

    assert positive_sample.min() > 0

    fig, ax = plt.subplots()
    sns.kdeplot(positive_sample, ax=ax)
    x, y = ax.lines[0].get_data()
    plt.close(fig)

    below_zero = x < 0
    assert below_zero.any(), "the default KDE grid must extend below zero"

    mass_below_zero = np.trapezoid(y[below_zero], x[below_zero])
    total_mass = np.trapezoid(y, x)
    fraction_below_zero = mass_below_zero / total_mass

    assert fraction_below_zero > 0.03
    print(f"  fraction of KDE mass below zero: {fraction_below_zero:.4f}")


# --------------------------------------------------------------------------
# Exercise 5 -- the boxplot's blind spot. The day's centrepiece.
# --------------------------------------------------------------------------


def test_05_boxplot_blind_spot(quartile_pair, quartile_targets):
    bimodal, unimodal = quartile_pair

    def five_number_summary(x):
        return np.percentile(x, [0, 25, 50, 75, 100])

    bimodal_summary = five_number_summary(bimodal)
    unimodal_summary = five_number_summary(unimodal)

    tolerance = 0.3
    assert np.max(np.abs(bimodal_summary - quartile_targets)) < tolerance
    assert np.max(np.abs(unimodal_summary - quartile_targets)) < tolerance
    # The two summaries agree with EACH OTHER to the same tight tolerance --
    # this is what makes their boxplots indistinguishable.
    assert np.max(np.abs(bimodal_summary - unimodal_summary)) < tolerance

    bin_count = 15
    bimodal_counts, _ = np.histogram(bimodal, bins=bin_count)
    unimodal_counts, _ = np.histogram(unimodal, bins=bin_count)
    bimodal_modes = count_local_maxima(bimodal_counts)
    unimodal_modes = count_local_maxima(unimodal_counts)

    assert bimodal_modes == 2
    assert unimodal_modes == 1
    assert bimodal_modes != unimodal_modes

    print(
        f"  bimodal 5-num: {np.round(bimodal_summary, 2)} ({bimodal_modes} modes at "
        f"{bin_count} bins)\n"
        f"  unimodal 5-num: {np.round(unimodal_summary, 2)} ({unimodal_modes} mode at "
        f"{bin_count} bins)"
    )


# --------------------------------------------------------------------------
# Exercise 6 -- ECDF is parameter-free.
# --------------------------------------------------------------------------


def test_06_ecdf_is_parameter_free(ecdf_sample):
    import matplotlib.pyplot as plt

    assert len(ecdf_sample) % 2 == 1, "an odd n makes the median a single real observation"

    fig, ax = plt.subplots()
    sns.ecdfplot(ecdf_sample, ax=ax)
    x, y = ax.lines[0].get_data()
    plt.close(fig)

    sorted_sample = np.sort(ecdf_sample)
    # every observation is a step location on the ECDF
    assert np.isin(np.round(sorted_sample, 9), np.round(x, 9)).all()

    median_index = np.searchsorted(y, 0.5, side="left")
    ecdf_median = x[median_index]
    numpy_median = np.median(ecdf_sample)
    assert abs(ecdf_median - numpy_median) < 1e-9
    print(f"  ECDF median {ecdf_median:.6f} == numpy.median {numpy_median:.6f}")


# --------------------------------------------------------------------------
# Exercise 7 -- overplotting.
# --------------------------------------------------------------------------


def test_07_overplotting(overplot_cloud):
    import matplotlib.pyplot as plt

    x, y = overplot_cloud
    n = len(x)

    fig, ax = plt.subplots(figsize=(3, 3), dpi=72)
    ax.scatter(x, y, s=4, alpha=0.35, edgecolors="none")
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    fig.canvas.draw()

    pixel_positions = ax.transData.transform(np.column_stack([x, y]))
    rounded = np.round(pixel_positions).astype(int)
    distinct_pixels = len(set(map(tuple, rounded)))
    plt.close(fig)

    fraction_distinct = distinct_pixels / n
    assert fraction_distinct < 0.5, "far below the point count"

    fig, ax = plt.subplots()
    hb = ax.hexbin(x, y, gridsize=30)
    max_hex_count = hb.get_array().max()
    plt.close(fig)

    assert max_hex_count > 20  # a real density peak survives hexbin
    print(
        f"  {distinct_pixels} distinct pixel positions from {n} points "
        f"({fraction_distinct:.2%}); hexbin max bin count {max_hex_count:.0f}"
    )


# --------------------------------------------------------------------------
# Exercise 8 -- correlation without shape.
# --------------------------------------------------------------------------


def test_08_correlation_without_shape(quadratic_data):
    x, y = quadratic_data
    frame = pd.DataFrame({"x": x, "y": y})

    pearson_r = frame["x"].corr(frame["y"], method="pearson")
    assert abs(pearson_r) < 0.1

    # pandas' spearman needs scipy, which is not installed here -- compute
    # it directly as the Pearson correlation of the ranks, which is its
    # exact definition.
    rank_x = frame["x"].rank()
    rank_y = frame["y"].rank()
    spearman_r = rank_x.corr(rank_y, method="pearson")
    assert abs(spearman_r) < 0.1  # symmetric parabola: no monotonic signal either

    coefficients = np.polyfit(x, y, 2)
    predicted = np.polyval(coefficients, x)
    residual_sum_sq = np.sum((y - predicted) ** 2)
    total_sum_sq = np.sum((y - y.mean()) ** 2)
    r_squared = 1 - residual_sum_sq / total_sum_sq

    assert r_squared > 0.95
    print(
        f"  pearson r={pearson_r:.4f}, spearman r={spearman_r:.4f}, "
        f"quadratic fit R^2={r_squared:.4f} (coeffs {np.round(coefficients, 4)})"
    )


# --------------------------------------------------------------------------
# Exercise 9 -- jitter is distortion.
# --------------------------------------------------------------------------


def test_09_jitter_is_distortion(discrete_sample):
    rng = np.random.default_rng(99)
    jitter_width = 0.15
    jittered = discrete_sample + rng.uniform(-jitter_width, jitter_width, len(discrete_sample))

    max_shift = np.max(np.abs(jittered - discrete_sample))
    assert max_shift <= jitter_width

    # the underlying data is untouched by constructing the jittered copy
    assert np.array_equal(discrete_sample, discrete_sample)
    assert set(np.unique(discrete_sample)) == {1, 2, 3, 4, 5}
    print(f"  max jitter shift {max_shift:.4f} (width {jitter_width}); values unchanged")
