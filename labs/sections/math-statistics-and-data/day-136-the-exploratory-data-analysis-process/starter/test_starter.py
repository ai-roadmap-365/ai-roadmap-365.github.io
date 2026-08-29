"""Your running score. Unattempted work SKIPS; wrong work FAILS with both
values.

Run from the lab directory:

    .venv/bin/pytest starter -q

On an untouched checkout this reports one pass and everything else skipped.
A skip means "not attempted". A failure means "attempted and wrong", and the
message shows your answer next to the real one so you can see the gap rather
than guess at it.
"""

import numpy as np
import pytest

import dataset as ds
import exploration as ex


def attempt(fn, what):
    """Call something that may not be written yet, and skip if it is not."""
    try:
        result = fn()
    except NotImplementedError:
        pytest.skip(f"not attempted yet: {what}")
    if result is None:
        pytest.skip(f"not attempted yet: {what}")
    return result


def test_the_suite_itself_runs():
    """One test that always passes, so a green run is distinguishable from a
    collection error that quietly ran nothing at all."""
    assert ds.ALPHA == 0.05


# --------------------------------------------------------------------------
# The z-test machinery
# --------------------------------------------------------------------------


def test_phi_of_zero_is_one_half():
    result = attempt(lambda: ex.phi(0.0), "phi")
    assert result == pytest.approx(0.5), f"phi(0.0) should be 0.5, got {result}"


def test_two_sample_z_test_matches_hand_computation():
    a = [50, 52, 49, 51, 53, 48, 50, 52, 51, 49]
    b = [54, 55, 53, 56, 54, 52, 55, 53, 54, 56]
    z, p = attempt(lambda: ex.two_sample_z_test(a, b), "two_sample_z_test")
    import math
    import statistics

    mean_a, var_a = statistics.mean(a), statistics.variance(a)
    mean_b, var_b = statistics.mean(b), statistics.variance(b)
    se = math.sqrt(var_a / len(a) + var_b / len(b))
    z_hand = (mean_a - mean_b) / se
    assert z == pytest.approx(z_hand, abs=1e-6), f"expected z={z_hand}, got {z}"
    assert p < 0.001


def test_cohens_d_of_identical_samples_is_zero():
    a = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = attempt(lambda: ex.cohens_d(a, a), "cohens_d")
    assert result == pytest.approx(0.0), f"expected 0.0, got {result}"


# --------------------------------------------------------------------------
# Exercise 1 -- forking paths, measured
# --------------------------------------------------------------------------


def test_1_simulated_forking_paths_matches_exact():
    rng = np.random.default_rng(3)

    def run():
        return ex.simulate_forking_paths(rng, 20, 1500, 200, 0.05)

    result = attempt(run, "simulate_forking_paths")
    dev, se = result["deviation"], result["standard_error"]
    assert dev <= 3 * se, f"simulated {result['simulated_rate']} too far from exact {result['exact_rate']}"


# --------------------------------------------------------------------------
# Exercise 2 -- a plausible story for noise
# --------------------------------------------------------------------------


def test_2_scan_and_best_significant_result():
    rng = np.random.default_rng(ds.NARRATIVE_SEED)
    df = ds.build_narrative_frame(rng)

    def run_scan():
        return ex.scan_narrative_frame(df, ds.NARRATIVE_SUBSET_COLS, ds.NARRATIVE_OUTCOME_COLS)

    results = attempt(run_scan, "scan_narrative_frame")
    assert len(results) >= ds.NARRATIVE_MIN_COMPARISONS

    def run_best():
        return ex.best_significant_result(results)

    best = attempt(run_best, "best_significant_result")
    assert best is not None and best["p"] < 0.05
    assert abs(best["effect_size"]) >= ds.PUBLISHABLE_EFFECT_SIZE


# --------------------------------------------------------------------------
# Exercise 3 -- the holdout rescues you
# --------------------------------------------------------------------------


def test_3_holdout_rescues_the_real_effect_only():
    rng = np.random.default_rng(ds.HOLDOUT_SEED)

    def run_build():
        return ex.build_holdout_frame(rng, ds.HOLDOUT_N_TOTAL, ds.REAL_EFFECT_DELTA, ds.REAL_EFFECT_SIGMA, ds.N_SPURIOUS_CANDIDATES)

    df = attempt(run_build, "build_holdout_frame")

    def run_split():
        return ex.split_exploration_confirmation(df, rng)

    exploration_df, confirmation_df = attempt(run_split, "split_exploration_confirmation")

    def run_real_exp():
        return ex.test_column_by_group(exploration_df, "real_metric")

    _, p_real_exp = attempt(run_real_exp, "test_column_by_group")

    def run_real_conf():
        return ex.test_column_by_group(confirmation_df, "real_metric")

    _, p_real_conf = attempt(run_real_conf, "test_column_by_group")
    assert p_real_exp < 0.05 and p_real_conf < 0.05

    spurious_cols = [c for c in df.columns if c.startswith("spurious_")]

    def run_best_spurious():
        return ex.best_spurious_column(exploration_df, spurious_cols)

    best_col, _, p_spur_exp = attempt(run_best_spurious, "best_spurious_column")
    _, p_spur_conf = ex.test_column_by_group(confirmation_df, best_col)
    assert p_spur_exp < 0.05
    assert p_spur_conf >= 0.05


