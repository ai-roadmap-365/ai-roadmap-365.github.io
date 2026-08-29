"""The worked reference suite for Day 127 -- "Charts That Answer the Question".

Nine exercises. The hard part of a visualisation lab is that "looks
better" is not testable, so this suite never asserts it. It asserts only
things that genuinely are measurable: drawn pixel areas, colour distances
in CIELAB before and after a colour vision deficiency transform, rank
correlation between a palette's order and its luminance, the number of
comparisons a reader performs, the fraction of a chart's ink that is data,
and the number of distinct grey levels an image contains.

Run it:

    pytest examples

`encoding.py` holds the geometry and colour arithmetic, `charts.py` the
two decision functions, `palettes.py` the swatches taken from matplotlib
and seaborn, and `render.py` everything that draws and everything that
measures a drawing. Read `starter/00_brief.md` for the exercise-by-exercise
explanation; this file is the answer key.

Every render writes into `png_dir`, a temporary directory outside the lab
that the fixture removes on the way out. The lab leaves no image behind.
"""

from __future__ import annotations

import math

import pytest

import charts as C
import encoding as E
import palettes as PAL
import render as R

# --------------------------------------------------------------------------
# Exercise 1 -- the square law, measured.
#
# Encode a value as a circle's RADIUS and every ratio in the chart comes
# out squared: a value twice as large is drawn four times as large. Encode
# it as the circle's AREA and the ratio the reader perceives is the ratio
# in the data. First the arithmetic, then the same claim measured off real
# rendered pixels, because arithmetic about a picture is not a picture.
# --------------------------------------------------------------------------

VALUES = [50.0, 100.0]  # the second is exactly twice the first


def test_1_radius_encoding_squares_every_ratio():
    data_ratio = VALUES[-1] / VALUES[0]
    assert data_ratio == 2.0

    by_radius = E.encoded_area_ratio(VALUES, mode="radius")
    by_area = E.encoded_area_ratio(VALUES, mode="area")

    # The distortion is exactly the square of the data ratio.
    assert by_radius == pytest.approx(4.0)
    assert by_radius == pytest.approx(data_ratio**2)

    # Encoding by area removes it entirely.
    assert by_area == pytest.approx(2.0)
    assert by_area == pytest.approx(data_ratio)

    # And the distortion is a factor of two, not a rounding difference.
    assert by_radius / by_area == pytest.approx(2.0)


def test_1_rendered_pixel_areas_confirm_the_square_law(png_dir):
    # Radius encoding: value 50 -> radius 40 px, value 100 -> radius 80 px.
    small = png_dir / "r_small.png"
    big = png_dir / "r_big.png"
    R.render_circle(small, radius_px=40)
    R.render_circle(big, radius_px=80)
    area_small = R.measure_circle_area_px(small)
    area_big = R.measure_circle_area_px(big)

    # Measured on this machine: 5156 px and 20368 px. The rasteriser lands
    # a couple of percent off the ideal pi*r^2 (5026.5 and 20106.2) because
    # a circle's boundary does not fall on pixel edges; the RATIO is what
    # the exercise is about and it survives that intact.
    assert area_small == pytest.approx(math.pi * 40**2, rel=0.03)
    assert area_big == pytest.approx(math.pi * 80**2, rel=0.03)
    assert area_big / area_small == pytest.approx(4.0, rel=0.02)

    # Area encoding: value 100 gets radius 40*sqrt(2), so twice the ink.
    honest = png_dir / "a_big.png"
    R.render_circle(honest, radius_px=40 * math.sqrt(2))
    area_honest = R.measure_circle_area_px(honest)
    assert area_honest / area_small == pytest.approx(2.0, rel=0.02)

    # The two encodings of the SAME value differ by a factor of two on the
    # page. This is the bubble chart that exaggerates without lying about
    # a single number.
    assert area_big / area_honest == pytest.approx(2.0, rel=0.02)


