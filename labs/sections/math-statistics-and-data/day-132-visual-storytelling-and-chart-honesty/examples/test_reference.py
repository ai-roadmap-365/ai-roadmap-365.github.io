"""Reference suite — Day 132. Every claim the lesson makes, asserted.

Nothing here compares rendered pixels to a stored reference image. Every
assertion reads a real artist's real geometry back out of matplotlib, or
computes a number from it, which is what makes the suite portable across
machines and matplotlib versions.
"""

import matplotlib.pyplot as plt
import numpy as np
import pytest

import honesty as H


# --------------------------------------------------------------------------
# Exercise 1 — the lie factor
# --------------------------------------------------------------------------


def test_lie_factor_is_a_ratio_of_ratios():
    assert H.lie_factor(3.0, 1.02) == pytest.approx(2.9411764705882355)
    assert H.lie_factor(1.02, 1.02) == 1.0


def test_lie_factor_rejects_a_zero_data_effect():
    with pytest.raises(ZeroDivisionError):
        H.lie_factor(1.0, 0.0)


def test_zero_baseline_bar_pair_has_lie_factor_one():
    factor, shown, data = H.bar_pair_lie_factor((100.0, 102.0))
    assert shown == pytest.approx(1.02)
    assert data == pytest.approx(1.02)
    assert factor == pytest.approx(1.0)


def test_truncated_bar_pair_shows_a_three_to_one_height_ratio():
    factor, shown, data = H.bar_pair_lie_factor((100.0, 102.0), ylim=(99, 103))
    assert shown == pytest.approx(3.0)
    assert data == pytest.approx(1.02)
    assert factor == pytest.approx(2.9411764705882355)
    assert factor > 2.5


def test_shown_ratio_comes_from_geometry_not_from_the_inputs():
    """The same inputs give two different shown ratios, which is only
    possible if the measurement really reads the drawn bars."""
    _, shown_honest, _ = H.bar_pair_lie_factor((100.0, 102.0))
    _, shown_lying, _ = H.bar_pair_lie_factor((100.0, 102.0), ylim=(99, 103))
    assert shown_honest != shown_lying


def test_matplotlib_autoscales_a_bar_chart_to_include_zero():
    fig, ax = H.bar_pair((100.0, 102.0))
    try:
        fig.canvas.draw()
        assert ax.get_ylim()[0] == 0.0
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# Exercise 2 — bars versus lines
# --------------------------------------------------------------------------


def test_a_line_on_a_truncated_axis_still_encodes_the_change_exactly():
    factor, shown, true_change = H.line_pair_lie_factor((100.0, 102.0), ylim=(99, 103))
    assert true_change == pytest.approx(2.0)
    assert shown == pytest.approx(2.0)
    assert factor == pytest.approx(1.0)


def test_the_line_lie_factor_is_one_on_every_baseline():
    for limits in (None, (99, 103), (90, 110), (99.5, 102.5)):
        factor, _, _ = H.line_pair_lie_factor((100.0, 102.0), ylim=limits)
        assert factor == pytest.approx(1.0), limits


def test_the_bar_and_the_line_disagree_on_the_same_axis():
    bar_factor, _, _ = H.bar_pair_lie_factor((100.0, 102.0), ylim=(99, 103))
    line_factor, _, _ = H.line_pair_lie_factor((100.0, 102.0), ylim=(99, 103))
    assert bar_factor > 2.5
    assert line_factor == pytest.approx(1.0)


# --------------------------------------------------------------------------
# Exercise 3 — dual axes
# --------------------------------------------------------------------------


def _dual(a, b, ylim_a, ylim_b, invert_b=False):
    if invert_b:
        ylim_b = (ylim_b[1], ylim_b[0])
    fig, ax, ax2 = H.dual_axis_figure(a, b, ylim_a=ylim_a, ylim_b=ylim_b)
    try:
        fig.canvas.draw()
        trace_a = H.drawn_trace(ax)
        trace_b = H.drawn_trace(ax2)
        return H.tracking_gap(trace_a, trace_b), H.pearson(trace_a, trace_b)
    finally:
        plt.close(fig)


