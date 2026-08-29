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

import itertools
from fractions import Fraction

import numpy as np
import pytest

import answers
import dataset as D
import probability as P
import simulate as S

# --------------------------------------------------------------------------
# The skip machinery
# --------------------------------------------------------------------------


def need(value, what):
    """Skip if the exercise has not been attempted, otherwise hand it back."""
    if value is None:
        pytest.skip(f"not attempted yet: {what}")
    return value


def attempt(fn, what):
    """Call something that may not be written yet, and skip if it is not."""
    try:
        result = fn()
    except (TypeError, AttributeError, NotImplementedError):
        pytest.skip(f"not attempted yet: {what}")
    if result is None:
        pytest.skip(f"not attempted yet: {what}")
    return result


def close(got, want, tol, what):
    assert abs(float(got) - float(want)) < tol, (
        f"{what}: your answer {got!r}, expected {want!r} "
        f"(difference {abs(float(got) - float(want)):.3e}, tolerance {tol:g})"
    )


def test_the_suite_itself_runs():
    """One test that always passes, so a green run is distinguishable from
    a collection error that quietly ran nothing at all."""
    assert len(D.TWO_DICE_SPACE) == 36


# --------------------------------------------------------------------------
# Exercise 1 -- the sample space and probability as counting
# --------------------------------------------------------------------------


def test_1_sample_space_has_36_outcomes():
    space = attempt(P.sample_space_two_dice, "sample_space_two_dice")
    assert len(space) == 36


def test_1_sample_space_matches_the_dataset_space():
    space = attempt(P.sample_space_two_dice, "sample_space_two_dice")
    assert set(space) == set(D.TWO_DICE_SPACE)


def test_1_event_filters_by_predicate():
    space = attempt(P.sample_space_two_dice, "sample_space_two_dice")
    ev = attempt(lambda: P.event(space, D.is_sum(7)), "event")
    assert len(ev) == 6
    assert all(a + b == 7 for a, b in ev)


def test_1_probability_of_sum_seven_is_exactly_one_sixth():
    space = attempt(P.sample_space_two_dice, "sample_space_two_dice")
    ev = attempt(lambda: P.event(space, D.is_sum(7)), "event")
    p = attempt(lambda: P.probability(ev, space), "probability")
    assert p == Fraction(1, 6), "P(sum == 7) must be exactly Fraction(1, 6)"


def test_1_probability_returns_a_fraction():
    space = attempt(P.sample_space_two_dice, "sample_space_two_dice")
    ev = attempt(lambda: P.event(space, D.is_sum(7)), "event")
    p = attempt(lambda: P.probability(ev, space), "probability")
    assert isinstance(p, Fraction), (
        "probability() must return a Fraction, not a float -- that is the "
        "whole point of using it here"
    )


def test_1_probability_of_the_whole_space_is_one():
    space = attempt(P.sample_space_two_dice, "sample_space_two_dice")
    p = attempt(lambda: P.probability(space, space), "probability")
    assert p == 1


def test_1_probability_of_the_empty_set_is_zero():
    space = attempt(P.sample_space_two_dice, "sample_space_two_dice")
    p = attempt(lambda: P.probability(frozenset(), space), "probability")
    assert p == 0


# --------------------------------------------------------------------------
# Exercise 2 -- the addition rule
# --------------------------------------------------------------------------


def _addition_setup():
    space = D.TWO_DICE_SPACE
    a = frozenset(o for o in space if D.ADDITION_EVENT_A(o))
    b = frozenset(o for o in space if D.ADDITION_EVENT_B(o))
    p_a = Fraction(len(a), len(space))
    p_b = Fraction(len(b), len(space))
    p_ab = Fraction(len(a & b), len(space))
    return p_a, p_b, p_ab


def test_2_addition_rule_gives_the_true_union():
    p_a, p_b, p_ab = _addition_setup()
    got = attempt(lambda: P.addition_rule(p_a, p_b, p_ab), "addition_rule")
    assert got == Fraction(11, 36)


def test_2_naive_sum_double_counts_the_overlap():
    p_a, p_b, p_ab = _addition_setup()
    naive = attempt(lambda: P.naive_sum(p_a, p_b), "naive_sum")
    assert naive == Fraction(1, 3), "P(A) + P(B) should be 6/36 + 6/36 = 1/3"


