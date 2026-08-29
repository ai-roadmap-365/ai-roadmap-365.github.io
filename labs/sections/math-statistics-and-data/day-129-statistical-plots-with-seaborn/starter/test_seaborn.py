"""Your exercises for Day 129 -- "Plots That Say What They Computed".

Nine exercises. Every test below currently calls `pytest.skip(...)` --
replace the skip with real assertions and delete the skip line. Read
`00_brief.md` for the exercise-by-exercise explanation, and `data.py` for
what `team_scores`, `wide_revenue` and `long_revenue` actually contain.

Check yourself at any point:

    pytest starter -v

The reference answer key lives in `examples/test_seaborn.py` -- read it
AFTER you have tried, never before.
"""

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pytest
import seaborn as sns

# --------------------------------------------------------------------------
# Exercise 1 -- axes-level versus figure-level.
# --------------------------------------------------------------------------


def test_1_axes_level_function_returns_the_axes_you_gave_it(team_scores):
    pytest.skip("Call sns.scatterplot(..., ax=ax) and assert the return value is that same ax")


def test_1_figure_level_function_returns_a_facetgrid_owning_its_own_figure(team_scores):
    pytest.skip("Call sns.relplot(...) and assert it returns a seaborn.axisgrid.FacetGrid owning its own Figure")


# --------------------------------------------------------------------------
# Exercise 2 -- the barplot trap.
# --------------------------------------------------------------------------


def test_2_bar_heights_are_group_means_not_raw_values(team_scores):
    pytest.skip("Draw a barplot; assert each bar's height equals that team's mean, and is absent from that team's own raw values")


def test_2_team_b_bar_is_lower_than_team_a_despite_having_the_best_scores(team_scores):
    pytest.skip("Compare team A's and team B's means, then compare their raw scores directly")


def test_2_stripplot_of_the_same_column_shows_all_four_raw_points_per_group(team_scores):
    pytest.skip("Draw a stripplot; assert every raw score in team_scores appears in some collection's offsets")


# --------------------------------------------------------------------------
# Exercise 3 -- bootstrap randomness.
# --------------------------------------------------------------------------


def test_3_unseeded_bootstrap_intervals_differ_between_two_runs(team_scores):
    pytest.skip("Draw the same barplot six times without seed=; assert not all six sets of error-bar extents are identical")


def test_3_seeded_bootstrap_intervals_are_identical_between_two_runs(team_scores):
    pytest.skip("Draw the same barplot twice with the same seed=; assert the two sets of error-bar extents match exactly")


# --------------------------------------------------------------------------
# Exercise 4 -- errorbar= options.
# --------------------------------------------------------------------------


def test_4_sd_and_ci95_error_bars_have_different_extents(team_scores):
    pytest.skip("Compare errorbar='sd' against errorbar=('ci', 95) on the same data; assert the extents differ")


def test_4_sd_error_bar_does_not_depend_on_the_seed(team_scores):
    pytest.skip("Draw errorbar='sd' with two different seed values; assert the extents are identical either way")


# --------------------------------------------------------------------------
# Exercise 5 -- long versus wide.
# --------------------------------------------------------------------------


def test_5_wide_frame_raises_when_asked_for_columns_it_does_not_have(wide_revenue):
    pytest.skip("Call sns.lineplot on wide_revenue asking for x='quarter'; assert it raises ValueError")


def test_5_melted_long_form_has_the_columns_hue_needs_and_plots_successfully(wide_revenue, long_revenue):
    pytest.skip("melt wide_revenue yourself and compare it to long_revenue; then plot the long form with hue='region'")


# --------------------------------------------------------------------------
# Exercise 6 -- faceting.
# --------------------------------------------------------------------------


def test_6_col_produces_exactly_one_axes_per_category(long_revenue):
    pytest.skip("Call sns.catplot(..., col='region', kind='bar'); assert the number of Axes equals the region count")


def test_6_col_wrap_changes_the_grid_shape_not_the_axes_count(long_revenue):
    pytest.skip("Repeat with col_wrap=3; assert the same Axes count but a different (nrow, ncol) grid shape")


# --------------------------------------------------------------------------
# Exercise 7 -- the escape hatch.
# --------------------------------------------------------------------------


def test_7_a_label_set_after_a_seaborn_call_is_present_on_the_axes(team_scores):
    pytest.skip("Draw a boxplot into ax, then ax.set_ylabel(...) afterwards; assert the new label sticks")


# --------------------------------------------------------------------------
# Exercise 8 -- theme side effects.
# --------------------------------------------------------------------------


def test_8_set_theme_changes_specific_rcparams_and_is_reversible():
    pytest.skip("Capture matplotlib.rcParams before sns.set_theme(); assert specific keys changed; restore and assert equality")


# --------------------------------------------------------------------------
# Exercise 9 -- overlay.
# --------------------------------------------------------------------------


def test_9_boxplot_with_stripplot_overlaid_carries_both_kinds_of_artist(team_scores):
    pytest.skip("Draw a boxplot then a stripplot into the same ax; assert both ax.patches and ax.collections are populated")