def test_the_demonstration_pair_really_is_uncorrelated():
    a, b = H.uncorrelated_pair()
    assert abs(H.pearson(a, b)) < 0.01


def test_pearson_matches_numpy_on_the_same_data():
    a, b = H.uncorrelated_pair()
    assert H.pearson(a, b) == pytest.approx(float(np.corrcoef(a, b)[0, 1]))


def test_axis_scaling_cannot_change_the_drawn_correlation():
    a, b = H.uncorrelated_pair()
    data_r = H.pearson(a, b)
    rng = np.random.default_rng(1132)
    for _ in range(40):
        factor_a = float(rng.uniform(0.5, 50.0))
        factor_b = float(rng.uniform(0.5, 50.0))
        _, drawn_r = _dual(
            a, b, H.widened_limits(a, factor_a), H.widened_limits(b, factor_b)
        )
        assert drawn_r == pytest.approx(data_r, abs=1e-12)


def test_inverting_one_axis_negates_the_drawn_correlation_exactly():
    c, d = H.correlated_pair()
    data_r = H.pearson(c, d)
    assert data_r > 0.85
    _, drawn_r = _dual(
        c, d, H.matched_limits(c), H.matched_limits(d), invert_b=True
    )
    assert drawn_r == pytest.approx(-data_r, abs=1e-12)


def test_the_tracking_gap_is_a_free_parameter():
    a, b = H.uncorrelated_pair()
    gap_apart, _ = _dual(
        a, b, H.banded_limits(a, 0.55, 0.95), H.banded_limits(b, 0.05, 0.45)
    )
    gap_wide, _ = _dual(a, b, H.widened_limits(a), H.widened_limits(b))
    assert gap_apart > 0.4
    assert gap_wide < 0.05
    assert gap_apart > 10 * gap_wide


def test_overlap_carries_no_information_about_correlation():
    """The centrepiece. The same widening drives BOTH an uncorrelated pair
    and a strongly correlated pair to overlapping curves, so a reader who
    concludes 'these track' from the picture has learned nothing."""
    a, b = H.uncorrelated_pair()
    c, d = H.correlated_pair()
    gap_uncorrelated, _ = _dual(a, b, H.widened_limits(a), H.widened_limits(b))
    gap_correlated, _ = _dual(c, d, H.widened_limits(c), H.widened_limits(d))
    assert abs(H.pearson(a, b)) < 0.01
    assert H.pearson(c, d) > 0.85
    assert gap_uncorrelated < 0.05
    assert gap_correlated < 0.05


def test_twinx_really_produced_a_second_independent_axes():
    a, b = H.uncorrelated_pair()
    fig, ax, ax2 = H.dual_axis_figure(a, b, ylim_a=(0, 100), ylim_b=(0, 1))
    try:
        assert ax is not ax2
        assert ax.get_ylim() == (0.0, 100.0)
        assert ax2.get_ylim() == (0.0, 1.0)
        assert len(ax.lines) == 1 and len(ax2.lines) == 1
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# Exercise 4 — cherry-picked windows
# --------------------------------------------------------------------------


def test_trend_slope_recovers_a_known_slope():
    y = 3.0 + 2.5 * np.arange(20)
    assert H.trend_slope(y) == pytest.approx(2.5)


def test_the_trend_sign_flips_between_the_two_halves():
    values = H.dipping_series()
    half = len(values) // 2
    first = H.trend_slope(values[:half])
    second = H.trend_slope(values[half:])
    assert first < 0 < second
    assert abs(first) > 0.5 and abs(second) > 0.5


def test_the_full_series_is_flat():
    values = H.dipping_series()
    assert abs(H.trend_slope(values)) < 0.05


# --------------------------------------------------------------------------
# Exercise 5 — binning
# --------------------------------------------------------------------------


def test_count_modes_counts_strict_local_maxima():
    assert H.count_modes([1, 5, 2]) == 1
    assert H.count_modes([5, 1, 5]) == 2
    assert H.count_modes([1, 2, 3, 4]) == 1
    assert H.count_modes([3, 3, 3]) == 0


