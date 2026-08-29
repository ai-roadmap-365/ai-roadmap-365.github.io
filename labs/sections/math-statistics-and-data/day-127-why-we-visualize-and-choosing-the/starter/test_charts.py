"""YOUR test suite for Day 127 -- "Charts That Answer the Question".

Nine exercises. Run it from the lab directory, not from here:

    pytest starter -v

Every exercise below ends in a `pytest.skip(...)` line. pytest reports a
skip as `s` and moves on, so an unfinished suite still exits 0. Replace
each skip with real assertions -- deleting the skip line is part of the
exercise. `starter/00_brief.md` explains each exercise in full.

The four modules beside this file are the lab's instruments, not
exercises. Read them before you start; do not edit them:

  encoding.py  geometry and colour arithmetic -- the square law, sRGB to
               CIELAB, the deuteranopia transform, Spearman's rho
  charts.py    the two decision functions, `best_encoding` and
               `choose_chart`, plus the Cleveland-McGill ordering
  palettes.py  the swatches, taken from matplotlib and seaborn themselves
  render.py    everything that draws, and everything that measures a
               drawing in pixels

Every render must go into the `png_dir` fixture -- a temporary directory
outside the lab. Write a PNG anywhere else and `tests/run_tests.sh` will
catch it.

Assert measured values, and give a rendered measurement a tolerance: a
rasteriser puts a circle's edge a pixel or two either way, so
`pytest.approx(..., rel=0.02)` is honest where an exact equality would be
luck. Nothing in this lab depends on timing.
"""

from __future__ import annotations

import math

import pytest

import charts as C
import encoding as E
import palettes as PAL
import render as R

# --------------------------------------------------------------------------
# EXERCISE 1 -- the square law, measured. See 00_brief.md exercise 1.
#
# Check with:   pytest starter -v -k test_1
# --------------------------------------------------------------------------

VALUES = [50.0, 100.0]  # the second is exactly twice the first


def test_1_radius_encoding_squares_every_ratio():
    pytest.skip(
        "exercise 1a: call encoding.encoded_area_ratio(VALUES, mode='radius') and again with "
        "mode='area'. Assert the radius encoding gives 4.0 -- the square of the data ratio 2.0 -- "
        "and the area encoding gives 2.0, and that the two differ by a factor of exactly 2."
    )


def test_1_rendered_pixel_areas_confirm_the_square_law(png_dir):
    pytest.skip(
        "exercise 1b: render.render_circle three circles into png_dir -- radius 40, radius 80, "
        "and radius 40*sqrt(2) -- then measure each with render.measure_circle_area_px. Assert "
        "the 80px circle covers about 4x the pixels of the 40px one (rel=0.02) and the "
        "40*sqrt(2) one about 2x, and report both counts."
    )


# --------------------------------------------------------------------------
# EXERCISE 2 -- the Cleveland-McGill ranking as a decision function.
#
# Check with:   pytest starter -v -k test_2
# --------------------------------------------------------------------------


def test_2_ranking_is_in_cleveland_mcgill_order():
    pytest.skip(
        "exercise 2a: use charts.encoding_rank to assert the ordering position_common_scale < "
        "position_nonaligned_scales < length < angle_slope < area < volume < color_saturation, "
        "and that asking for the rank of 'hue' raises ValueError."
    )


def test_2_best_encoding_case_table():
    pytest.skip(
        "exercise 2b: build a list of ((data_type, task), expected_channel) cases and assert "
        "charts.best_encoding returns each one. Cover at least: quantitative/compare, "
        "quantitative/compare_across_panels, quantitative/magnitude_on_map, "
        "ordinal/encode_in_color, nominal/identify_group and nominal/compare. Justify each "
        "expected answer in a comment, and assert explicitly that ordinal/encode_in_color is NOT "
        "'hue'."
    )


def test_2_best_encoding_rejects_what_it_does_not_understand():
    pytest.skip(
        "exercise 2c: assert charts.best_encoding raises ValueError matching 'unknown data type' "
        "for a bad data type and 'unknown task' for a bad task."
    )


# --------------------------------------------------------------------------
# EXERCISE 3 -- from the question to the chart.
#
# Check with:   pytest starter -v -k test_3
# --------------------------------------------------------------------------


def test_3_choose_chart_case_table():
    pytest.skip(
        "exercise 3a: build a ((question_kind, n_categories, data_types), expected) case table "
        "and assert charts.choose_chart returns each one. Cover all five question kinds, and "
        "include at least one case on each side of TABLE_MAX_VALUES, OVERPLOT_POINT_LIMIT and "
        "SMALL_MULTIPLE_LIMIT."
    )


def test_3_choose_chart_never_recommends_a_pie():
    pytest.skip(
        "exercise 3b: collect choose_chart's answer over every question kind and a spread of "
        "n_categories into a set, and assert neither 'pie' nor 'donut' is in it. Then assert "
        "that for ranking specifically the answer is always 'sorted_horizontal_bar'."
    )


def test_3_choose_chart_validates_its_inputs():
    pytest.skip(
        "exercise 3c: assert choose_chart raises ValueError for an unknown question kind, an "
        "unknown data type, n_categories of 0, and change_over_time with no temporal variable."
    )