def test_2_the_naive_sum_overstates_by_exactly_the_intersection():
    p_a, p_b, p_ab = _addition_setup()
    naive = attempt(lambda: P.naive_sum(p_a, p_b), "naive_sum")
    true_union = attempt(lambda: P.addition_rule(p_a, p_b, p_ab), "addition_rule")
    assert naive - true_union == p_ab, (
        "the naive sum's error should be exactly P(A and B) = 1/36"
    )


# --------------------------------------------------------------------------
# Exercise 3 -- de Méré, exact and simulated
# --------------------------------------------------------------------------


def test_3a_complement_of_one_sixth_is_five_sixths():
    got = attempt(lambda: P.complement(Fraction(1, 6)), "complement")
    assert got == Fraction(5, 6)


def test_3b_at_least_one_six_matches_the_exact_de_mere_answer():
    got = attempt(
        lambda: P.at_least_one(Fraction(1, 6), D.DE_MERE_SINGLE_ROLLS), "at_least_one"
    )
    assert got == D.DE_MERE_SINGLE_EXACT


def test_3b_at_least_one_double_six_matches_the_exact_de_mere_answer():
    got = attempt(
        lambda: P.at_least_one(Fraction(1, 36), D.DE_MERE_DOUBLE_ROLLS),
        "at_least_one",
    )
    assert got == D.DE_MERE_DOUBLE_EXACT


def test_3c_bet_one_is_favourable_and_bet_two_is_not():
    assert D.DE_MERE_SINGLE_EXACT > Fraction(1, 2)
    assert D.DE_MERE_DOUBLE_EXACT < Fraction(1, 2)


def test_3d_simulation_of_bet_one_lands_within_three_standard_errors():
    rng = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
    got = attempt(
        lambda: S.simulate_at_least_one_six(rng, D.DE_MERE_SIM_TRIALS),
        "simulate_at_least_one_six",
    )
    close(got, float(D.DE_MERE_SINGLE_EXACT), D.DE_MERE_SINGLE_TOL, "de Méré bet 1")


def test_3d_simulation_of_bet_two_lands_within_three_standard_errors():
    rng = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
    got = attempt(
        lambda: S.simulate_at_least_one_double_six(rng, D.DE_MERE_SIM_TRIALS),
        "simulate_at_least_one_double_six",
    )
    close(got, float(D.DE_MERE_DOUBLE_EXACT), D.DE_MERE_DOUBLE_TOL, "de Méré bet 2")


# --------------------------------------------------------------------------
# Exercise 4 -- independence
# --------------------------------------------------------------------------


def test_4_the_independent_pair_is_reported_independent():
    a_pred, b_pred = D.INDEPENDENT_PAIR
    space = D.TWO_DICE_SPACE
    a = frozenset(o for o in space if a_pred(o))
    b = frozenset(o for o in space if b_pred(o))
    p_a, p_b = Fraction(len(a), 36), Fraction(len(b), 36)
    p_ab = Fraction(len(a & b), 36)
    got = attempt(lambda: P.is_independent(p_a, p_b, p_ab), "is_independent")
    assert got is True


def test_4_the_dependent_pair_is_reported_dependent():
    a_pred, b_pred = D.DEPENDENT_PAIR
    space = D.TWO_DICE_SPACE
    a = frozenset(o for o in space if a_pred(o))
    b = frozenset(o for o in space if b_pred(o))
    p_a, p_b = Fraction(len(a), 36), Fraction(len(b), 36)
    p_ab = Fraction(len(a & b), 36)
    got = attempt(lambda: P.is_independent(p_a, p_b, p_ab), "is_independent")
    assert got is False


# --------------------------------------------------------------------------
# Exercise 5 -- mutual exclusivity implies dependence
# --------------------------------------------------------------------------


def test_5_mutually_exclusive_events_have_zero_conditional():
    a_pred, b_pred = D.MUTUALLY_EXCLUSIVE_PAIR
    space = D.TWO_DICE_SPACE
    a = frozenset(o for o in space if a_pred(o))
    b = frozenset(o for o in space if b_pred(o))
    p_a = Fraction(len(a), 36)
    p_ab = Fraction(len(a & b), 36)
    p_b = Fraction(len(b), 36)
    got = attempt(lambda: P.conditional(p_ab, p_b), "conditional")
    assert got == 0
    assert p_a != 0, "P(A) must be non-zero for this to demonstrate dependence"
    assert got != p_a, "P(A | B) == 0 while P(A) != 0 -- the events are dependent"