# --------------------------------------------------------------------------
# Exercise 2 -- the perceptual ranking as a decision function.
#
# Cleveland and McGill measured how accurately people read magnitudes off
# each visual channel. That ranking is not taste, and `best_encoding` is
# what it looks like when you actually use it to decide something.
# --------------------------------------------------------------------------


def test_2_ranking_is_in_cleveland_mcgill_order():
    # Position beats length beats angle beats area beats volume beats
    # saturation. Asserting the INDICES rather than the list literal means
    # the test is about the ordering, not about the spelling.
    assert C.encoding_rank("position_common_scale") == 0
    assert C.encoding_rank("position_common_scale") < C.encoding_rank("position_nonaligned_scales")
    assert C.encoding_rank("position_nonaligned_scales") < C.encoding_rank("length")
    assert C.encoding_rank("length") < C.encoding_rank("angle_slope")
    assert C.encoding_rank("angle_slope") < C.encoding_rank("area")
    assert C.encoding_rank("area") < C.encoding_rank("volume")
    assert C.encoding_rank("volume") < C.encoding_rank("color_saturation")

    # Hue is not on the ladder at all, and asking for its rank is an error
    # rather than a large number: there is no magnitude to read off a hue,
    # so "how accurately" is not a question hue can be asked.
    with pytest.raises(ValueError, match="not a ranked magnitude channel"):
        C.encoding_rank("hue")


def test_2_best_encoding_case_table():
    # Each case, and why it is the answer it is.
    cases = [
        # Nothing is competing for the axes, so take the top of the ladder.
        (("quantitative", "compare"), "position_common_scale"),
        # Small multiples: each panel carries its own axis, which IS
        # Cleveland and McGill's second task.
        (("quantitative", "compare_across_panels"), "position_nonaligned_scales"),
        # A map has already spent both spatial axes on geography, so the
        # best REMAINING channel is area -- bubbles, and now you know
        # exactly why they must be scaled by area and not by radius.
        (("quantitative", "magnitude_on_map"), "area"),
        # Both axes taken by other variables: colour is what is left, and
        # for a quantity that means intensity, read roughly.
        (("quantitative", "encode_in_color"), "color_saturation"),
        # An ordinal variable on an axis reads exactly like a quantitative
        # one: the categories are in order and position preserves it.
        (("ordinal", "compare"), "position_common_scale"),
        # But an ordinal variable pushed into colour must keep its order,
        # so it needs a luminance ramp -- never a categorical palette.
        (("ordinal", "encode_in_color"), "luminance_sequential"),
        # Time is ordered, so the same rule applies to it.
        (("temporal", "encode_in_color"), "luminance_sequential"),
        (("temporal", "trend"), "position_common_scale"),
        # Nominal has no order and no magnitude. Hue says "different",
        # which is the entire claim nominal data supports.
        (("nominal", "identify_group"), "hue"),
        (("nominal", "encode_in_color"), "hue"),
        # Comparing counts BY nominal category still puts the count on the
        # common scale; the category goes on the categorical axis and no
        # order is invented.
        (("nominal", "compare"), "position_common_scale"),
    ]
    for (data_type, task), expected in cases:
        assert C.best_encoding(data_type, task) == expected, (data_type, task)

    # The load-bearing negative: ordinal data must NOT land on a
    # categorical hue palette. Exercise 5 measures why.
    assert C.best_encoding("ordinal", "encode_in_color") != "hue"


def test_2_best_encoding_rejects_what_it_does_not_understand():
    with pytest.raises(ValueError, match="unknown data type"):
        C.best_encoding("categorical", "compare")
    with pytest.raises(ValueError, match="unknown task"):
        C.best_encoding("quantitative", "look_nice")


# --------------------------------------------------------------------------
# Exercise 3 -- from the question to the chart.
#
# `choose_chart` takes the reader's question, the number of values, and
# the data types, and names an instrument. Two of its answers are the
# point of the whole function: below a stated number of values it returns
# a TABLE, and it never returns a pie chart for anything.
# --------------------------------------------------------------------------


