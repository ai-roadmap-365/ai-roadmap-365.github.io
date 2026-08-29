"""Starter suite — Day 132. Skips what you have not written yet.

Every test calls one of your functions inside a helper that turns a
NotImplementedError into a SKIP. So a fresh checkout reports skips, not
failures, and the count of skips is your progress bar. A wrong answer
still fails, and prints your value beside the expected one.

Run it from inside starter/:

    ../.venv/bin/pytest . -q
"""

import matplotlib.pyplot as plt
import numpy as np
import pytest

import honesty as H


def attempt(call, *args, **kwargs):
    """Run one of your functions, or skip if it is still a stub."""
    try:
        return call(*args, **kwargs)
    except NotImplementedError:
        pytest.skip(f"{call.__name__} is not written yet")


# --- Exercise 1 ------------------------------------------------------------


def test_ex1_lie_factor_arithmetic():
    assert attempt(H.lie_factor, 3.0, 1.02) == pytest.approx(2.9411764705882355)
    assert attempt(H.lie_factor, 1.02, 1.02) == 1.0


def test_ex1_drawn_bar_heights_read_the_zero_baseline_chart():
    fig, ax = H.bar_pair((100.0, 102.0))
    try:
        fig.canvas.draw()
        heights = attempt(H.drawn_bar_heights, ax)
    finally:
        plt.close(fig)
    assert len(heights) == 2
    assert heights[1] / heights[0] == pytest.approx(1.02)


def test_ex1_drawn_bar_heights_read_the_truncated_chart():
    fig, ax = H.bar_pair((100.0, 102.0), ylim=(99, 103))
    try:
        fig.canvas.draw()
        heights = attempt(H.drawn_bar_heights, ax)
    finally:
        plt.close(fig)
    assert heights[1] / heights[0] == pytest.approx(3.0)


# --- Exercise 2 ------------------------------------------------------------


def test_ex2_a_line_encodes_the_change_whatever_the_baseline():
    for limits in (None, (99, 103), (90, 110)):
        fig, ax = H.line_pair((100.0, 102.0), ylim=limits)
        try:
            fig.canvas.draw()
            change = attempt(H.drawn_change, ax)
        finally:
            plt.close(fig)
        assert change == pytest.approx(2.0), f"ylim={limits}"


# --- Exercise 3 ------------------------------------------------------------


def test_ex3_pearson_matches_numpy():
    a, b = H.uncorrelated_pair()
    assert attempt(H.pearson, a, b) == pytest.approx(float(np.corrcoef(a, b)[0, 1]))


def test_ex3_tracking_gap_is_zero_for_identical_traces():
    trace = np.array([0.1, 0.5, 0.9, 0.3])
    assert attempt(H.tracking_gap, trace, trace) == pytest.approx(0.0)
    assert attempt(H.tracking_gap, trace, trace + 0.2) == pytest.approx(0.2)


def test_ex3_widened_limits_widen_around_the_midpoint():
    low, high = attempt(H.widened_limits, np.array([0.0, 10.0]), 4.0)
    assert (low, high) == pytest.approx((-15.0, 25.0))


def test_ex3_scaling_cannot_change_the_drawn_correlation():
    a, b = H.uncorrelated_pair()
    data_r = attempt(H.pearson, a, b)
    limits_a = attempt(H.widened_limits, a, 20.0)
    limits_b = attempt(H.widened_limits, b, 20.0)
    fig, ax, ax2 = H.dual_axis_figure(a, b, ylim_a=limits_a, ylim_b=limits_b)
    try:
        fig.canvas.draw()
        drawn_r = attempt(H.pearson, H.drawn_trace(ax), H.drawn_trace(ax2))
        gap = attempt(H.tracking_gap, H.drawn_trace(ax), H.drawn_trace(ax2))
    finally:
        plt.close(fig)
    assert drawn_r == pytest.approx(data_r, abs=1e-12)
    assert gap < 0.05


# --- Exercise 4 ------------------------------------------------------------


def test_ex4_trend_slope_recovers_a_known_slope():
    assert attempt(H.trend_slope, 3.0 + 2.5 * np.arange(20)) == pytest.approx(2.5)


def test_ex4_the_trend_sign_flips_between_the_halves():
    values = H.dipping_series()
    half = len(values) // 2
    first = attempt(H.trend_slope, values[:half])
    second = attempt(H.trend_slope, values[half:])
    full = attempt(H.trend_slope, values)
    assert first < 0 < second
    assert abs(full) < 0.05


# --- Exercise 5 ------------------------------------------------------------