# --------------------------------------------------------------------------
# Exercise 6 -- conditioning by restriction
# --------------------------------------------------------------------------


def test_6_conditional_by_formula_matches_conditional_by_filtering():
    space = D.TWO_DICE_SPACE
    a = frozenset(o for o in space if D.CONDITIONING_EVENT_A(o))
    b = frozenset(o for o in space if D.CONDITIONING_EVENT_B(o))
    p_ab = Fraction(len(a & b), 36)
    p_b = Fraction(len(b), 36)
    by_formula = attempt(lambda: P.conditional(p_ab, p_b), "conditional")

    restricted = frozenset(o for o in b if D.CONDITIONING_EVENT_A(o))
    by_filtering = Fraction(len(restricted), len(b))

    assert by_formula == by_filtering == Fraction(1, 6)


# --------------------------------------------------------------------------
# Exercise 7 -- the law of total probability
# --------------------------------------------------------------------------


def test_7_total_probability_matches_the_combined_enumeration():
    got = attempt(
        lambda: P.total_probability(D.URN_PRIOR, D.URN_CONDITIONAL_RED),
        "total_probability",
    )
    assert got == Fraction(9, 20)

    # Enumerate the combined 20-outcome experiment directly: 10 balls in
    # each of 2 urns, chosen with equal prior, so all 20 (urn, ball) pairs
    # are equally likely.
    urn1 = ["red"] * D.URN_1_RED + ["blue"] * D.URN_1_BLUE
    urn2 = ["red"] * D.URN_2_RED + ["blue"] * D.URN_2_BLUE
    combined = [("urn1", b) for b in urn1] + [("urn2", b) for b in urn2]
    reds = [o for o in combined if o[1] == "red"]
    enumerated = Fraction(len(reds), len(combined))
    assert got == enumerated


# --------------------------------------------------------------------------
# Exercise 8 -- Monte Carlo error scaling
# --------------------------------------------------------------------------


def test_8_error_shrinks_across_four_decades_of_sample_size():
    target = float(D.MONTE_CARLO_TARGET)
    mean_errors = []
    for n in D.MONTE_CARLO_SAMPLE_SIZES:
        errors = []
        for seed in D.MONTE_CARLO_SEEDS:
            rng = np.random.default_rng(seed)
            got = attempt(lambda: S.simulate_sum_seven(rng, n), "simulate_sum_seven")
            errors.append(abs(got - target))
        mean_errors.append(sum(errors) / len(errors))
    assert mean_errors[-1] < mean_errors[0], (
        "the average error at the largest n must be smaller than at the "
        "smallest n"
    )
    assert mean_errors[-1] < mean_errors[0] / 5.0, (
        "a thousandfold increase in n should shrink the error by roughly "
        "sqrt(1000) = ~31x, well below a factor of 5"
    )


def test_8_the_shrink_looks_like_one_over_sqrt_n_not_one_over_n():
    target = float(D.MONTE_CARLO_TARGET)
    small_n, large_n = D.MONTE_CARLO_SAMPLE_SIZES[0], D.MONTE_CARLO_SAMPLE_SIZES[-1]
    ratio_n = large_n / small_n  # 1000

    def mean_error(n):
        errors = []
        for seed in D.MONTE_CARLO_SEEDS:
            rng = np.random.default_rng(seed)
            got = attempt(lambda: S.simulate_sum_seven(rng, n), "simulate_sum_seven")
            errors.append(abs(got - target))
        return sum(errors) / len(errors)

    error_ratio = mean_error(small_n) / mean_error(large_n)
    sqrt_prediction = ratio_n**0.5  # ~31.6
    linear_prediction = ratio_n  # 1000
    # The observed shrink must land far closer to the sqrt(n) prediction
    # than to the 1/n prediction -- checked as a wide band, not a point, so
    # the test is not flaky on a different machine.
    assert 0.3 * sqrt_prediction < error_ratio < 3.0 * sqrt_prediction
    assert error_ratio < linear_prediction / 10.0


