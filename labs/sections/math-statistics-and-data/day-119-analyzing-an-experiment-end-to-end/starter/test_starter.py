"""Your running score. Unattempted work SKIPS; wrong work FAILS with both
values.

Run from the lab directory:

    .venv/bin/pytest starter -q

On an untouched checkout this reports one pass and everything else skipped.
"""

from pathlib import Path

import pytest

import dataset as D
import experiment as E

DATA_DIR = Path(__file__).parent.parent / "data"


def attempt(fn, what):
    try:
        result = fn()
    except NotImplementedError:
        pytest.skip(f"not attempted yet: {what}")
    return result


def test_the_suite_itself_runs():
    assert D.PLANNED_SPLIT == 0.5


# --------------------------------------------------------------------------
# Exercise 1
# --------------------------------------------------------------------------


def test_1_load_experiment_row_counts():
    rows_a = attempt(lambda: E.load_experiment(DATA_DIR / "exp_a.csv"), "load_experiment")
    rows_b = attempt(lambda: E.load_experiment(DATA_DIR / "exp_b.csv"), "load_experiment")
    assert len(rows_a) == 16000
    assert len(rows_b) == 20000


def test_1_load_experiment_rejects_bad_group(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "user_id,group,segment,converted,latency_ms,time_on_page_sec\n"
        "1,not_a_group,desktop,0,200.0,40.0\n"
    )

    def call():
        return E.load_experiment(bad)

    try:
        call()
    except NotImplementedError:
        pytest.skip("not attempted yet: load_experiment")
    except ValueError:
        return
    pytest.fail("load_experiment should raise ValueError on an invalid group label")


# --------------------------------------------------------------------------
# Exercise 2
# --------------------------------------------------------------------------


def test_2_srm_passes_on_a_fails_on_b():
    rows_a = attempt(lambda: E.load_experiment(DATA_DIR / "exp_a.csv"), "load_experiment")
    rows_b = attempt(lambda: E.load_experiment(DATA_DIR / "exp_b.csv"), "load_experiment")
    srm_a = attempt(lambda: E.srm_check(rows_a), "srm_check")
    srm_b = attempt(lambda: E.srm_check(rows_b), "srm_check")
    assert srm_a["passed"]
    assert not srm_b["passed"]


# --------------------------------------------------------------------------
# Exercise 3
# --------------------------------------------------------------------------


def test_3_mean_exceeds_median_under_outliers():
    rows_a = attempt(lambda: E.load_experiment(DATA_DIR / "exp_a.csv"), "load_experiment")
    summary = attempt(lambda: E.group_summary(rows_a), "group_summary")
    for group in ("control", "treatment"):
        assert summary[group]["mean"] > summary[group]["median"]


# --------------------------------------------------------------------------
# Exercise 4
# --------------------------------------------------------------------------


def test_4_primary_test_excludes_zero_on_a():
    rows_a = attempt(lambda: E.load_experiment(DATA_DIR / "exp_a.csv"), "load_experiment")
    result = attempt(lambda: E.primary_test(rows_a), "primary_test")
    assert result["excludes_zero"]


# --------------------------------------------------------------------------
# Exercise 5
# --------------------------------------------------------------------------


def test_5_effect_size_reports_both_numbers():
    rows_a = attempt(lambda: E.load_experiment(DATA_DIR / "exp_a.csv"), "load_experiment")
    result = attempt(lambda: E.primary_test(rows_a), "primary_test")
    effect = attempt(lambda: E.effect_size(result), "effect_size")
    assert "abs_diff_pp" in effect and "relative_lift_pct" in effect


# --------------------------------------------------------------------------
# Exercise 6
# --------------------------------------------------------------------------


def test_6_guardrail_passes_on_a():
    rows_a = attempt(lambda: E.load_experiment(DATA_DIR / "exp_a.csv"), "load_experiment")
    guardrail = attempt(lambda: E.guardrail_check(rows_a), "guardrail_check")
    assert guardrail["passed"]


# --------------------------------------------------------------------------
# Exercise 7
# --------------------------------------------------------------------------


def test_7_segment_analysis_flags_reversal_only_on_b():
    rows_a = attempt(lambda: E.load_experiment(DATA_DIR / "exp_a.csv"), "load_experiment")
    rows_b = attempt(lambda: E.load_experiment(DATA_DIR / "exp_b.csv"), "load_experiment")
    seg_a = attempt(lambda: E.segment_analysis(rows_a), "segment_analysis")
    seg_b = attempt(lambda: E.segment_analysis(rows_b), "segment_analysis")
    assert not seg_a["reversal_flagged"]
    assert seg_b["reversal_flagged"]


# --------------------------------------------------------------------------
# Exercise 8
# --------------------------------------------------------------------------


def test_8_peek_path_crosses_significance_before_the_end():
    rows_a = attempt(lambda: E.load_experiment(DATA_DIR / "exp_a.csv"), "load_experiment")
    path = attempt(lambda: E.peek_path(rows_a, checkpoint_every=500), "peek_path")
    crossed = attempt(lambda: E.crossed_significance(path), "crossed_significance")
    assert crossed
    assert path[-1]["significant"]


# --------------------------------------------------------------------------
# Exercise 9
# --------------------------------------------------------------------------


def test_9_verdict_ships_a_and_refuses_b():
    rows_a = attempt(lambda: E.load_experiment(DATA_DIR / "exp_a.csv"), "load_experiment")
    rows_b = attempt(lambda: E.load_experiment(DATA_DIR / "exp_b.csv"), "load_experiment")
    srm_a, srm_b = attempt(lambda: E.srm_check(rows_a), "srm_check"), attempt(
        lambda: E.srm_check(rows_b), "srm_check"
    )
    primary_a, primary_b = attempt(lambda: E.primary_test(rows_a), "primary_test"), attempt(
        lambda: E.primary_test(rows_b), "primary_test"
    )
    guard_a, guard_b = attempt(lambda: E.guardrail_check(rows_a), "guardrail_check"), attempt(
        lambda: E.guardrail_check(rows_b), "guardrail_check"
    )
    seg_a, seg_b = attempt(lambda: E.segment_analysis(rows_a), "segment_analysis"), attempt(
        lambda: E.segment_analysis(rows_b), "segment_analysis"
    )

    verdict_a = attempt(lambda: E.verdict(srm_a, primary_a, guard_a, seg_a), "verdict")
    verdict_b = attempt(lambda: E.verdict(srm_b, primary_b, guard_b, seg_b), "verdict")

    assert verdict_a["verdict"] == "ship"
    assert verdict_b["verdict"] == "do not trust this result"
    assert verdict_b["refused"]
    assert "estimate_pp" not in verdict_b