def test_3_choose_chart_case_table():
    cases = [
        # Comparison. Eight regions is past the table threshold, and
        # sorting is what turns "find the largest" into one glance.
        (("comparison", 8, ["nominal", "quantitative"]), "sorted_horizontal_bar"),
        (("comparison", 30, ["nominal", "quantitative"]), "sorted_horizontal_bar"),
        # Three numbers do not need a chart. Print them.
        (("comparison", 3, ["nominal", "quantitative"]), "table"),
        (("comparison", 5, ["nominal", "quantitative"]), "table"),
        (("comparison", 6, ["nominal", "quantitative"]), "sorted_horizontal_bar"),
        # Distribution. One variable is a histogram; a handful of groups
        # is small multiples; many groups is a box plot grid, where the
        # summary is the only thing that still fits.
        (("distribution", 1, ["quantitative"]), "histogram"),
        (("distribution", 4, ["quantitative", "nominal"]), "small_multiples_histogram"),
        (("distribution", 40, ["quantitative", "nominal"]), "boxplot_by_category"),
        # Relationship. A scatter until the marks stop being individually
        # readable, then a density map that admits what it is showing.
        (("relationship", 200, ["quantitative"]), "scatter"),
        (("relationship", 10_000, ["quantitative"]), "hexbin"),
        # Composition. Small enough is a table; larger is a stacked bar --
        # never a pie, see the next test.
        (("composition", 3, ["nominal", "quantitative"]), "table"),
        (("composition", 12, ["nominal", "quantitative"]), "stacked_bar"),
        # Change over time. One line, or small multiples once the tangle
        # would beat the reader.
        (("change_over_time", 3, ["temporal", "quantitative"]), "line"),
        (("change_over_time", 20, ["temporal", "quantitative"]), "small_multiples_line"),
    ]
    for (kind, n, types), expected in cases:
        assert C.choose_chart(kind, n, types) == expected, (kind, n, types)


def test_3_choose_chart_never_recommends_a_pie():
    recommendations = set()
    for kind in sorted(C.QUESTION_KINDS):
        types = ["temporal", "quantitative"] if kind == "change_over_time" else [
            "nominal",
            "quantitative",
        ]
        for n in (1, 2, 3, 5, 6, 8, 9, 30, 2001, 10_000):
            recommendations.add(C.choose_chart(kind, n, types))

    assert "pie" not in recommendations
    assert "donut" not in recommendations
    # Specifically for ranking, the case where a pie is worst: the answer
    # is always the sorted bar chart, at every size past the table rule.
    for n in (6, 8, 30, 200):
        assert C.choose_chart("comparison", n, ["nominal", "quantitative"]) == (
            "sorted_horizontal_bar"
        )


def test_3_choose_chart_validates_its_inputs():
    with pytest.raises(ValueError, match="unknown question kind"):
        C.choose_chart("pretty", 8, ["quantitative"])
    with pytest.raises(ValueError, match="unknown data types"):
        C.choose_chart("comparison", 8, ["categorical"])
    with pytest.raises(ValueError, match="n_categories must be at least 1"):
        C.choose_chart("comparison", 0, ["quantitative"])
    # "Over time" with no time in the data is a question about something
    # else, and guessing at what would be worse than refusing.
    with pytest.raises(ValueError, match="needs a temporal variable"):
        C.choose_chart("change_over_time", 5, ["nominal", "quantitative"])


# --------------------------------------------------------------------------
# Exercise 4 -- colour deficiency, simulated and measured.
#
# The claim "a red/green pass-fail chart is unreadable for a substantial
# minority of your audience" is usually asserted. Here it is measured: run
# both colours through a published deuteranopia transform and see how much
# of the separation survives.
# --------------------------------------------------------------------------

