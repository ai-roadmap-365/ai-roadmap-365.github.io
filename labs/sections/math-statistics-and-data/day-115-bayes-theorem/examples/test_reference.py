"""The reference suite: real values, real exceptions, real simulations.

Run from the lab directory:

    .venv/bin/pytest examples -q -p no:cacheprovider
"""

from fractions import Fraction

import numpy as np
import pytest

import bayes as B
import dataset as D
import naive_bayes as NB
import simulate as S

# ---------------------------------------------------------------------------
# Exercise 1 -- the opening posterior
# ---------------------------------------------------------------------------


def test_opening_posterior_matches_the_hand_derivation():
    p_cond_pos = D.PREVALENCE * D.SENSITIVITY
    p_nocond_pos = (1 - D.PREVALENCE) * (1 - D.SPECIFICITY)
    expected = p_cond_pos / (p_cond_pos + p_nocond_pos)
    assert B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY) == expected


def test_opening_posterior_is_exactly_99_over_1098():
    assert B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY) == Fraction(99, 1098)


def test_opening_posterior_reduces_to_11_over_122():
    assert B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY) == Fraction(11, 122)


def test_opening_posterior_rounds_to_0_0902():
    result = B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY)
    assert round(float(result), 4) == 0.0902


def test_opening_posterior_is_not_the_naive_099_guess():
    result = B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY)
    assert result != Fraction(99, 100)
    assert Fraction(99, 100) - result > Fraction(8, 10)


def test_posterior_returns_a_fraction():
    assert isinstance(B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY), Fraction)


def test_posterior_of_a_certain_prior_is_one():
    assert B.posterior(Fraction(1), D.SENSITIVITY, D.SPECIFICITY) == 1


def test_posterior_of_an_impossible_prior_is_zero():
    assert B.posterior(Fraction(0), D.SENSITIVITY, D.SPECIFICITY) == 0


@pytest.mark.parametrize(
    "sens,spec",
    [(Fraction(1, 1), Fraction(1, 1)), (Fraction(9, 10), Fraction(9, 10)), (Fraction(1, 2), Fraction(1, 2))],
)
def test_posterior_matches_a_from_scratch_partition_sum_for_several_tests(sens, spec):
    # This is Day 113's law of total probability, applied directly: the
    # evidence P(positive) partitions into "condition" and "no condition".
    prior = D.PREVALENCE
    p_pos = prior * sens + (1 - prior) * (1 - spec)
    expected = (prior * sens) / p_pos
    assert B.posterior(prior, sens, spec) == expected


# ---------------------------------------------------------------------------
# Exercise 2 -- natural frequencies
# ---------------------------------------------------------------------------


def test_natural_frequency_population_splits_correctly():
    assert D.NATURAL_FREQUENCY_SICK + D.NATURAL_FREQUENCY_WELL == D.NATURAL_FREQUENCY_POPULATION


def test_natural_frequency_sick_matches_the_prevalence_exactly():
    assert Fraction(D.NATURAL_FREQUENCY_SICK, D.NATURAL_FREQUENCY_POPULATION) == D.PREVALENCE


def test_natural_frequency_tp_and_fn_account_for_every_sick_person():
    assert D.NATURAL_FREQUENCY_TP + D.NATURAL_FREQUENCY_FN == D.NATURAL_FREQUENCY_SICK


def test_natural_frequency_fp_and_tn_account_for_every_well_person():
    assert D.NATURAL_FREQUENCY_FP + D.NATURAL_FREQUENCY_TN == D.NATURAL_FREQUENCY_WELL


def test_natural_frequency_cell_counts_are_the_documented_values():
    assert (D.NATURAL_FREQUENCY_TP, D.NATURAL_FREQUENCY_FP, D.NATURAL_FREQUENCY_TN, D.NATURAL_FREQUENCY_FN) == (
        99,
        999,
        98_901,
        1,
    )


def test_natural_frequency_ratio_matches_the_formula_posterior_exactly():
    total_positive = D.NATURAL_FREQUENCY_TP + D.NATURAL_FREQUENCY_FP
    ratio = Fraction(D.NATURAL_FREQUENCY_TP, total_positive)
    assert ratio == B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY)


def test_natural_frequency_total_positives_is_1098():
    assert D.NATURAL_FREQUENCY_TP + D.NATURAL_FREQUENCY_FP == 1098


# ---------------------------------------------------------------------------
# Exercise 3 -- simulation
# ---------------------------------------------------------------------------


def test_simulate_population_counts_add_up():
    rng = np.random.default_rng(0)
    counts = S.simulate_population(rng, 50_000, 0.1, 0.9, 0.9)
    total = counts.true_positive + counts.false_positive + counts.true_negative + counts.false_negative
    assert total == 50_000


