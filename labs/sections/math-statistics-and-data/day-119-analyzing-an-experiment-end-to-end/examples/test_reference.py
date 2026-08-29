"""A pytest suite over the reference implementation, independent of the
numbered scripts. Run with `pytest examples -q`.
"""

from pathlib import Path

import pytest

from experiment import (
    crossed_significance,
    effect_size,
    group_summary,
    guardrail_check,
    load_experiment,
    peek_path,
    primary_test,
    segment_analysis,
    srm_check,
    verdict,
)

DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="module")
def rows_a():
    return load_experiment(DATA_DIR / "exp_a.csv")


@pytest.fixture(scope="module")
def rows_b():
    return load_experiment(DATA_DIR / "exp_b.csv")


def test_load_experiment_row_counts(rows_a, rows_b):
    assert len(rows_a) == 16000
    assert len(rows_b) == 20000


def test_load_experiment_rejects_bad_group(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "user_id,group,segment,converted,latency_ms,time_on_page_sec\n"
        "1,not_a_group,desktop,0,200.0,40.0\n"
    )
    with pytest.raises(ValueError):
        load_experiment(bad)


def test_srm_passes_on_a_fails_on_b(rows_a, rows_b):
    srm_a = srm_check(rows_a)
    srm_b = srm_check(rows_b)
    assert srm_a["passed"]
    assert not srm_b["passed"]
    assert srm_b["p_value"] < 0.001


def test_group_summary_mean_exceeds_median_under_outliers(rows_a):
    summary = group_summary(rows_a)
    for group in ("control", "treatment"):
        assert summary[group]["mean"] > summary[group]["median"]


def test_primary_test_excludes_zero_on_a(rows_a):
    result = primary_test(rows_a)
    assert result["excludes_zero"]
    assert result["ci_low"] > 0.0


def test_effect_size_reports_both_numbers(rows_a):
    result = primary_test(rows_a)
    effect = effect_size(result)
    assert effect["relative_lift_pct"] is not None
    assert effect["abs_diff_pp"] > 0


def test_guardrail_passes_on_a(rows_a):
    guardrail = guardrail_check(rows_a)
    assert guardrail["passed"]


def test_guardrail_can_fail_with_a_tight_tolerance(rows_a):
    guardrail = guardrail_check(rows_a, tolerance=-100.0)
    assert not guardrail["passed"]


def test_segment_analysis_flags_reversal_only_on_b(rows_a, rows_b):
    seg_a = segment_analysis(rows_a)
    seg_b = segment_analysis(rows_b)
    assert not seg_a["reversal_flagged"]
    assert seg_b["reversal_flagged"]
    assert seg_b["pooled_diff_pp"] > 0
    assert all(info["diff_pp"] < 0 for info in seg_b["segments"].values())


def test_peek_path_crosses_significance_before_the_end(rows_a):
    path = peek_path(rows_a, checkpoint_every=500)
    assert crossed_significance(path)
    assert path[-1]["significant"]


def test_verdict_ships_a_and_refuses_b(rows_a, rows_b):
    srm_a, srm_b = srm_check(rows_a), srm_check(rows_b)
    primary_a, primary_b = primary_test(rows_a), primary_test(rows_b)
    guard_a, guard_b = guardrail_check(rows_a), guardrail_check(rows_b)
    seg_a, seg_b = segment_analysis(rows_a), segment_analysis(rows_b)

    verdict_a = verdict(srm_a, primary_a, guard_a, seg_a)
    verdict_b = verdict(srm_b, primary_b, guard_b, seg_b)

    assert verdict_a["verdict"] == "ship"
    assert not verdict_a["refused"]
    assert verdict_b["verdict"] == "do not trust this result"
    assert verdict_b["refused"]


def test_verdict_refuses_before_computing_an_estimate(rows_b):
    srm_b = srm_check(rows_b)
    primary_b = primary_test(rows_b)
    guard_b = guardrail_check(rows_b)
    seg_b = segment_analysis(rows_b)
    result = verdict(srm_b, primary_b, guard_b, seg_b)
    assert "estimate_pp" not in result
