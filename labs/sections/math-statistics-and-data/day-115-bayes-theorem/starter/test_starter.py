"""Your running score. Unattempted work SKIPS; wrong work FAILS with both values.

Run from the lab directory:

    .venv/bin/pytest starter -q

On an untouched checkout this reports one pass and everything else skipped.
A skip means "not attempted". A failure means "attempted and wrong", and the
message shows your answer next to the real one so you can see the gap rather
than guess at it.

Nothing in here checks that a function exists or that a file is present.
Every test runs your code and compares a value.
"""

from fractions import Fraction

import numpy as np
import pytest

import answers
import bayes as B
import dataset as D
import naive_bayes as NB
import simulate as S

# --------------------------------------------------------------------------
# The skip machinery
# --------------------------------------------------------------------------


def attempt(fn, what):
    """Call something that may not be written yet, and skip if it is not."""
    try:
        result = fn()
    except (TypeError, AttributeError, NotImplementedError):
        pytest.skip(f"not attempted yet: {what}")
    if result is None:
        pytest.skip(f"not attempted yet: {what}")
    return result


def need(value, what):
    """Skip if the exercise has not been attempted, otherwise hand it back."""
    if value is None:
        pytest.skip(f"not attempted yet: {what}")
    return value


def test_the_suite_itself_runs():
    """One test that always passes, so a green run is distinguishable from
    a collection error that quietly ran nothing at all."""
    assert D.PREVALENCE == Fraction(1, 1000)


# --------------------------------------------------------------------------
# Exercise 1 -- the opening posterior
# --------------------------------------------------------------------------


def test_1_posterior_matches_the_exact_fraction():
    result = attempt(lambda: B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY), "posterior")
    assert result == D.OPENING_POSTERIOR_EXACT


def test_1_posterior_returns_a_fraction_not_a_float():
    result = attempt(lambda: B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY), "posterior")
    assert isinstance(result, Fraction)


def test_1_posterior_is_not_the_naive_099_guess():
    result = attempt(lambda: B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY), "posterior")
    assert result != Fraction(99, 100)


def test_1_posterior_of_a_certain_prior_is_one():
    result = attempt(lambda: B.posterior(Fraction(1), D.SENSITIVITY, D.SPECIFICITY), "posterior")
    assert result == 1


# --------------------------------------------------------------------------
# Exercise 2 -- natural frequencies (uses dataset.py's captured constants,
# nothing to implement, but confirms you have read them)
# --------------------------------------------------------------------------


def test_2_natural_frequency_ratio_matches_the_formula():
    ratio = Fraction(D.NATURAL_FREQUENCY_TP, D.NATURAL_FREQUENCY_TP + D.NATURAL_FREQUENCY_FP)
    exact = attempt(lambda: B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY), "posterior")
    assert ratio == exact


# --------------------------------------------------------------------------
# Exercise 3 -- simulation
# --------------------------------------------------------------------------


def test_3_simulate_population_counts_add_up():
    counts = attempt(
        lambda: S.simulate_population(np.random.default_rng(0), 20_000, 0.1, 0.9, 0.9),
        "simulate_population",
    )
    total = counts.true_positive + counts.false_positive + counts.true_negative + counts.false_negative
    assert total == 20_000


def test_3_simulate_population_within_tolerance_at_scale():
    counts = attempt(
        lambda: S.simulate_population(
            np.random.default_rng(D.SIMULATION_SEED),
            D.SIMULATION_POPULATION,
            float(D.PREVALENCE),
            float(D.SENSITIVITY),
            float(D.SPECIFICITY),
        ),
        "simulate_population",
    )
    exact = float(D.OPENING_POSTERIOR_EXACT)
    tol = 3.0 * D.standard_error(exact, counts.positives)
    assert abs(counts.empirical_posterior - exact) < tol


# --------------------------------------------------------------------------
# Exercise 4 -- the prevalence sweep
# --------------------------------------------------------------------------


def test_4_prevalence_one_half_gives_exactly_099():
    result = attempt(lambda: B.posterior(Fraction(1, 2), D.SENSITIVITY, D.SPECIFICITY), "posterior")
    assert result == Fraction(99, 100)


def test_4_prevalence_sweep_is_strictly_increasing():
    results = attempt(
        lambda: [B.posterior(p, D.SENSITIVITY, D.SPECIFICITY) for p in D.PREVALENCE_SWEEP],
        "posterior",
    )
    assert all(results[i] < results[i + 1] for i in range(len(results) - 1))