def test_simulate_population_empirical_posterior_within_tolerance_at_scale():
    rng = np.random.default_rng(D.SIMULATION_SEED)
    counts = S.simulate_population(
        rng, D.SIMULATION_POPULATION, float(D.PREVALENCE), float(D.SENSITIVITY), float(D.SPECIFICITY)
    )
    exact = float(D.OPENING_POSTERIOR_EXACT)
    tol = 3.0 * D.standard_error(exact, counts.positives)
    assert abs(counts.empirical_posterior - exact) < tol


def test_simulate_population_empirical_posterior_is_far_from_naive_099():
    rng = np.random.default_rng(D.SIMULATION_SEED)
    counts = S.simulate_population(
        rng, D.SIMULATION_POPULATION, float(D.PREVALENCE), float(D.SENSITIVITY), float(D.SPECIFICITY)
    )
    assert counts.empirical_posterior < 0.5


def test_simulate_population_with_zero_prevalence_has_no_true_positives():
    rng = np.random.default_rng(1)
    counts = S.simulate_population(rng, 10_000, 0.0, 0.99, 0.99)
    assert counts.true_positive == 0
    assert counts.false_negative == 0


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_simulate_population_is_reproducible_for_a_fixed_seed(seed):
    counts_a = S.simulate_population(
        np.random.default_rng(seed), 100_000, float(D.PREVALENCE), float(D.SENSITIVITY), float(D.SPECIFICITY)
    )
    counts_b = S.simulate_population(
        np.random.default_rng(seed), 100_000, float(D.PREVALENCE), float(D.SENSITIVITY), float(D.SPECIFICITY)
    )
    assert counts_a == counts_b


# ---------------------------------------------------------------------------
# Exercise 4 -- prevalence sweep
# ---------------------------------------------------------------------------


def test_prevalence_sweep_is_strictly_increasing():
    results = [B.posterior(p, D.SENSITIVITY, D.SPECIFICITY) for p in D.PREVALENCE_SWEEP]
    assert all(results[i] < results[i + 1] for i in range(len(results) - 1))


def test_prevalence_one_half_gives_exactly_the_sensitivity():
    assert B.posterior(Fraction(1, 2), D.SENSITIVITY, D.SPECIFICITY) == Fraction(99, 100)


def test_prevalence_sweep_final_value_is_one_half():
    assert D.PREVALENCE_SWEEP[-1] == Fraction(1, 2)


@pytest.mark.parametrize("prevalence,expected", [
    (Fraction(1, 100_000), Fraction(11, 11122)),
    (Fraction(1, 10_000), Fraction(1, 102)),
    (Fraction(1, 100), Fraction(1, 2)),
])
def test_prevalence_sweep_matches_documented_exact_values(prevalence, expected):
    assert B.posterior(prevalence, D.SENSITIVITY, D.SPECIFICITY) == expected


def test_099_is_over_ten_times_the_true_answer_at_one_in_a_thousand():
    true_answer = B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY)
    assert Fraction(99, 100) / true_answer > 10


# ---------------------------------------------------------------------------
# Exercise 5 -- odds form
# ---------------------------------------------------------------------------


def test_probability_to_odds_and_back_round_trips():
    p = Fraction(11, 122)
    assert B.odds_to_probability(B.probability_to_odds(p)) == p


def test_prior_odds_are_exactly_1_over_999():
    assert B.probability_to_odds(D.PREVALENCE) == Fraction(1, 999)


def test_likelihood_ratio_is_exactly_99():
    assert B.likelihood_ratio(D.SENSITIVITY, D.SPECIFICITY) == 99


def test_posterior_odds_equal_prior_odds_times_likelihood_ratio():
    prior_odds = B.probability_to_odds(D.PREVALENCE)
    ratio = B.likelihood_ratio(D.SENSITIVITY, D.SPECIFICITY)
    posterior_odds = B.update_odds(prior_odds, ratio)
    assert posterior_odds == prior_odds * ratio


def test_odds_form_matches_direct_posterior_exactly():
    prior_odds = B.probability_to_odds(D.PREVALENCE)
    ratio = B.likelihood_ratio(D.SENSITIVITY, D.SPECIFICITY)
    via_odds = B.odds_to_probability(B.update_odds(prior_odds, ratio))
    direct = B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY)
    assert via_odds == direct


def test_odds_of_one_half_probability_is_exactly_one():
    assert B.probability_to_odds(Fraction(1, 2)) == 1


# ---------------------------------------------------------------------------
# Exercise 6 -- sequential updating
# ---------------------------------------------------------------------------


