"""The reference pytest suite -- real values, real exceptions, one test per
claim the nine scripts make. Run from the lab directory:

    .venv/bin/pytest examples -q -p no:cacheprovider
"""
import math

import numpy as np
import pytest

import dataset as ds
import exploration as ex


# --------------------------------------------------------------------------
# The z-test machinery (reused from Day 118)
# --------------------------------------------------------------------------


def test_phi_of_zero_is_one_half():
    assert ex.phi(0.0) == pytest.approx(0.5)


def test_z_critical_two_sided_matches_known_constant():
    assert ex.z_critical_two_sided(0.05) == pytest.approx(1.959964, abs=1e-4)


def test_two_sample_z_test_matches_hand_computation():
    a = [50, 52, 49, 51, 53, 48, 50, 52, 51, 49]
    b = [54, 55, 53, 56, 54, 52, 55, 53, 54, 56]
    z, p = ex.two_sample_z_test(a, b)
    import statistics

    mean_a, var_a = statistics.mean(a), statistics.variance(a)
    mean_b, var_b = statistics.mean(b), statistics.variance(b)
    se = math.sqrt(var_a / len(a) + var_b / len(b))
    z_hand = (mean_a - mean_b) / se
    assert z == pytest.approx(z_hand, abs=1e-9)
    assert p < 0.001


def test_cohens_d_of_identical_samples_is_zero():
    a = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert ex.cohens_d(a, a) == pytest.approx(0.0)


# --------------------------------------------------------------------------
# Exercise 1 -- forking paths, measured
# --------------------------------------------------------------------------


def test_exact_fwer_matches_known_values():
    assert abs((1 - (1 - 0.05) ** 5) - 0.2262) < 0.0001
    assert abs((1 - (1 - 0.05) ** 20) - 0.6415) < 0.0001
    assert abs((1 - (1 - 0.05) ** 40) - 0.8715) < 0.0001


def test_simulated_forking_paths_matches_exact_within_tolerance():
    rng = np.random.default_rng(3)
    for k in ds.FORK_K_VALUES:
        result = ex.simulate_forking_paths(rng, k, 1500, 200, ds.ALPHA)
        assert result["deviation"] <= ds.FORK_SIM_TOLERANCE_SE * result["standard_error"], (
            f"k={k}: simulated {result['simulated_rate']} too far from exact {result['exact_rate']}"
        )


def test_narrative_scan_runs_at_least_forty_comparisons():
    rng = np.random.default_rng(ds.NARRATIVE_SEED)
    df = ds.build_narrative_frame(rng)
    results = ex.scan_narrative_frame(df, ds.NARRATIVE_SUBSET_COLS, ds.NARRATIVE_OUTCOME_COLS)
    assert len(results) >= ds.NARRATIVE_MIN_COMPARISONS


def test_narrative_scan_finds_at_least_one_significant_result():
    rng = np.random.default_rng(ds.NARRATIVE_SEED)
    df = ds.build_narrative_frame(rng)
    results = ex.scan_narrative_frame(df, ds.NARRATIVE_SUBSET_COLS, ds.NARRATIVE_OUTCOME_COLS)
    best = ex.best_significant_result(results)
    assert best is not None
    assert best["p"] < ds.ALPHA


# --------------------------------------------------------------------------
# Exercise 2 -- a plausible story for noise
# --------------------------------------------------------------------------


def test_winning_comparison_looks_publishable():
    rng = np.random.default_rng(ds.NARRATIVE_SEED)
    df = ds.build_narrative_frame(rng)
    results = ex.scan_narrative_frame(df, ds.NARRATIVE_SUBSET_COLS, ds.NARRATIVE_OUTCOME_COLS)
    best = ex.best_significant_result(results)
    assert abs(best["effect_size"]) >= ds.PUBLISHABLE_EFFECT_SIZE


# --------------------------------------------------------------------------
# Exercise 3 -- the holdout rescues you
# --------------------------------------------------------------------------


def test_real_effect_survives_confirmation():
    rng = np.random.default_rng(ds.HOLDOUT_SEED)
    df = ex.build_holdout_frame(rng, ds.HOLDOUT_N_TOTAL, ds.REAL_EFFECT_DELTA, ds.REAL_EFFECT_SIGMA, ds.N_SPURIOUS_CANDIDATES)
    exploration_df, confirmation_df = ex.split_exploration_confirmation(df, rng)
    _, p_exp = ex.test_column_by_group(exploration_df, "real_metric")
    _, p_conf = ex.test_column_by_group(confirmation_df, "real_metric")
    assert p_exp < ds.ALPHA
    assert p_conf < ds.ALPHA


def test_spurious_finding_does_not_survive_confirmation():
    rng = np.random.default_rng(ds.HOLDOUT_SEED)
    df = ex.build_holdout_frame(rng, ds.HOLDOUT_N_TOTAL, ds.REAL_EFFECT_DELTA, ds.REAL_EFFECT_SIGMA, ds.N_SPURIOUS_CANDIDATES)
    exploration_df, confirmation_df = ex.split_exploration_confirmation(df, rng)
    spurious_cols = [c for c in df.columns if c.startswith("spurious_")]
    best_col, _, p_exp = ex.best_spurious_column(exploration_df, spurious_cols)
    _, p_conf = ex.test_column_by_group(confirmation_df, best_col)
    assert p_exp < ds.ALPHA
    assert p_conf >= ds.ALPHA


# --------------------------------------------------------------------------
# Exercise 4 -- choices are comparisons
# --------------------------------------------------------------------------