# CIE76 distance below which two swatches in a legend are, for practical
# purposes, the same colour. The literature puts the just-noticeable
# difference for adjacent patches near 2.3; 10 is a deliberately generous
# threshold, chosen so passing this test is not a close-run thing.
COLLAPSE_THRESHOLD = 10.0

# And the distance a pair must keep to count as genuinely distinguishable.
SURVIVAL_THRESHOLD = 25.0


def test_4_red_green_pair_collapses_under_deuteranopia():
    red, green = PAL.PASS_FAIL_RED, PAL.PASS_FAIL_GREEN
    result = E.deuteranopia_collapse(red, green)

    # To a reader with typical colour vision these are about as far apart
    # as two colours get: measured 119.77 on this machine.
    assert result["normal_delta_e"] > 100.0

    # After the transform they are 7.31 apart -- closer together than many
    # people can reliably separate in a legend, and about 6% of the
    # separation a normal-vision reader gets.
    assert result["simulated_delta_e"] < COLLAPSE_THRESHOLD
    assert result["retained_fraction"] < 0.10

    # Simulation approximates a deficiency; it does not reproduce anyone's
    # experience. What this number licenses is "do not let colour alone
    # carry this distinction", not "this is what they see".
    assert 0.0 < result["simulated_delta_e"] < result["normal_delta_e"]


def test_4_colorblind_safe_pair_survives_the_same_transform():
    result = E.deuteranopia_collapse(PAL.SAFE_BLUE, PAL.SAFE_ORANGE)

    # seaborn's blue and orange start about as far apart as the red/green
    # pair (measured 115.70) and stay there: 116.51 after the transform,
    # so essentially all of the separation survives.
    assert result["normal_delta_e"] > 100.0
    assert result["simulated_delta_e"] > SURVIVAL_THRESHOLD
    assert result["retained_fraction"] > 0.90

    # The two pairs are close to equally distinguishable to a normal
    # -vision reader and nowhere near it afterwards. Same starting point,
    # opposite outcome -- which is the whole argument for choosing the
    # palette on purpose.
    unsafe = E.deuteranopia_collapse(PAL.PASS_FAIL_RED, PAL.PASS_FAIL_GREEN)
    assert result["simulated_delta_e"] > 10 * unsafe["simulated_delta_e"]


# --------------------------------------------------------------------------
# Exercise 5 -- an ordered variable on a categorical palette.
#
# Order is information the data HAS. A palette either carries it or
# destroys it, and the measurement is the rank correlation between the
# variable's order and the palette's luminance order.
# --------------------------------------------------------------------------


def test_5_sequential_palette_preserves_the_order():
    palette = PAL.viridis_steps(len(PAL.SATISFACTION_LEVELS))
    assert len(palette) == 5

    luminances = [E.relative_luminance(c) for c in palette]
    # Measured: 0.0190, 0.0885, 0.2234, 0.4511, 0.7826 -- strictly rising.
    assert luminances == sorted(luminances)

    rho = E.luminance_order_correlation(palette)
    assert rho == pytest.approx(1.0)

    # So a greyscale photocopy of a viridis-coded chart still reads in the
    # right order. That is not a nicety; it is the difference between a
    # legend being needed and being merely helpful.


def test_5_categorical_palette_destroys_the_order():
    palette = PAL.tab10_steps(len(PAL.SATISFACTION_LEVELS))
    assert len(palette) == 5

    luminances = [E.relative_luminance(c) for c in palette]
    # Measured: 0.1678, 0.3647, 0.2586, 0.1590, 0.1967 -- up, down, down,
    # up. "Satisfied" is DARKER than "dissatisfied", so the picture says
    # the opposite of the data.
    assert luminances != sorted(luminances)

    rho = E.luminance_order_correlation(palette)
    # Measured -0.2 on this machine: not merely weak, but pointing the
    # wrong way. tab10 is not defective -- it is doing its job, which is
    # to make neighbours look DIFFERENT, and difference has no direction.
    assert rho == pytest.approx(-0.2)
    assert abs(rho) < 0.5

    sequential_rho = E.luminance_order_correlation(PAL.viridis_steps(5))
    assert abs(sequential_rho) > abs(rho)