def _tests_ab():
    return (D.TEST_A_SENSITIVITY, D.TEST_A_SPECIFICITY), (D.TEST_B_SENSITIVITY, D.TEST_B_SPECIFICITY)


def test_sequential_posterior_matches_hand_worked_value():
    test_a, test_b = _tests_ab()
    result = B.sequential_posterior(D.PREVALENCE, [test_a, test_b])
    assert result == Fraction(1045, 1267)


def test_sequential_posterior_order_does_not_matter():
    test_a, test_b = _tests_ab()
    forward = B.sequential_posterior(D.PREVALENCE, [test_a, test_b])
    backward = B.sequential_posterior(D.PREVALENCE, [test_b, test_a])
    assert forward == backward


def test_sequential_posterior_with_one_test_matches_single_posterior():
    test_a, _ = _tests_ab()
    single = B.posterior(D.PREVALENCE, *test_a)
    assert B.sequential_posterior(D.PREVALENCE, [test_a]) == single


def test_sequential_posterior_with_no_tests_returns_the_prior():
    assert B.sequential_posterior(D.PREVALENCE, []) == D.PREVALENCE


def test_two_tests_move_the_posterior_well_above_a_single_test():
    test_a, test_b = _tests_ab()
    single = B.posterior(D.PREVALENCE, *test_a)
    double = B.sequential_posterior(D.PREVALENCE, [test_a, test_b])
    assert double > single
    assert double > Fraction(1, 2)


@pytest.mark.parametrize("order", [0, 1])
def test_sequential_posterior_is_commutative_across_three_tests(order):
    tests = [
        (D.TEST_A_SENSITIVITY, D.TEST_A_SPECIFICITY),
        (D.TEST_B_SENSITIVITY, D.TEST_B_SPECIFICITY),
        (D.SENSITIVITY, D.SPECIFICITY),
    ]
    shuffled = list(reversed(tests)) if order else tests
    result = B.sequential_posterior(D.PREVALENCE, shuffled)
    expected = B.sequential_posterior(D.PREVALENCE, tests)
    assert result == expected


# ---------------------------------------------------------------------------
# Exercise 7 -- correlated tests
# ---------------------------------------------------------------------------


def test_independent_pair_probability_is_the_square():
    assert B.independent_pair_probability(Fraction(99, 100)) == Fraction(9801, 10000)


def test_correlated_pair_probability_with_zero_weight_matches_independent():
    rate = Fraction(99, 100)
    assert B.correlated_pair_probability(rate, Fraction(0)) == B.independent_pair_probability(rate)


def test_correlated_pair_probability_with_full_weight_is_the_single_rate():
    rate = Fraction(3, 4)
    assert B.correlated_pair_probability(rate, Fraction(1)) == rate


def test_naive_posterior_is_exactly_363_over_400():
    naive_tp = B.independent_pair_probability(D.CORRELATED_SENSITIVITY)
    naive_fp = B.independent_pair_probability(1 - D.CORRELATED_SPECIFICITY)
    assert B.posterior_general(D.PREVALENCE, naive_tp, naive_fp) == Fraction(363, 400)


def test_naive_posterior_is_strictly_higher_than_the_correlated_posterior():
    naive_tp = B.independent_pair_probability(D.CORRELATED_SENSITIVITY)
    naive_fp = B.independent_pair_probability(1 - D.CORRELATED_SPECIFICITY)
    naive = B.posterior_general(D.PREVALENCE, naive_tp, naive_fp)

    corr_tp = B.correlated_pair_probability(D.CORRELATED_SENSITIVITY, D.CORRELATION_WEIGHT)
    corr_fp = B.correlated_pair_probability(1 - D.CORRELATED_SPECIFICITY, D.CORRELATION_WEIGHT)
    correlated = B.posterior_general(D.PREVALENCE, corr_tp, corr_fp)

    assert naive > correlated


def test_correlated_posterior_still_exceeds_a_single_tests_posterior():
    corr_tp = B.correlated_pair_probability(D.CORRELATED_SENSITIVITY, D.CORRELATION_WEIGHT)
    corr_fp = B.correlated_pair_probability(1 - D.CORRELATED_SPECIFICITY, D.CORRELATION_WEIGHT)
    correlated = B.posterior_general(D.PREVALENCE, corr_tp, corr_fp)
    assert correlated > D.OPENING_POSTERIOR_EXACT


# ---------------------------------------------------------------------------
# Exercise 8 -- Naive Bayes with Laplace smoothing
# ---------------------------------------------------------------------------


@pytest.fixture
def trained_model():
    return NB.train({"spam": D.SPAM_DOCS, "ham": D.HAM_DOCS})


