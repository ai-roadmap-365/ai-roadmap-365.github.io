"""Grouped by what the retrospective computes.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from retro import (  # noqa: E402
    Caught,
    Incident,
    Task,
    apply_multiplier,
    by_area,
    calibration,
    detection,
    findings,
    is_uniform,
    median,
)


def tasks_uniform():
    return [
        Task("a", "backend", 4, 8),
        Task("b", "backend", 6, 12),
        Task("c", "frontend", 5, 10),
        Task("d", "frontend", 3, 6),
    ]


def tasks_concentrated():
    return [
        Task("a", "familiar", 8, 9),
        Task("b", "familiar", 6, 7),
        Task("c", "unfamiliar", 6, 20),
        Task("d", "unfamiliar", 8, 26),
    ]


# ------------------------------------------------------------------- median


def test_median_ignores_one_extreme_task():
    # A single 8x task would drag a mean far above what most tasks did.
    values = [1.0, 1.1, 1.2, 1.3, 8.0]
    assert median(values) == 1.2
    assert sum(values) / len(values) > 2.0


def test_median_of_an_even_count_averages_the_middle_two():
    assert median([1.0, 2.0, 3.0, 4.0]) == 2.5


def test_median_of_nothing_is_zero():
    assert median([]) == 0.0


# -------------------------------------------------------------- calibration


def test_ratio_is_actual_over_estimated():
    assert Task("t", "a", 4, 8).ratio == 2.0
    assert Task("t", "a", 8, 4).ratio == 0.5


def test_a_zero_estimate_does_not_divide_by_zero():
    assert Task("t", "a", 0, 5).ratio == 0.0


def test_calibration_counts_direction_not_just_size():
    # Direction is the part that transfers. Uniformly over is a multiplier;
    # a mix is a different problem.
    cal = calibration([Task("a", "x", 4, 8), Task("b", "x", 8, 4), Task("c", "x", 4, 4)])
    assert cal.underestimated == 1
    assert cal.overestimated == 1


def test_calibration_names_the_worst_and_best_areas():
    cal = calibration(tasks_concentrated())
    assert cal.worst_area == "unfamiliar"
    assert cal.best_area == "familiar"
    assert cal.worst_area_ratio > cal.best_area_ratio


def test_calibration_of_no_tasks_is_empty_rather_than_an_error():
    cal = calibration([])
    assert cal.median_ratio == 0.0 and cal.worst_area == ""


# ----------------------------------------------------------------- spread


def test_uniform_error_is_recognised():
    assert is_uniform(tasks_uniform())


def test_concentrated_error_is_recognised():
    # THE finding of this lab: a median of 1.20x across the project hides
    # familiar work at 1.15x and unfamiliar work at 3.33x.
    assert not is_uniform(tasks_concentrated())


def test_a_single_area_is_trivially_uniform():
    assert is_uniform([Task("a", "only", 4, 12)])


def test_by_area_reports_a_median_per_area():
    areas = by_area(tasks_concentrated())
    assert set(areas) == {"familiar", "unfamiliar"}
    assert areas["unfamiliar"] > 3.0
    assert areas["familiar"] < 1.3


# ------------------------------------------------------------- multiplier


def test_the_multiplier_applies_your_own_history():
    cal = calibration(tasks_uniform())  # every task ran exactly 2x
    assert cal.median_ratio == 2.0
    assert apply_multiplier(10, cal) == 20.0


# ------------------------------------------------------------- detection


def test_incidents_are_counted_by_where_they_were_caught():
    report = detection(
        [
            Incident("a", Caught.REVIEW),
            Incident("b", Caught.TESTS),
            Incident("c", Caught.USER),
        ]
    )
    assert report.counts[Caught.REVIEW] == 1
    assert report.counts[Caught.USER] == 1


def test_only_production_incidents_count_as_escaped():
    report = detection(
        [
            Incident("caught early", Caught.TESTS),
            Incident("caught in staging", Caught.STAGING),
            Incident("found by a metric", Caught.MONITORING),
            Incident("found by a person", Caught.USER),
        ]
    )
    assert len(report.escaped) == 2
    assert report.escape_rate == 0.5


def test_preventable_escapes_are_separated_out():
    report = detection(
        [
            Incident("spend spike", Caught.MONITORING, preventable_by="a per-request cap"),
            Incident("unknown unknown", Caught.USER),
        ]
    )
    assert len(report.escaped) == 2
    assert len(report.preventable) == 1
    assert report.preventable[0].preventable_by == "a per-request cap"


def test_no_incidents_is_a_zero_escape_rate_not_an_error():
    assert detection([]).escape_rate == 0.0


# -------------------------------------------------------------- findings


def test_findings_state_the_multiplier_when_estimates_ran_long():
    out = findings(tasks_uniform(), [])
    assert any("2.00x" in f and "Multiply" in f for f in out)


def test_findings_call_out_concentrated_error_specifically():
    out = findings(tasks_concentrated(), [])
    assert any("concentrated" in f and "unfamiliar" in f for f in out)
    assert any("single multiplier will not fix this" in f for f in out)


def test_findings_report_padding_when_estimates_were_conservative():
    generous = [Task("a", "x", 10, 5), Task("b", "x", 8, 4)]
    out = findings(generous, [])
    assert any("conservative" in f for f in out)


def test_findings_name_each_preventable_escape():
    out = findings(
        tasks_uniform(),
        [Incident("spend spike", Caught.MONITORING, preventable_by="a per-request cap")],
    )
    assert any("a per-request cap would have caught it" in f for f in out)


def test_a_clean_record_says_so_rather_than_inventing_a_finding():
    clean = [Task("a", "x", 4, 4), Task("b", "x", 6, 6)]
    out = findings(clean, [Incident("caught early", Caught.TESTS)])
    assert out == ["No systematic pattern in the record. Keep the estimates and the gates as they are."]
