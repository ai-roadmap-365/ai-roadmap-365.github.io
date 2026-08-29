"""The worked reference suite for Day 129 -- "Plots That Say What They
Computed".

Nine exercises, each proving one real seaborn 0.13.2 / matplotlib 3.11.1
behaviour by drawing a real plot and reading real return types, artist
state, or numeric values -- never by reading source. Run it:

    pytest examples

Every table these tests use comes from `data.py`, imported through the
fixtures in `conftest.py`. Read `starter/00_brief.md` for the exercise-by-
exercise explanation; this file is the answer key.
"""

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pytest
import seaborn as sns

# --------------------------------------------------------------------------
# Exercise 1 -- axes-level versus figure-level. `scatterplot` draws into
# an Axes you already own and returns that Axes; `relplot` creates and
# owns its own Figure and returns a FacetGrid wrapping it.
# --------------------------------------------------------------------------


def test_1_axes_level_function_returns_the_axes_you_gave_it(team_scores):
    fig, ax = plt.subplots()
    result = sns.scatterplot(data=team_scores, x="team", y="score", ax=ax)
    assert isinstance(result, matplotlib.axes.Axes)
    assert result is ax  # drew into the Axes it was handed, nothing new


def test_1_figure_level_function_returns_a_facetgrid_owning_its_own_figure(team_scores):
    grid = sns.relplot(data=team_scores, x="team", y="score")
    assert isinstance(grid, sns.axisgrid.FacetGrid)
    assert isinstance(grid.figure, matplotlib.figure.Figure)
    # relplot never took an ax= argument here -- the Figure it owns is
    # its own, not one the caller created and handed in.
    assert grid.ax is not None
    assert grid.ax.figure is grid.figure


# --------------------------------------------------------------------------
# Exercise 2 -- the barplot trap. team_scores' four groups: A and B have
# almost the same shape of data (four values), but B's are 90, 88, 92, 10
# -- three of the four best scores in the whole table, with one outlier.
# The bar heights are the group MEANS, not any raw value; a stripplot of
# the same column exposes the four real points per group.
# --------------------------------------------------------------------------


def test_2_bar_heights_are_group_means_not_raw_values(team_scores):
    fig, ax = plt.subplots()
    sns.barplot(data=team_scores, x="team", y="score", ax=ax)
    heights = {round(float(bar.get_height()), 4) for bar in ax.patches}

    expected_means = team_scores.groupby("team")["score"].mean()
    assert set(round(float(m), 4) for m in expected_means) == heights
    assert heights == {79.0, 70.0, 67.5, 57.5}

    # For every team, its own bar height is a computed mean, not one of
    # its own four raw observations -- the chart draws a statistic, not
    # a value anyone actually recorded.
    for team, group in team_scores.groupby("team"):
        mean = round(float(group["score"].mean()), 4)
        raw_values_for_team = set(group["score"])
        assert mean not in raw_values_for_team


def test_2_team_b_bar_is_lower_than_team_a_despite_having_the_best_scores(team_scores):
    means = team_scores.groupby("team")["score"].mean()
    assert means["B"] < means["A"]

    # But three of team B's four raw scores exceed every one of team A's.
    b_scores = team_scores.loc[team_scores["team"] == "B", "score"]
    a_scores = team_scores.loc[team_scores["team"] == "A", "score"]
    b_above_all_of_a = (b_scores.values[:, None] > a_scores.values[None, :]).all(axis=1)
    assert b_above_all_of_a.sum() == 3  # 90, 88 and 92 all beat every A score; only 10 does not


def test_2_stripplot_of_the_same_column_shows_all_four_raw_points_per_group(team_scores):
    fig, ax = plt.subplots()
    sns.stripplot(data=team_scores, x="team", y="score", ax=ax)
    # One PathCollection per category; each collection's offsets are the
    # real per-point (x, y) locations stripplot drew -- there is no
    # aggregation step to hide anything behind.
    assert len(ax.collections) == 4
    all_y = sorted(float(y) for coll in ax.collections for (_, y) in coll.get_offsets())
    assert all_y == sorted(float(v) for v in team_scores["score"])  # every raw value present, none averaged