def test_two_textbook_bin_rules_give_opposite_answers():
    sample = H.bimodal_sample()
    sturges = H.histogram_counts(sample, bins="sturges")
    freedman = H.histogram_counts(sample, bins="fd")
    assert H.count_modes(sturges) == 1
    assert H.count_modes(freedman) == 2
    assert len(sturges) == 10
    assert len(freedman) == 14


def test_the_sturges_histogram_really_reads_as_one_hump():
    """Not merely 'one strict local maximum' -- the counts rise to a peak
    and fall away from it with no interior dip at all, so a reader looking
    at the picture would call it unimodal too."""
    counts = H.histogram_counts(H.bimodal_sample(), bins="sturges")
    peak = int(np.argmax(counts))
    assert all(counts[i] <= counts[i + 1] for i in range(peak))
    assert all(counts[i] >= counts[i + 1] for i in range(peak, len(counts) - 1))


def test_histogram_counts_conserve_the_sample():
    sample = H.bimodal_sample()
    assert sum(H.histogram_counts(sample, bins="fd")) == len(sample)


# --------------------------------------------------------------------------
# Exercise 6 — radius versus area
# --------------------------------------------------------------------------


def _area_ratio(values, encode):
    fig, ax = H.bubble_pair(values, encode=encode)
    try:
        fig.canvas.draw()
        return H.drawn_area_ratio(ax)
    finally:
        plt.close(fig)


def test_encoding_by_area_is_faithful():
    ratio = _area_ratio((25.0, 100.0), "area")
    assert ratio == pytest.approx(4.0)
    assert H.lie_factor(ratio, 4.0) == pytest.approx(1.0)


def test_encoding_by_radius_squares_the_shown_ratio():
    data_ratio = 4.0
    ratio = _area_ratio((25.0, 100.0), "radius")
    assert ratio == pytest.approx(data_ratio**2)
    assert H.lie_factor(ratio, data_ratio) == pytest.approx(data_ratio)


def test_the_radius_distortion_grows_with_the_real_difference():
    for values in ((10.0, 20.0), (10.0, 50.0), (10.0, 100.0)):
        data_ratio = values[1] / values[0]
        ratio = _area_ratio(values, "radius")
        assert H.lie_factor(ratio, data_ratio) == pytest.approx(data_ratio, rel=1e-6)


def test_bubble_pair_rejects_an_unknown_encoding():
    with pytest.raises(ValueError):
        H.bubble_pair((1.0, 2.0), encode="diameter")


# --------------------------------------------------------------------------
# Exercise 7 — 3D perspective
# --------------------------------------------------------------------------


def test_flat_bars_reproduce_the_data_ratio_exactly():
    fig, ax = H.bar_pair((1.0, 2.0))
    try:
        fig.canvas.draw()
        heights = H.drawn_bar_heights(ax)
    finally:
        plt.close(fig)
    assert heights[1] / heights[0] == pytest.approx(2.0)


def test_perspective_departs_from_the_data_ratio_by_more_than_ten_percent():
    areas = H.bar3d_projected_areas([1.0, 2.0], [0.0, 3.0])
    ratio = areas[1] / areas[0]
    assert abs(ratio / 2.0 - 1.0) > 0.10
    assert ratio == pytest.approx(2.341, abs=0.02)


def test_moving_the_taller_bar_nearer_makes_the_distortion_much_worse():
    far = H.bar3d_projected_areas([1.0, 2.0], [0.0, 3.0])
    near = H.bar3d_projected_areas([1.0, 2.0], [3.0, 0.0])
    assert near[1] / near[0] > far[1] / far[0]
    assert near[1] / near[0] > 4.0


def test_polygon_area_matches_a_known_square():
    assert H._polygon_area([(0, 0), (2, 0), (2, 3), (0, 3)]) == pytest.approx(6.0)


# --------------------------------------------------------------------------
# Exercise 8 — ordering, annotation, emphasis
# --------------------------------------------------------------------------


def test_sorting_removes_every_comparison_needed_to_find_the_maximum():
    values = [41.0, 88.0, 37.0, 52.0, 63.0]
    assert H.comparisons_to_find_max(values) == 4
    assert H.comparisons_to_find_max(sorted(values, reverse=True)) == 0