def test_ex5_count_modes_counts_strict_local_maxima():
    assert attempt(H.count_modes, [1, 5, 2]) == 1
    assert attempt(H.count_modes, [5, 1, 5]) == 2
    assert attempt(H.count_modes, [1, 2, 3, 4]) == 1
    assert attempt(H.count_modes, [3, 3, 3]) == 0


def test_ex5_two_bin_rules_give_opposite_answers():
    sample = H.bimodal_sample()
    assert attempt(H.count_modes, H.histogram_counts(sample, bins="sturges")) == 1
    assert attempt(H.count_modes, H.histogram_counts(sample, bins="fd")) == 2


# --- Exercise 6 ------------------------------------------------------------


def test_ex6_radius_encoding_squares_the_shown_ratio():
    ratios = {}
    for encoding in ("area", "radius"):
        fig, ax = H.bubble_pair((25.0, 100.0), encode=encoding)
        try:
            fig.canvas.draw()
            ratios[encoding] = attempt(H.drawn_area_ratio, ax)
        finally:
            plt.close(fig)
    assert ratios["area"] == pytest.approx(4.0)
    assert ratios["radius"] == pytest.approx(16.0)
    assert attempt(H.lie_factor, ratios["radius"], 4.0) == pytest.approx(4.0)


# --- Exercise 7 ------------------------------------------------------------


def test_ex7_polygon_area_matches_a_known_rectangle():
    assert attempt(H._polygon_area, [(0, 0), (2, 0), (2, 3), (0, 3)]) == pytest.approx(6.0)


def test_ex7_perspective_departs_from_the_data_ratio():
    areas = attempt(H.bar3d_projected_areas, [1.0, 2.0], [0.0, 3.0])
    ratio = areas[1] / areas[0]
    assert abs(ratio / 2.0 - 1.0) > 0.10


# --- Exercise 8 ------------------------------------------------------------


def test_ex8_sorting_removes_the_comparisons():
    values = [41.0, 88.0, 37.0, 52.0, 63.0]
    assert attempt(H.comparisons_to_find_max, values) == 4
    assert attempt(H.comparisons_to_find_max, sorted(values, reverse=True)) == 0


def test_ex8_the_chart_carries_its_claim_as_retrievable_text():
    claim = "south is 39% higher than the next region"
    fig, ax = H.annotated_bar_chart(
        ["north", "south", "east", "west", "central"],
        [41.0, 88.0, 37.0, 52.0, 63.0],
        claim,
    )
    try:
        fig.canvas.draw()
        text = attempt(H.axes_text, ax)
    finally:
        plt.close(fig)
    assert claim in text
    assert "" not in text


def test_ex8_relative_luminance_and_the_red_green_collapse():
    assert attempt(H.relative_luminance, "#000000") == pytest.approx(0.0)
    assert attempt(H.relative_luminance, "#ffffff") == pytest.approx(1.0)
    red_green = attempt(H.luminance_separation, H.CLASSIC_RED, H.CLASSIC_GREEN)
    emphasis = attempt(H.luminance_separation, H.HIGHLIGHT, H.MUTED)
    assert red_green < 0.11
    assert emphasis > 0.5


# --- Exercise 9 ------------------------------------------------------------


def test_ex9_the_contract_passes_an_honest_chart():
    fig, ax = H.bar_pair((100.0, 102.0))
    try:
        fig.canvas.draw()
        passed, failures = attempt(
            H.review_chart, ax, "Group B is 2% higher than group A."
        )
    finally:
        plt.close(fig)
    assert passed, failures


def test_ex9_the_contract_fails_the_truncated_chart():
    fig, ax = H.bar_pair((100.0, 102.0), ylim=(99, 103))
    try:
        fig.canvas.draw()
        passed, failures = attempt(
            H.review_chart, ax, "Group B is 2% higher than group A."
        )
    finally:
        plt.close(fig)
    assert not passed
    assert any("does not say so" in f for f in failures)
    assert any("without disclosure" in f for f in failures)


def test_ex9_the_contract_passes_a_disclosed_rule_break():
    fig, ax = H.line_pair((100.0, 102.0), ylim=(99, 103))
    try:
        fig.canvas.draw()
        passed, failures = attempt(
            H.review_chart,
            ax,
            "Group B is 2% higher than group A. Note: the y axis starts at "
            "99, not zero.",
        )
    finally:
        plt.close(fig)
    assert passed, failures


def test_ex9_an_accurate_but_silent_chart_still_fails():
    fig, ax = H.bar_pair((100.0, 102.0))
    ax.set_ylabel("")
    try:
        fig.canvas.draw()
        passed, failures = attempt(H.review_chart, ax, "Results.")
    finally:
        plt.close(fig)
    assert not passed
    assert len(failures) == 2