# --------------------------------------------------------------------------
# Exercise 3 -- bootstrap randomness. The default error bar is a
# bootstrapped 95% confidence interval, and a bootstrap is a random
# resampling procedure: two unseeded calls give slightly different
# extents; fixing seed= makes them identical.
# --------------------------------------------------------------------------


def _barplot_errorbar_extents(team_scores, **kwargs):
    fig, ax = plt.subplots()
    sns.barplot(data=team_scores, x="team", y="score", ax=ax, **kwargs)
    return [(float(min(line.get_ydata())), float(max(line.get_ydata()))) for line in ax.lines]


def test_3_unseeded_bootstrap_intervals_differ_between_two_runs(team_scores):
    # A bootstrap over a tiny sample (4 observations per group) draws
    # from a small, discrete space of possible resamples, so any SINGLE
    # pair of unseeded runs can occasionally land on the same extent by
    # chance -- that is a real property of resampling a small sample,
    # not a flaw in the claim. Six independent draws makes the claim
    # itself robust: the probability that all six happen to coincide is
    # negligible, while any two of them differing is still exactly the
    # fact this exercise is about.
    runs = [_barplot_errorbar_extents(team_scores) for _ in range(6)]
    distinct_runs = {tuple(run) for run in runs}
    assert len(distinct_runs) > 1


def test_3_seeded_bootstrap_intervals_are_identical_between_two_runs(team_scores):
    run_1 = _barplot_errorbar_extents(team_scores, seed=42)
    run_2 = _barplot_errorbar_extents(team_scores, seed=42)
    assert run_1 == run_2


# --------------------------------------------------------------------------
# Exercise 4 -- errorbar= options. 'sd' draws +/- one standard deviation;
# ('ci', 95) draws a bootstrapped 95% confidence interval. On the same
# data these are different statistics and must produce different extents.
# --------------------------------------------------------------------------


def test_4_sd_and_ci95_error_bars_have_different_extents(team_scores):
    sd_extents = _barplot_errorbar_extents(team_scores, errorbar="sd", seed=42)
    ci_extents = _barplot_errorbar_extents(team_scores, errorbar=("ci", 95), seed=42)
    assert sd_extents != ci_extents

    # Team A specifically: 'sd' is a fixed, deterministic computation
    # (does not depend on the seed at all) while ('ci', 95) is bootstrapped.
    sd_width = sd_extents[0][1] - sd_extents[0][0]
    ci_width = ci_extents[0][1] - ci_extents[0][0]
    assert round(sd_width, 2) != round(ci_width, 2)


def test_4_sd_error_bar_does_not_depend_on_the_seed(team_scores):
    # 'sd' is a closed-form statistic, not a resampling procedure, so it
    # is identical regardless of seed -- unlike the bootstrapped options.
    run_1 = _barplot_errorbar_extents(team_scores, errorbar="sd", seed=1)
    run_2 = _barplot_errorbar_extents(team_scores, errorbar="sd", seed=2)
    assert run_1 == run_2


# --------------------------------------------------------------------------
# Exercise 5 -- long versus wide. seaborn's semantic mappings read column
# NAMES; a wide frame has no "quarter" or "revenue" column to name, so
# asking for one raises. The long form melt (Day 124) produces has both.
# --------------------------------------------------------------------------


def test_5_wide_frame_raises_when_asked_for_columns_it_does_not_have(wide_revenue):
    with pytest.raises(ValueError, match="quarter"):
        sns.lineplot(data=wide_revenue, x="quarter", y="revenue", hue="region")


def test_5_melted_long_form_has_the_columns_hue_needs_and_plots_successfully(wide_revenue, long_revenue):
    # The exact melt call Day 124 taught: one id column, the rest become
    # a variable/value pair.
    reconstructed = wide_revenue.melt(id_vars="region", var_name="quarter", value_name="revenue")
    pd.testing.assert_frame_equal(reconstructed, long_revenue)

    assert list(long_revenue.columns) == ["region", "quarter", "revenue"]
    assert long_revenue.shape == (20, 3)  # 5 regions * 4 quarters

    ax = sns.lineplot(data=long_revenue, x="quarter", y="revenue", hue="region")
    assert isinstance(ax, matplotlib.axes.Axes)
    _, legend_labels = ax.get_legend_handles_labels()
    assert set(legend_labels) == set(long_revenue["region"].unique())  # one legend entry per region