# --------------------------------------------------------------------------
# Exercise 4 -- choices are comparisons
# --------------------------------------------------------------------------


def test_4_choice_grid_inflates_significance():
    rng = np.random.default_rng(ds.CHOICES_SEED)

    def run():
        return ex.simulate_choice_grid_best_p_rate(
            rng, 1200, ds.CHOICES_N_ROWS, ds.CHOICES_SUBSET_CUTOFFS, ds.CHOICES_OUTCOME_DEFINITIONS, ds.ALPHA
        )

    result = attempt(run, "simulate_choice_grid_best_p_rate")
    assert result["naive_best_rate"] > 3 * ds.ALPHA
    assert abs(result["single_declared_rate"] - ds.ALPHA) < 0.03


# --------------------------------------------------------------------------
# Exercise 5 -- Bonferroni, and its limit
# --------------------------------------------------------------------------


def test_5_bonferroni_alpha_divides_by_m():
    result = attempt(lambda: ex.bonferroni_alpha(0.05, 20), "bonferroni_alpha")
    assert result == pytest.approx(0.0025), f"expected 0.05/20=0.0025, got {result}"


def test_5_bonferroni_fails_with_wrong_m():
    rng = np.random.default_rng(12)

    def run_alpha():
        return ex.bonferroni_alpha(ds.ALPHA, ds.BONFERRONI_KNOWN_M)

    corrected = attempt(run_alpha, "bonferroni_alpha")

    def run_right():
        return ex.simulate_family_wise_rate(rng, ds.BONFERRONI_KNOWN_M, 8000, corrected)

    rate_right = attempt(run_right, "simulate_family_wise_rate")

    def run_wrong():
        return ex.simulate_family_wise_rate(rng, ds.BONFERRONI_TRUE_M, 8000, corrected)

    rate_wrong = attempt(run_wrong, "simulate_family_wise_rate")
    assert rate_wrong > rate_right
    assert rate_wrong > 2 * ds.ALPHA


# --------------------------------------------------------------------------
# Exercise 6 -- the research log
# --------------------------------------------------------------------------


def test_6_research_log_records_everything():
    def run():
        log = ex.ResearchLog()
        log.record("q1", "look1", None)
        log.record("q2", "look2", "p=0.01")
        return log

    log = attempt(run, "ResearchLog.record")
    assert log.comparison_count == 2, f"expected comparison_count=2, got {log.comparison_count}"
    assert log.null_count == 1, f"expected null_count=1, got {log.null_count}"
    assert len(log.findings()) == 1


# --------------------------------------------------------------------------
# Exercise 7 -- triage
# --------------------------------------------------------------------------


def test_7_triage_rewards_cheap_and_relevant():
    cheap_relevant = ex.Candidate("a", expected_information=0.8, cost_hours=2, decision_relevance=0.9)
    expensive_irrelevant = ex.Candidate("b", expected_information=0.9, cost_hours=40, decision_relevance=0.5)

    def run():
        return ex.triage_score(cheap_relevant), ex.triage_score(expensive_irrelevant)

    score_a, score_b = attempt(run, "triage_score")
    assert score_a > score_b, f"expected cheap+relevant to score higher, got {score_a} vs {score_b}"

    def run_rank():
        return ex.rank_candidates([expensive_irrelevant, cheap_relevant])

    ranked = attempt(run_rank, "rank_candidates")
    assert ranked[0].name == "a", f"expected 'a' ranked first, got {[c.name for c in ranked]}"


# --------------------------------------------------------------------------
# Exercise 8 -- a stopping rule
# --------------------------------------------------------------------------


def test_8_stopping_rules_diverge():
    rng = np.random.default_rng(ds.STOPPING_SEED)

    def run_tb():
        return ex.time_boxed_false_positive_rate(rng, 15000, ds.STOPPING_BUDGET_QUESTIONS, ds.ALPHA)

    tb_rate = attempt(run_tb, "time_boxed_false_positive_rate")

    def run_sw():
        return ex.stop_when_significant_rate(rng, 15000, ds.STOPPING_BUDGET_QUESTIONS, ds.ALPHA)

    sw_rate = attempt(run_sw, "stop_when_significant_rate")
    assert abs(tb_rate - ds.ALPHA) < 0.02, f"expected time-boxed rate near {ds.ALPHA}, got {tb_rate}"
    assert sw_rate > 3 * ds.ALPHA, f"expected stop-when-significant rate well above {ds.ALPHA}, got {sw_rate}"


# --------------------------------------------------------------------------
# Exercise 9 -- the handoff to Day 133
# --------------------------------------------------------------------------


def test_9_handoff_accepts_complete_and_refuses_incomplete():
    def run_build():
        return ex.build_handoff({"name": "x", "p": 0.01}, {"p": 0.02}, 10)

    handoff = attempt(run_build, "build_handoff")
    assert handoff["comparison_count"] == 10

    def run_validate_should_raise():
        try:
            ex.validate_handoff({"finding": {"name": "x"}})
        except ValueError:
            return "raised"
        except NotImplementedError:
            raise
        return None

    outcome = attempt(run_validate_should_raise, "validate_handoff")
    assert outcome == "raised", "validate_handoff should raise ValueError on a handoff missing fields"

    def run_report():
        return ex.write_report_stub(handoff)

    text = attempt(run_report, "write_report_stub")
    assert "10" in text, f"expected the comparison count in the report text, got: {text}"