# --------------------------------------------------------------------------
# Exercise 9 -- reproducibility
# --------------------------------------------------------------------------


def test_9_the_same_seed_gives_byte_identical_results():
    rng_a = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
    rng_b = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
    result_a = attempt(
        lambda: S.simulate_sum_seven(rng_a, D.REPRODUCIBILITY_TRIALS),
        "simulate_sum_seven",
    )
    result_b = attempt(
        lambda: S.simulate_sum_seven(rng_b, D.REPRODUCIBILITY_TRIALS),
        "simulate_sum_seven",
    )
    assert result_a == result_b, (
        "two Generators built from the same seed must produce identical "
        "results -- that is the entire point of default_rng(seed)"
    )


def test_9_a_different_seed_gives_a_different_but_still_close_result():
    rng_a = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
    rng_b = np.random.default_rng(D.REPRODUCIBILITY_SEED_B)
    result_a = attempt(
        lambda: S.simulate_sum_seven(rng_a, D.REPRODUCIBILITY_TRIALS),
        "simulate_sum_seven",
    )
    result_b = attempt(
        lambda: S.simulate_sum_seven(rng_b, D.REPRODUCIBILITY_TRIALS),
        "simulate_sum_seven",
    )
    assert result_a != result_b, "different seeds should not coincide exactly"
    target = float(D.MONTE_CARLO_TARGET)
    tol = 4.0 * D.standard_error(target, D.REPRODUCIBILITY_TRIALS)
    close(result_a, target, tol, "seed A")
    close(result_b, target, tol, "seed B")


# --------------------------------------------------------------------------
# The eighteen predictions
# --------------------------------------------------------------------------

EXPECTED: dict[str, object] = {
    "sample_space_size": 36,
    "p_sum_seven": float(Fraction(1, 6)),
    "addition_naive_sum": float(Fraction(1, 3)),
    "addition_true_union": float(Fraction(11, 36)),
    "addition_error_amount": float(Fraction(1, 36)),
    "de_mere_single_bet_probability": float(D.DE_MERE_SINGLE_EXACT),
    "de_mere_double_bet_probability": float(D.DE_MERE_DOUBLE_EXACT),
    "de_mere_favorable_bet": 1,
    "independent_pair_holds": True,
    "dependent_pair_holds": False,
    "mutually_exclusive_implies_dependent": True,
    "conditional_p_sum8_given_first_even": float(Fraction(1, 6)),
    "conditional_formula_matches_filter": True,
    "urn_total_probability_red": 0.45,
    "urn_enumeration_matches_formula": True,
    "monte_carlo_error_shrinks_with_n": True,
    "monte_carlo_error_ratio_near_sqrt10": True,
    "reproducibility_same_seed_identical": True,
    "reproducibility_different_seed_differs": True,
}

HINTS: dict[str, str] = {
    "addition_error_amount": (
        "This is exactly P(A and B), the region the naive sum counted twice."
    ),
    "de_mere_favorable_bet": (
        "A bet is favourable to the player when its probability is above "
        "0.5. Only one of the two is."
    ),
    "mutually_exclusive_implies_dependent": (
        "P(A | B) collapses to 0 for a mutually exclusive pair, but P(A) is "
        "not 0 -- so knowing B happened changed what you believe about A."
    ),
    "monte_carlo_error_ratio_near_sqrt10": (
        "Multiplying n by 10 should shrink the error by about sqrt(10), "
        "roughly 3.16x -- not by 10x."
    ),
}


@pytest.mark.parametrize("key", sorted(EXPECTED))
def test_predictions(key):
    got = need(answers.ANSWERS.get(key), f"answers.ANSWERS[{key!r}]")
    want = EXPECTED[key]
    hint = HINTS.get(key, "")
    if isinstance(want, bool) or isinstance(want, int):
        assert got == want, f"{key}: your answer {got!r}, expected {want!r}. {hint}"
    else:
        assert abs(float(got) - want) < 1e-9, (
            f"{key}: your answer {got!r}, expected {want!r}. {hint}"
        )


def test_every_answer_key_is_still_present():
    missing = sorted(set(EXPECTED) - set(answers.ANSWERS))
    assert not missing, f"answers.py is missing these keys: {missing}"