# --------------------------------------------------------------------------
# Exercise 5 -- the odds form
# --------------------------------------------------------------------------


def test_5_likelihood_ratio_is_exactly_99():
    result = attempt(lambda: B.likelihood_ratio(D.SENSITIVITY, D.SPECIFICITY), "likelihood_ratio")
    assert result == 99


def test_5_posterior_odds_equal_prior_odds_times_ratio():
    prior_odds = attempt(lambda: B.probability_to_odds(D.PREVALENCE), "probability_to_odds")
    ratio = attempt(lambda: B.likelihood_ratio(D.SENSITIVITY, D.SPECIFICITY), "likelihood_ratio")
    posterior_odds = attempt(lambda: B.update_odds(prior_odds, ratio), "update_odds")
    assert posterior_odds == prior_odds * ratio


def test_5_odds_form_matches_direct_posterior():
    prior_odds = attempt(lambda: B.probability_to_odds(D.PREVALENCE), "probability_to_odds")
    ratio = attempt(lambda: B.likelihood_ratio(D.SENSITIVITY, D.SPECIFICITY), "likelihood_ratio")
    posterior_odds = attempt(lambda: B.update_odds(prior_odds, ratio), "update_odds")
    via_odds = attempt(lambda: B.odds_to_probability(posterior_odds), "odds_to_probability")
    direct = attempt(lambda: B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY), "posterior")
    assert via_odds == direct


# --------------------------------------------------------------------------
# Exercise 6 -- sequential updating
# --------------------------------------------------------------------------


def _tests_ab():
    return (D.TEST_A_SENSITIVITY, D.TEST_A_SPECIFICITY), (D.TEST_B_SENSITIVITY, D.TEST_B_SPECIFICITY)


def test_6_sequential_posterior_matches_the_documented_value():
    test_a, test_b = _tests_ab()
    result = attempt(lambda: B.sequential_posterior(D.PREVALENCE, [test_a, test_b]), "sequential_posterior")
    assert result == Fraction(1045, 1267)


def test_6_sequential_posterior_order_does_not_matter():
    test_a, test_b = _tests_ab()
    forward = attempt(lambda: B.sequential_posterior(D.PREVALENCE, [test_a, test_b]), "sequential_posterior")
    backward = attempt(lambda: B.sequential_posterior(D.PREVALENCE, [test_b, test_a]), "sequential_posterior")
    assert forward == backward


# --------------------------------------------------------------------------
# Exercise 7 -- correlated tests
# --------------------------------------------------------------------------


def test_7_naive_posterior_is_exactly_363_over_400():
    naive_tp = attempt(lambda: B.independent_pair_probability(D.CORRELATED_SENSITIVITY), "independent_pair_probability")
    naive_fp = attempt(
        lambda: B.independent_pair_probability(1 - D.CORRELATED_SPECIFICITY), "independent_pair_probability"
    )
    result = attempt(lambda: B.posterior_general(D.PREVALENCE, naive_tp, naive_fp), "posterior_general")
    assert result == Fraction(363, 400)


def test_7_naive_posterior_is_strictly_higher_than_correlated():
    naive_tp = attempt(lambda: B.independent_pair_probability(D.CORRELATED_SENSITIVITY), "independent_pair_probability")
    naive_fp = attempt(
        lambda: B.independent_pair_probability(1 - D.CORRELATED_SPECIFICITY), "independent_pair_probability"
    )
    naive = attempt(lambda: B.posterior_general(D.PREVALENCE, naive_tp, naive_fp), "posterior_general")

    corr_tp = attempt(
        lambda: B.correlated_pair_probability(D.CORRELATED_SENSITIVITY, D.CORRELATION_WEIGHT),
        "correlated_pair_probability",
    )
    corr_fp = attempt(
        lambda: B.correlated_pair_probability(1 - D.CORRELATED_SPECIFICITY, D.CORRELATION_WEIGHT),
        "correlated_pair_probability",
    )
    correlated = attempt(lambda: B.posterior_general(D.PREVALENCE, corr_tp, corr_fp), "posterior_general")
    assert naive > correlated


# --------------------------------------------------------------------------
# Exercise 8 -- Naive Bayes with Laplace smoothing
# --------------------------------------------------------------------------