# --------------------------------------------------------------------------
# Exercise 6 -- faceting. col= produces exactly one Axes per category;
# col_wrap reshapes the grid without changing how many Axes exist.
# --------------------------------------------------------------------------


def test_6_col_produces_exactly_one_axes_per_category(long_revenue):
    n_regions = long_revenue["region"].nunique()
    assert n_regions == 5

    grid = sns.catplot(data=long_revenue, x="quarter", y="revenue", col="region", kind="bar")
    assert len(grid.axes.flat) == n_regions
    assert grid._nrow == 1
    assert grid._ncol == n_regions


def test_6_col_wrap_changes_the_grid_shape_not_the_axes_count(long_revenue):
    n_regions = long_revenue["region"].nunique()

    wrapped = sns.catplot(data=long_revenue, x="quarter", y="revenue", col="region", kind="bar", col_wrap=3)
    assert len(wrapped.axes.flat) == n_regions  # still 5 Axes total
    assert wrapped._ncol == 3  # but now arranged 3 wide
    assert wrapped._nrow == 2  # and 2 rows tall (ceil(5 / 3))


# --------------------------------------------------------------------------
# Exercise 7 -- the escape hatch. seaborn draws with matplotlib underneath,
# so a label set with the Day 128 object API after a seaborn call sticks.
# --------------------------------------------------------------------------


def test_7_a_label_set_after_a_seaborn_call_is_present_on_the_axes(team_scores):
    fig, ax = plt.subplots()
    sns.boxplot(data=team_scores, x="team", y="score", ax=ax)
    assert ax.get_ylabel() == "score"  # seaborn's own default label, from the column name

    ax.set_ylabel("Score (0-100 scale)")
    ax.set_ylim(0, 100)
    assert ax.get_ylabel() == "Score (0-100 scale)"
    assert ax.get_ylim() == (0.0, 100.0)


# --------------------------------------------------------------------------
# Exercise 8 -- theme side effects. set_theme() mutates matplotlib's
# global rcParams; every plot drawn afterwards, seaborn or not, inherits
# the change until it is explicitly reset.
# --------------------------------------------------------------------------


def test_8_set_theme_changes_specific_rcparams_and_is_reversible():
    watched_keys = [
        "axes.facecolor",
        "axes.grid",
        "axes.edgecolor",
        "grid.color",
        "axes.axisbelow",
        "xtick.bottom",
        "ytick.left",
    ]
    before = {key: matplotlib.rcParams[key] for key in watched_keys}

    sns.set_theme()
    after = {key: matplotlib.rcParams[key] for key in watched_keys}
    changed_keys = {key for key in watched_keys if before[key] != after[key]}

    # Every one of these seven keys changed on this run; report exactly
    # which if that ever narrows on a different seaborn version.
    assert changed_keys == set(watched_keys)
    assert after["axes.facecolor"] == "#EAEAF2"
    assert after["axes.grid"] is True

    matplotlib.rcParams.update(before)
    restored = {key: matplotlib.rcParams[key] for key in watched_keys}
    assert restored == before  # matplotlib is back exactly where it started


# --------------------------------------------------------------------------
# Exercise 9 -- overlay. A boxplot's box artists are matplotlib patches;
# a stripplot's points are a separate PathCollection per category. Both
# can share one Axes, which is the honest form for a small sample.
# --------------------------------------------------------------------------


def test_9_boxplot_with_stripplot_overlaid_carries_both_kinds_of_artist(team_scores):
    fig, ax = plt.subplots()
    sns.boxplot(data=team_scores, x="team", y="score", ax=ax)
    assert len(ax.patches) == 4  # one box per team
    assert len(ax.collections) == 0  # nothing point-based yet

    sns.stripplot(data=team_scores, x="team", y="score", ax=ax, color="black")
    assert len(ax.patches) == 4  # the box patches are still there, untouched
    assert len(ax.collections) == 4  # one point collection per team, added on top

    n_points_drawn = sum(len(coll.get_offsets()) for coll in ax.collections)
    assert n_points_drawn == len(team_scores)  # every one of the 16 raw points is visible somewhere