def test_the_annotated_chart_sorts_its_bars_and_carries_its_claim():
    claim = "south is 39% higher than the next region"
    fig, ax = H.annotated_bar_chart(
        ["north", "south", "east", "west", "central"],
        [41.0, 88.0, 37.0, 52.0, 63.0],
        claim,
    )
    try:
        fig.canvas.draw()
        text = H.axes_text(ax)
        labels = [t.get_text() for t in ax.get_xticklabels()]
    finally:
        plt.close(fig)
    assert labels == ["south", "central", "west", "north", "east"]
    assert claim in text
    assert text.count(claim) == 2
    assert "value" in text


def test_relative_luminance_matches_the_wcag_endpoints():
    assert H.relative_luminance("#000000") == pytest.approx(0.0)
    assert H.relative_luminance("#ffffff") == pytest.approx(1.0)


def test_red_and_green_collapse_where_deliberate_emphasis_does_not():
    red_green = H.luminance_separation(H.CLASSIC_RED, H.CLASSIC_GREEN)
    emphasis = H.luminance_separation(H.HIGHLIGHT, H.MUTED)
    assert red_green < 0.11
    assert emphasis > 0.5
    assert emphasis > 5 * red_green


def test_seabornes_colorblind_palette_separates_better_than_red_green():
    import seaborn as sns

    first, second = sns.color_palette("colorblind").as_hex()[:2]
    assert H.luminance_separation(first, second) > H.luminance_separation(
        H.CLASSIC_RED, H.CLASSIC_GREEN
    )


# --------------------------------------------------------------------------
# Exercise 9 — the caption contract
# --------------------------------------------------------------------------


def test_the_contract_passes_an_honest_chart():
    fig, ax = H.bar_pair((100.0, 102.0))
    try:
        fig.canvas.draw()
        passed, failures = H.review_chart(ax, "Group B is 2% higher than group A.")
    finally:
        plt.close(fig)
    assert passed, failures
    assert failures == []


def test_the_contract_fails_the_truncated_chart():
    fig, ax = H.bar_pair((100.0, 102.0), ylim=(99, 103))
    try:
        fig.canvas.draw()
        passed, failures = H.review_chart(ax, "Group B is 2% higher than group A.")
    finally:
        plt.close(fig)
    assert not passed
    assert any("does not say so" in f for f in failures)
    assert any("without disclosure" in f for f in failures)


def test_the_contract_passes_a_disclosed_rule_break():
    fig, ax = H.line_pair((100.0, 102.0), ylim=(99, 103))
    try:
        fig.canvas.draw()
        passed, failures = H.review_chart(
            ax,
            "Group B is 2% higher than group A. Note: the y axis starts at "
            "99, not zero.",
        )
    finally:
        plt.close(fig)
    assert passed, failures


def test_the_contract_fails_an_accurate_but_silent_chart():
    fig, ax = H.bar_pair((100.0, 102.0))
    ax.set_ylabel("")
    try:
        fig.canvas.draw()
        passed, failures = H.review_chart(ax, "Results.")
    finally:
        plt.close(fig)
    assert not passed
    assert len(failures) == 2
    assert any("no claim" in f for f in failures)
    assert any("no label" in f for f in failures)


def test_an_empty_caption_is_reported_as_its_own_failure():
    fig, ax = H.bar_pair((100.0, 102.0))
    try:
        fig.canvas.draw()
        passed, failures = H.review_chart(ax, "")
    finally:
        plt.close(fig)
    assert not passed
    assert any("caption is empty" in f for f in failures)


# --------------------------------------------------------------------------
# The lab's own hygiene
# --------------------------------------------------------------------------


def test_no_figures_are_left_open_by_the_helper_functions():
    plt.close("all")
    H.bar_pair_lie_factor((100.0, 102.0))
    H.line_pair_lie_factor((100.0, 102.0))
    H.histogram_counts(H.bimodal_sample(), bins="fd")
    H.bar3d_projected_areas([1.0, 2.0], [0.0, 3.0])
    assert plt.get_fignums() == []