# --------------------------------------------------------------------------
# EXERCISE 4 -- colour deficiency, simulated and measured.
#
# Check with:   pytest starter -v -k test_4
# --------------------------------------------------------------------------

COLLAPSE_THRESHOLD = 10.0
SURVIVAL_THRESHOLD = 25.0


def test_4_red_green_pair_collapses_under_deuteranopia():
    pytest.skip(
        "exercise 4a: call encoding.deuteranopia_collapse(PAL.PASS_FAIL_RED, PAL.PASS_FAIL_GREEN). "
        "Assert the normal-vision CIE76 distance is above 100, the simulated distance is below "
        "COLLAPSE_THRESHOLD, and the retained fraction is below 0.10. Report all three numbers."
    )


def test_4_colorblind_safe_pair_survives_the_same_transform():
    pytest.skip(
        "exercise 4b: run the same measurement on PAL.SAFE_BLUE and PAL.SAFE_ORANGE. Assert the "
        "simulated distance stays above SURVIVAL_THRESHOLD and the retained fraction above 0.90, "
        "and that the safe pair's simulated distance is more than 10x the red/green pair's."
    )


# --------------------------------------------------------------------------
# EXERCISE 5 -- an ordered variable on a categorical palette.
#
# Check with:   pytest starter -v -k test_5
# --------------------------------------------------------------------------


def test_5_sequential_palette_preserves_the_order():
    pytest.skip(
        "exercise 5a: take PAL.viridis_steps(5), compute encoding.relative_luminance of each, "
        "and assert the list is already sorted. Then assert "
        "encoding.luminance_order_correlation(palette) is approximately 1.0."
    )


def test_5_categorical_palette_destroys_the_order():
    pytest.skip(
        "exercise 5b: do the same with PAL.tab10_steps(5). Assert the luminance list is NOT "
        "sorted, that the rank correlation is well below the sequential palette's in absolute "
        "value, and report the number you measure."
    )


# --------------------------------------------------------------------------
# EXERCISE 6 -- sorting is an encoding decision.
#
# Check with:   pytest starter -v -k test_6
# --------------------------------------------------------------------------


def test_6_sorting_changes_the_effort_not_the_answer():
    pytest.skip(
        "exercise 6: build a list of 20 unsorted values. Assert "
        "charts.comparisons_to_find_max(values, presented_sorted=False) is 19 and with "
        "presented_sorted=True is 1, and that sorted(values, reverse=True)[0] equals "
        "values[charts.index_of_max(values)] -- sorting moved the effort, not the answer."
    )


# --------------------------------------------------------------------------
# EXERCISE 7 -- the data-ink ratio, counted in pixels.
#
# Check with:   pytest starter -v -k test_7
# --------------------------------------------------------------------------


def test_7_removing_furniture_raises_the_data_ink_ratio(png_dir):
    pytest.skip(
        "exercise 7: render.render_region_bar_chart into png_dir twice, decorated=True and "
        "decorated=False. Count total ink with render.count_non_background_pixels and the "
        "data-ink fraction with render.data_ink_ratio(path, render.BAR_RGB). Assert the plain "
        "chart's ratio is higher, and that the gap is more than 0.5. Report both counts and "
        "both ratios."
    )


# --------------------------------------------------------------------------
# EXERCISE 8 -- overplotting, and two ways out of it.
#
# Check with:   pytest starter -v -k test_8
# --------------------------------------------------------------------------

N_POINTS = 10_000


def test_8_overplotting_hides_a_third_of_the_data(png_dir, points):
    pytest.skip(
        "exercise 8a: confirm render.points_inside_axes says nothing is clipped, render the "
        "cloud with alpha=1.0, and assert the painted-pixel count is below 75% of N_POINTS. "
        "Then assert render.count_distinct_luminance_levels of that image is exactly 2 -- the "
        "density information is not dimmed, it is absent."
    )


def test_8_alpha_and_hexbin_recover_the_density(png_dir, points):
    pytest.skip(
        "exercise 8b: render the same cloud three ways -- alpha=1.0, alpha=0.05, and "
        "render.render_hexbin -- and count distinct luminance levels in each. Assert the alpha "
        "version has more than the opaque one and the hexbin more than 50. Finish by asserting "
        "charts.choose_chart('relationship', N_POINTS, ['quantitative']) == 'hexbin'."
    )


# --------------------------------------------------------------------------
# EXERCISE 9 -- when a table beats a chart.
#
# Check with:   pytest starter -v -k test_9
# --------------------------------------------------------------------------


def test_9_a_table_beats_a_chart_below_the_threshold():
    pytest.skip(
        "exercise 9: assert choose_chart('comparison', 3, ...) is 'table' and "
        "choose_chart('comparison', 30, ...) is 'sorted_horizontal_bar'. Assert the boundary "
        "sits exactly at charts.TABLE_MAX_VALUES by testing that value and that value plus one. "
        "Then write a comment explaining WHY the boundary is where it is -- what a chart buys "
        "you, and why three numbers do not need it."
    )