# --------------------------------------------------------------------------
# Exercise 6 -- sorting is an encoding decision, and its cost is the
# reader's, not yours.
# --------------------------------------------------------------------------


def test_6_sorting_changes_the_effort_not_the_answer():
    values = [float(v) for v in (37, 12, 88, 45, 3, 61, 29, 74, 18, 52, 9, 66, 41, 25, 80, 7, 58, 33, 95, 21)]
    assert len(values) == 20

    unsorted_cost = C.comparisons_to_find_max(values, presented_sorted=False)
    sorted_cost = C.comparisons_to_find_max(values, presented_sorted=True)

    # Source order: hold a running best, check all nineteen others.
    assert unsorted_cost == 19
    # Sorted: read the top row, glance at the second to confirm the chart
    # really is sorted, stop.
    assert sorted_cost == 1
    assert unsorted_cost == 19 * sorted_cost

    # And the answer is identical either way. Sorting moved nothing but
    # the reader's effort -- which is exactly why it is free to do and
    # expensive to skip.
    descending = sorted(values, reverse=True)
    assert descending[0] == values[C.index_of_max(values)] == 95.0

    # The same argument at the scale of a real category list.
    assert C.comparisons_to_find_max([0.0] * 200, presented_sorted=False) == 199
    assert C.comparisons_to_find_max([0.0] * 200, presented_sorted=True) == 1


# --------------------------------------------------------------------------
# Exercise 7 -- the data-ink ratio, counted in pixels.
#
# Same eight numbers, same bars, same labels. One chart adds a tinted
# panel, gridlines on both axes and a heavy box; the other does not. Count
# the ink and divide.
# --------------------------------------------------------------------------


def test_7_removing_furniture_raises_the_data_ink_ratio(png_dir):
    decorated = png_dir / "decorated.png"
    plain = png_dir / "plain.png"
    R.render_region_bar_chart(decorated, decorated=True)
    R.render_region_bar_chart(plain, decorated=False)

    total_decorated = R.count_non_background_pixels(decorated)
    total_plain = R.count_non_background_pixels(plain)
    ratio_decorated = R.data_ink_ratio(decorated, R.BAR_RGB)
    ratio_plain = R.data_ink_ratio(plain, R.BAR_RGB)

    # Measured on this machine: 172,351 total ink against 79,107 -- the
    # decorated chart spends more than twice the ink to say the same
    # thing.
    assert total_decorated == pytest.approx(172_351, rel=0.05)
    assert total_plain == pytest.approx(79_107, rel=0.05)
    assert total_decorated > 2 * total_plain

    # And the ratio moves in the expected direction, hard: 0.367 against
    # 0.934. Nearly two thirds of the decorated chart is furniture.
    assert ratio_decorated == pytest.approx(0.3669, abs=0.03)
    assert ratio_plain == pytest.approx(0.9344, abs=0.03)
    assert ratio_plain > ratio_decorated
    assert ratio_plain - ratio_decorated > 0.5

    # The point is not that gridlines are forbidden. It is that every mark
    # is a claim on the reader's attention, and the ones that are not data
    # should have to justify themselves.


# --------------------------------------------------------------------------
# Exercise 8 -- overplotting, and two ways out of it.
#
# Ten thousand points, one pixel each, none of them clipped. Count how
# many distinct pixels end up painted -- the shortfall is data that is on
# the page in principle and invisible in fact.
# --------------------------------------------------------------------------

N_POINTS = 10_000