def _trained_model():
    return NB.train({"spam": D.SPAM_DOCS, "ham": D.HAM_DOCS})


def test_8_clear_documents_classify_correctly():
    model = attempt(_trained_model, "train")
    spam_winner, _ = attempt(lambda: NB.classify(model, D.HELD_OUT_CLEAR_SPAM, alpha=D.LAPLACE_ALPHA), "classify")
    ham_winner, _ = attempt(lambda: NB.classify(model, D.HELD_OUT_CLEAR_HAM, alpha=D.LAPLACE_ALPHA), "classify")
    assert (spam_winner, ham_winner) == ("spam", "ham")


def test_8_veto_case_classifies_ham_with_smoothing():
    model = attempt(_trained_model, "train")
    winner, _ = attempt(lambda: NB.classify(model, D.HELD_OUT_VETO_CASE, alpha=D.LAPLACE_ALPHA), "classify")
    assert winner == "ham"


def test_8_veto_case_ham_score_is_exactly_zero_without_smoothing():
    model = attempt(_trained_model, "train")
    _, scores = attempt(lambda: NB.classify(model, D.HELD_OUT_VETO_CASE, alpha=0), "classify")
    assert scores["ham"] == 0


def test_8_word_probability_with_smoothing_never_zero():
    model = attempt(_trained_model, "train")
    prob = attempt(lambda: NB.word_probability(model, "watches", "ham", alpha=1), "word_probability")
    assert prob > 0


# --------------------------------------------------------------------------
# Exercise 9 -- log space
# --------------------------------------------------------------------------


def test_9_500_factors_of_001_underflow_to_exactly_zero():
    result = attempt(lambda: NB.multiply_probabilities([0.01] * 500), "multiply_probabilities")
    assert result == 0.0


def test_9_sum_of_logs_stays_finite():
    import math

    result = attempt(lambda: NB.sum_of_logs([0.01] * 500), "sum_of_logs")
    assert math.isfinite(result)


def test_9_sum_of_logs_matches_the_measured_value():
    result = attempt(lambda: NB.sum_of_logs([0.01] * 500), "sum_of_logs")
    assert result == D.UNDERFLOW_LOG_SUM


# --------------------------------------------------------------------------
# Predictions -- fifteen numbers, checked against the real answers
# --------------------------------------------------------------------------

EXPECTED: dict[str, object] = {
    "opening_posterior": float(D.OPENING_POSTERIOR_EXACT),
    "opening_posterior_below_naive_guess": True,
    "natural_frequency_total_positives": 1098.0,
    "simulation_within_tolerance": True,
    "prevalence_half_posterior": 0.99,
    "prevalence_sweep_increasing": True,
    "likelihood_ratio_value": 99.0,
    "odds_form_matches_direct": True,
    "sequential_two_test_posterior": float(Fraction(1045, 1267)),
    "sequential_order_independent": True,
    "correlated_naive_posterior": 0.9075,
    "correlated_naive_overstates": True,
    "veto_case_smoothed_class": "ham",
    "veto_case_unsmoothed_ham_is_zero": True,
    "underflow_to_exactly_zero": True,
}

HINTS: dict[str, str] = {
    "opening_posterior": (
        "Bayes' theorem: (prior x sensitivity) / evidence, where evidence "
        "is the law of total probability over {condition, no condition}."
    ),
    "correlated_naive_posterior": (
        "This is the SAME formula as exercise 6, just with sensitivity "
        "squared and (1 - specificity) squared as the two likelihoods."
    ),
    "veto_case_smoothed_class": (
        "Three of the four words in this document are ham-associated; "
        "only 'watches' points toward spam."
    ),
}


@pytest.mark.parametrize("key", sorted(EXPECTED))
def test_predictions(key):
    got = need(answers.ANSWERS.get(key), f"answers.ANSWERS[{key!r}]")
    want = EXPECTED[key]
    hint = HINTS.get(key, "")
    if isinstance(want, (bool, str)):
        assert got == want, f"{key}: your answer {got!r}, expected {want!r}. {hint}"
    else:
        assert abs(float(got) - float(want)) < 1e-6, (
            f"{key}: your answer {got!r}, expected {want!r}. {hint}"
        )


def test_every_answer_key_is_still_present():
    missing = sorted(set(EXPECTED) - set(answers.ANSWERS))
    assert not missing, f"answers.py is missing these keys: {missing}"