def test_choice_grid_inflates_significance_rate():
    rng = np.random.default_rng(ds.CHOICES_SEED)
    result = ex.simulate_choice_grid_best_p_rate(
        rng, 1200, ds.CHOICES_N_ROWS, ds.CHOICES_SUBSET_CUTOFFS, ds.CHOICES_OUTCOME_DEFINITIONS, ds.ALPHA
    )
    assert result["naive_best_rate"] > 3 * ds.ALPHA
    assert abs(result["single_declared_rate"] - ds.ALPHA) < 0.03


# --------------------------------------------------------------------------
# Exercise 5 -- Bonferroni, and its limit
# --------------------------------------------------------------------------


def test_bonferroni_alpha_divides_by_m():
    assert ex.bonferroni_alpha(0.05, 20) == pytest.approx(0.0025)


def test_bonferroni_restores_nominal_rate_when_m_is_known():
    rng = np.random.default_rng(11)
    corrected = ex.bonferroni_alpha(ds.ALPHA, ds.BONFERRONI_KNOWN_M)
    rate = ex.simulate_family_wise_rate(rng, ds.BONFERRONI_KNOWN_M, 8000, corrected)
    assert abs(rate - ds.ALPHA) < 0.02


def test_bonferroni_fails_when_true_m_exceeds_reported_m():
    rng = np.random.default_rng(12)
    corrected = ex.bonferroni_alpha(ds.ALPHA, ds.BONFERRONI_KNOWN_M)
    rate_right = ex.simulate_family_wise_rate(rng, ds.BONFERRONI_KNOWN_M, 8000, corrected)
    rate_wrong = ex.simulate_family_wise_rate(rng, ds.BONFERRONI_TRUE_M, 8000, corrected)
    assert rate_wrong > rate_right
    assert rate_wrong > 2 * ds.ALPHA


# --------------------------------------------------------------------------
# Exercise 6 -- the research log
# --------------------------------------------------------------------------


def test_log_records_timestamp_look_and_outcome():
    log = ex.ResearchLog()
    log.record("q1", "look1", None)
    log.record("q2", "look2", "p=0.01")
    assert log.comparison_count == 2
    assert all(e.timestamp for e in log.entries)
    assert all(e.look for e in log.entries)
    assert log.null_count == 1
    assert len(log.findings()) == 1


def test_log_comparison_count_matches_comparisons_actually_run():
    rng = np.random.default_rng(ds.NARRATIVE_SEED)
    df = ds.build_narrative_frame(rng)
    results = ex.scan_narrative_frame(df, ds.NARRATIVE_SUBSET_COLS, ds.NARRATIVE_OUTCOME_COLS)
    log = ex.ResearchLog()
    for r in results:
        log.record("q", "look", "found" if r["significant"] else None)
    assert log.comparison_count == len(results)


# --------------------------------------------------------------------------
# Exercise 7 -- triage
# --------------------------------------------------------------------------


def test_triage_score_rewards_cheap_and_relevant():
    cheap_relevant = ex.Candidate("a", expected_information=0.8, cost_hours=2, decision_relevance=0.9)
    expensive_irrelevant = ex.Candidate("b", expected_information=0.9, cost_hours=40, decision_relevance=0.5)
    assert ex.triage_score(cheap_relevant) > ex.triage_score(expensive_irrelevant)


def test_rank_candidates_orders_descending_by_score():
    candidates = [
        ex.Candidate("low", expected_information=0.1, cost_hours=10, decision_relevance=0.1),
        ex.Candidate("high", expected_information=0.9, cost_hours=1, decision_relevance=0.9),
    ]
    ranked = ex.rank_candidates(candidates)
    assert ranked[0].name == "high"
    assert ranked[1].name == "low"


# --------------------------------------------------------------------------
# Exercise 8 -- a stopping rule
# --------------------------------------------------------------------------


def test_time_boxed_rate_sits_near_nominal_alpha():
    rng = np.random.default_rng(ds.STOPPING_SEED)
    rate = ex.time_boxed_false_positive_rate(rng, 15000, ds.STOPPING_BUDGET_QUESTIONS, ds.ALPHA)
    assert abs(rate - ds.ALPHA) < 0.02


def test_stop_when_significant_rate_is_much_higher():
    rng = np.random.default_rng(ds.STOPPING_SEED)
    tb_rate = ex.time_boxed_false_positive_rate(rng, 15000, ds.STOPPING_BUDGET_QUESTIONS, ds.ALPHA)
    sw_rate = ex.stop_when_significant_rate(rng, 15000, ds.STOPPING_BUDGET_QUESTIONS, ds.ALPHA)
    assert sw_rate > 3 * ds.ALPHA
    assert sw_rate > tb_rate


# --------------------------------------------------------------------------
# Exercise 9 -- the handoff to Day 133
# --------------------------------------------------------------------------


def test_build_handoff_accepts_a_complete_object():
    handoff = ex.build_handoff({"name": "x", "p": 0.01}, {"p": 0.02}, 10)
    assert handoff["comparison_count"] == 10


@pytest.mark.parametrize("missing_field", ex.REQUIRED_HANDOFF_FIELDS)
def test_build_handoff_refuses_a_missing_field(missing_field):
    kwargs = {"finding": {"name": "x"}, "confirmation_result": {"p": 0.02}, "comparison_count": 5}
    kwargs[missing_field] = None
    with pytest.raises(ValueError):
        ex.build_handoff(**kwargs)


def test_write_report_stub_refuses_a_bare_finding():
    with pytest.raises(ValueError):
        ex.write_report_stub({"finding": {"name": "x"}})


def test_write_report_stub_renders_a_complete_handoff():
    handoff = ex.build_handoff({"name": "x", "p": 0.004}, {"p": 0.01}, 12)
    text = ex.write_report_stub(handoff)
    assert "x" in text
    assert "12" in text