def test_8_overplotting_hides_a_third_of_the_data(png_dir, points):
    x, y = points
    assert len(x) == N_POINTS
    # Nothing is clipped, so a shortfall below is overplotting and not
    # points falling off the edge of the picture.
    assert R.points_inside_axes(x, y) == N_POINTS

    opaque = png_dir / "opaque.png"
    R.render_scatter(opaque, x, y, alpha=1.0)
    painted = R.count_painted_pixels(opaque)

    # Measured: 6,349 painted pixels for 10,000 points. 3,651 points --
    # 36.5% of the data -- landed on a pixel another point had already
    # blackened and changed nothing about the image.
    assert painted == pytest.approx(6_349, rel=0.05)
    assert painted < N_POINTS
    assert painted / N_POINTS < 0.75

    # The stronger statement: the opaque image contains exactly TWO grey
    # levels, paper and ink. Whether a pixel carries one point or forty,
    # it is the same black -- the density information is not dimmed, it is
    # absent.
    assert R.count_distinct_luminance_levels(opaque) == 2


def test_8_alpha_and_hexbin_recover_the_density(png_dir, points):
    x, y = points

    opaque = png_dir / "opaque.png"
    blended = png_dir / "blended.png"
    hexes = png_dir / "hexbin.png"
    R.render_scatter(opaque, x, y, alpha=1.0)
    R.render_scatter(blended, x, y, alpha=0.05)
    R.render_hexbin(hexes, x, y)

    opaque_levels = R.count_distinct_luminance_levels(opaque)
    blended_levels = R.count_distinct_luminance_levels(blended)
    hexbin_levels = R.count_distinct_luminance_levels(hexes)

    # Measured: 2, 9 and 244. Alpha blending lets a pixel record HOW MANY
    # points landed on it, up to the point where the stack saturates --
    # 9 levels means the busiest pixel in this cloud carries about eight
    # points.
    assert opaque_levels == 2
    assert blended_levels >= 5
    assert blended_levels > opaque_levels

    # Hexbin does better still, because it aggregates BEFORE drawing
    # instead of hoping the compositor will: 244 distinct levels, a
    # genuine density surface rather than a smudge.
    assert hexbin_levels > 50
    assert hexbin_levels > blended_levels

    # And this is why `choose_chart` stops recommending a scatter past
    # `OVERPLOT_POINT_LIMIT` -- the recommendation and the measurement are
    # the same fact seen twice.
    assert C.choose_chart("relationship", N_POINTS, ["quantitative"]) == "hexbin"


# --------------------------------------------------------------------------
# Exercise 9 -- when a table beats a chart.
#
# The reflex to chart everything is itself a failure mode, and the
# threshold where charting starts to pay is a decision you should make on
# purpose rather than by habit.
# --------------------------------------------------------------------------


def test_9_a_table_beats_a_chart_below_the_threshold():
    small = C.choose_chart("comparison", 3, ["nominal", "quantitative"])
    large = C.choose_chart("comparison", 30, ["nominal", "quantitative"])

    assert small == "table"
    assert large == "sorted_horizontal_bar"

    # The boundary, stated: a chart's advantage is that it converts
    # comparison from arithmetic into a perceptual judgement. With three
    # numbers there was no arithmetic to convert -- the reader can just
    # read them, exactly, which a bar length never lets them do. Past
    # TABLE_MAX_VALUES the reader can no longer hold the set in their head
    # at once and the perceptual judgement starts to pay for the precision
    # it costs. Five is where this course puts the line; the number is a
    # judgement and the point is that it is written down.
    assert C.TABLE_MAX_VALUES == 5
    assert C.choose_chart("comparison", C.TABLE_MAX_VALUES, ["quantitative"]) == "table"
    assert C.choose_chart("comparison", C.TABLE_MAX_VALUES + 1, ["quantitative"]) == (
        "sorted_horizontal_bar"
    )

    # Composition obeys the same rule, which is where the last argument
    # for a pie chart goes: "just two or three slices" is precisely the
    # case a table answers exactly.
    assert C.choose_chart("composition", 2, ["nominal", "quantitative"]) == "table"
    assert C.choose_chart("composition", 3, ["nominal", "quantitative"]) == "table"