def test_vocabulary_and_class_counts(trained_model):
    assert "watches" in trained_model.vocabulary
    assert trained_model.doc_counts == {"spam": 3, "ham": 3}


def test_watches_never_appears_in_ham_training(trained_model):
    assert trained_model.word_counts["ham"]["watches"] == 0


def test_review_never_appears_in_spam_training(trained_model):
    assert trained_model.word_counts["spam"]["review"] == 0


def test_clear_spam_document_classifies_spam_smoothed(trained_model):
    winner, _ = NB.classify(trained_model, D.HELD_OUT_CLEAR_SPAM, alpha=D.LAPLACE_ALPHA)
    assert winner == "spam"


def test_clear_ham_document_classifies_ham_smoothed(trained_model):
    winner, _ = NB.classify(trained_model, D.HELD_OUT_CLEAR_HAM, alpha=D.LAPLACE_ALPHA)
    assert winner == "ham"


def test_veto_case_classifies_ham_with_smoothing(trained_model):
    winner, _ = NB.classify(trained_model, D.HELD_OUT_VETO_CASE, alpha=D.LAPLACE_ALPHA)
    assert winner == "ham"


def test_veto_case_ham_score_is_exactly_zero_without_smoothing(trained_model):
    _, scores = NB.classify(trained_model, D.HELD_OUT_VETO_CASE, alpha=0)
    assert scores["ham"] == 0


def test_veto_case_spam_score_is_also_exactly_zero_without_smoothing(trained_model):
    _, scores = NB.classify(trained_model, D.HELD_OUT_VETO_CASE, alpha=0)
    assert scores["spam"] == 0


def test_veto_case_misclassifies_without_smoothing(trained_model):
    smoothed_winner, _ = NB.classify(trained_model, D.HELD_OUT_VETO_CASE, alpha=D.LAPLACE_ALPHA)
    unsmoothed_winner, _ = NB.classify(trained_model, D.HELD_OUT_VETO_CASE, alpha=0)
    assert unsmoothed_winner != smoothed_winner


def test_word_probability_returns_a_fraction(trained_model):
    prob = NB.word_probability(trained_model, "buy", "spam", alpha=1)
    assert isinstance(prob, Fraction)


def test_word_probability_with_smoothing_is_never_exactly_zero(trained_model):
    prob = NB.word_probability(trained_model, "watches", "ham", alpha=1)
    assert prob > 0


def test_word_probability_without_smoothing_is_exactly_zero_for_an_absent_word(trained_model):
    prob = NB.word_probability(trained_model, "watches", "ham", alpha=0)
    assert prob == 0


def test_out_of_vocabulary_words_are_skipped_rather_than_zeroing_everything(trained_model):
    # "xyzzy" was never seen in training at all.
    winner, scores = NB.classify(trained_model, "buy cheap watches xyzzy", alpha=D.LAPLACE_ALPHA)
    assert winner == "spam"
    assert all(score > 0 for score in scores.values())


# ---------------------------------------------------------------------------
# Exercise 9 -- log space
# ---------------------------------------------------------------------------


def test_500_factors_of_001_underflow_to_exactly_zero():
    factors = [0.01] * 500
    assert NB.multiply_probabilities(factors) == 0.0


def test_sum_of_logs_stays_finite():
    import math

    factors = [0.01] * 500
    assert math.isfinite(NB.sum_of_logs(factors))


def test_sum_of_logs_matches_the_measured_value():
    factors = [0.01] * 500
    assert NB.sum_of_logs(factors) == D.UNDERFLOW_LOG_SUM


def test_sum_of_logs_is_not_the_wrong_draft_figure():
    factors = [0.01] * 500
    assert round(NB.sum_of_logs(factors), 2) != -1151.29


def test_fewer_factors_do_not_underflow():
    factors = [0.01] * 50
    assert NB.multiply_probabilities(factors) > 0.0


def test_classify_log_space_agrees_with_classify_on_short_documents(trained_model):
    smoothed_winner, _ = NB.classify(trained_model, D.HELD_OUT_CLEAR_SPAM, alpha=D.LAPLACE_ALPHA)
    log_winner, _ = NB.classify_log_space(trained_model, D.HELD_OUT_CLEAR_SPAM, alpha=D.LAPLACE_ALPHA)
    assert smoothed_winner == log_winner


def test_classify_log_space_still_works_on_a_long_repeated_document(trained_model):
    # A document long enough that the plain product would underflow.
    long_doc = " ".join(["buy", "cheap", "watches"] * 200)
    winner, scores = NB.classify_log_space(trained_model, long_doc, alpha=D.LAPLACE_ALPHA)
    assert winner == "spam"
    import math

    assert all(math.isfinite(score) for score in scores.values())
