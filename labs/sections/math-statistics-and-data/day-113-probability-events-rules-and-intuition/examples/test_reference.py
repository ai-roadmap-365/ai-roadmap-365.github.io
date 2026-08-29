"""The reference suite: real values, real exceptions, real simulations.

Run from the lab directory:

    .venv/bin/pytest examples -q -p no:cacheprovider
"""

import itertools
from fractions import Fraction

import numpy as np
import pytest

import dataset as D
import probability as P
import simulate as S

SPACE = P.sample_space_two_dice()

# ---------------------------------------------------------------------------
# Exercise 1 -- the sample space and probability as counting
# ---------------------------------------------------------------------------


def test_sample_space_has_36_outcomes():
    assert len(SPACE) == 36


def test_sample_space_has_no_duplicates():
    assert len(set(SPACE)) == len(SPACE)


def test_sample_space_matches_direct_itertools_product():
    assert set(SPACE) == set(itertools.product(range(1, 7), range(1, 7)))


def test_event_of_sum_seven_has_six_outcomes():
    ev = P.event(SPACE, D.is_sum(7))
    assert ev == frozenset({(1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1)})


def test_event_of_sum_two_has_one_outcome():
    ev = P.event(SPACE, D.is_sum(2))
    assert ev == frozenset({(1, 1)})


def test_event_of_sum_twelve_has_one_outcome():
    ev = P.event(SPACE, D.is_sum(12))
    assert ev == frozenset({(6, 6)})


@pytest.mark.parametrize(
    "target,count",
    [(2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 5), (9, 4), (10, 3), (11, 2), (12, 1)],
)
def test_event_counts_for_every_possible_sum(target, count):
    assert len(P.event(SPACE, D.is_sum(target))) == count


def test_probability_of_sum_seven_is_exactly_one_sixth():
    ev = P.event(SPACE, D.is_sum(7))
    assert P.probability(ev, SPACE) == Fraction(1, 6)


def test_probability_returns_a_fraction_type():
    ev = P.event(SPACE, D.is_sum(7))
    assert isinstance(P.probability(ev, SPACE), Fraction)


def test_probability_of_the_whole_space_is_one():
    assert P.probability(SPACE, SPACE) == 1


def test_probability_of_the_empty_event_is_zero():
    assert P.probability(frozenset(), SPACE) == 0


def test_probability_of_a_double_is_one_sixth():
    ev = P.event(SPACE, D.is_double)
    assert P.probability(ev, SPACE) == Fraction(1, 6)


# ---------------------------------------------------------------------------
# Exercise 2 -- the addition rule
# ---------------------------------------------------------------------------


def test_addition_rule_matches_enumerated_union():
    a = P.event(SPACE, D.ADDITION_EVENT_A)
    b = P.event(SPACE, D.ADDITION_EVENT_B)
    p_a, p_b = P.probability(a, SPACE), P.probability(b, SPACE)
    p_ab = P.probability(a & b, SPACE)
    formula = P.addition_rule(p_a, p_b, p_ab)
    enumerated = P.probability(a | b, SPACE)
    assert formula == enumerated == Fraction(11, 36)


def test_naive_sum_overstates_by_exactly_the_intersection():
    a = P.event(SPACE, D.ADDITION_EVENT_A)
    b = P.event(SPACE, D.ADDITION_EVENT_B)
    p_a, p_b = P.probability(a, SPACE), P.probability(b, SPACE)
    p_ab = P.probability(a & b, SPACE)
    naive = P.naive_sum(p_a, p_b)
    true_union = P.addition_rule(p_a, p_b, p_ab)
    assert naive - true_union == p_ab


def test_addition_rule_reduces_to_naive_sum_for_disjoint_events():
    a = P.event(SPACE, D.is_sum(2))
    b = P.event(SPACE, D.is_sum(12))
    assert len(a & b) == 0
    p_a, p_b = P.probability(a, SPACE), P.probability(b, SPACE)
    p_ab = P.probability(a & b, SPACE)
    assert P.addition_rule(p_a, p_b, p_ab) == P.naive_sum(p_a, p_b)


@pytest.mark.parametrize(
    "target_a,target_b",
    [(4, 6), (5, 9), (7, 11)],
)
def test_addition_rule_on_further_pairs_matches_enumeration(target_a, target_b):
    a = P.event(SPACE, D.is_sum(target_a))
    b = P.event(SPACE, D.is_sum(target_b))
    p_a, p_b = P.probability(a, SPACE), P.probability(b, SPACE)
    p_ab = P.probability(a & b, SPACE)
    assert P.addition_rule(p_a, p_b, p_ab) == P.probability(a | b, SPACE)


# ---------------------------------------------------------------------------
# Exercise 3 -- the complement rule and de Méré, exact
# ---------------------------------------------------------------------------


def test_complement_of_a_sixth_is_five_sixths():
    assert P.complement(Fraction(1, 6)) == Fraction(5, 6)


def test_complement_is_its_own_inverse():
    p = Fraction(7, 20)
    assert P.complement(P.complement(p)) == p


def test_complement_of_zero_is_one():
    assert P.complement(Fraction(0)) == 1


def test_complement_of_one_is_zero():
    assert P.complement(Fraction(1)) == 0


def test_at_least_one_of_zero_trials_is_zero():
    assert P.at_least_one(Fraction(1, 6), 0) == 0


def test_at_least_one_of_a_certain_event_is_certain():
    assert P.at_least_one(Fraction(1, 1), 5) == 1


def test_de_mere_bet_one_matches_dataset_exact_value():
    assert P.at_least_one(Fraction(1, 6), D.DE_MERE_SINGLE_ROLLS) == D.DE_MERE_SINGLE_EXACT


def test_de_mere_bet_two_matches_dataset_exact_value():
    assert P.at_least_one(Fraction(1, 36), D.DE_MERE_DOUBLE_ROLLS) == D.DE_MERE_DOUBLE_EXACT


def test_de_mere_bet_one_rounds_to_the_historical_figure():
    assert round(float(D.DE_MERE_SINGLE_EXACT), 4) == 0.5177


def test_de_mere_bet_two_rounds_to_the_historical_figure():
    assert round(float(D.DE_MERE_DOUBLE_EXACT), 4) == 0.4914


def test_de_mere_bet_one_favours_the_player():
    assert D.DE_MERE_SINGLE_EXACT > Fraction(1, 2)


def test_de_mere_bet_two_does_not_favour_the_player():
    assert D.DE_MERE_DOUBLE_EXACT < Fraction(1, 2)


def test_de_mere_bets_are_not_equal_despite_the_six_to_one_scaling():
    # 24 = 6 x 4, matching the 6x smaller probability of a double six --
    # and the two bets are still not equal. That gap IS the lesson.
    assert D.DE_MERE_SINGLE_EXACT != D.DE_MERE_DOUBLE_EXACT


def test_de_mere_simulation_bet_one_within_three_standard_errors():
    rng = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
    got = S.simulate_at_least_one_six(rng, D.DE_MERE_SIM_TRIALS)
    assert abs(got - float(D.DE_MERE_SINGLE_EXACT)) < D.DE_MERE_SINGLE_TOL


def test_de_mere_simulation_bet_two_within_three_standard_errors():
    rng = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
    got = S.simulate_at_least_one_double_six(rng, D.DE_MERE_SIM_TRIALS)
    assert abs(got - float(D.DE_MERE_DOUBLE_EXACT)) < D.DE_MERE_DOUBLE_TOL


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_de_mere_simulation_bet_one_is_stable_across_seeds(seed):
    rng = np.random.default_rng(seed)
    got = S.simulate_at_least_one_six(rng, D.DE_MERE_SIM_TRIALS)
    assert abs(got - float(D.DE_MERE_SINGLE_EXACT)) < D.DE_MERE_SINGLE_TOL


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_de_mere_simulation_bet_two_is_stable_across_seeds(seed):
    rng = np.random.default_rng(seed)
    got = S.simulate_at_least_one_double_six(rng, D.DE_MERE_SIM_TRIALS)
    assert abs(got - float(D.DE_MERE_DOUBLE_EXACT)) < D.DE_MERE_DOUBLE_TOL


def test_simulate_at_least_one_six_returns_a_plain_float():
    rng = np.random.default_rng(0)
    got = S.simulate_at_least_one_six(rng, 1000)
    assert isinstance(got, float)
    assert 0.0 <= got <= 1.0


def test_simulate_at_least_one_double_six_returns_a_plain_float():
    rng = np.random.default_rng(0)
    got = S.simulate_at_least_one_double_six(rng, 1000)
    assert isinstance(got, float)
    assert 0.0 <= got <= 1.0


# ---------------------------------------------------------------------------
# Exercise 4 -- independence
# ---------------------------------------------------------------------------


def _pair_stats(pred_a, pred_b):
    a = P.event(SPACE, pred_a)
    b = P.event(SPACE, pred_b)
    p_a, p_b = P.probability(a, SPACE), P.probability(b, SPACE)
    p_ab = P.probability(a & b, SPACE)
    return p_a, p_b, p_ab


def test_the_independent_pair_satisfies_the_product_rule_exactly():
    p_a, p_b, p_ab = _pair_stats(*D.INDEPENDENT_PAIR)
    assert p_ab == p_a * p_b
    assert P.is_independent(p_a, p_b, p_ab) is True


def test_the_dependent_pair_fails_the_product_rule():
    p_a, p_b, p_ab = _pair_stats(*D.DEPENDENT_PAIR)
    assert p_ab != p_a * p_b
    assert P.is_independent(p_a, p_b, p_ab) is False


def test_is_independent_returns_a_python_bool():
    p_a, p_b, p_ab = _pair_stats(*D.INDEPENDENT_PAIR)
    assert isinstance(P.is_independent(p_a, p_b, p_ab), bool)


@pytest.mark.parametrize("first_die_value", [1, 2, 4, 5, 6])
def test_sum_seven_is_independent_of_every_value_of_the_first_die(first_die_value):
    # The independence of "sum = 7" from the first die is not special to the
    # value 3 -- it holds for every value, because exactly one second-die
    # value completes the sum to 7 regardless.
    p_a, p_b, p_ab = _pair_stats(D.is_sum(7), D.is_first_die(first_die_value))
    assert p_ab == p_a * p_b


# ---------------------------------------------------------------------------
# Exercise 5 -- mutual exclusivity implies dependence
# ---------------------------------------------------------------------------


def test_mutually_exclusive_pair_has_empty_intersection():
    pred_a, pred_b = D.MUTUALLY_EXCLUSIVE_PAIR
    a, b = P.event(SPACE, pred_a), P.event(SPACE, pred_b)
    assert (a & b) == frozenset()


def test_mutually_exclusive_pair_has_zero_conditional_probability():
    pred_a, pred_b = D.MUTUALLY_EXCLUSIVE_PAIR
    a, b = P.event(SPACE, pred_a), P.event(SPACE, pred_b)
    p_ab = P.probability(a & b, SPACE)
    p_b = P.probability(b, SPACE)
    assert P.conditional(p_ab, p_b) == 0


def test_mutually_exclusive_pair_is_therefore_dependent():
    pred_a, pred_b = D.MUTUALLY_EXCLUSIVE_PAIR
    a, b = P.event(SPACE, pred_a), P.event(SPACE, pred_b)
    p_a = P.probability(a, SPACE)
    p_ab = P.probability(a & b, SPACE)
    p_b = P.probability(b, SPACE)
    p_a_given_b = P.conditional(p_ab, p_b)
    assert p_a != 0
    assert p_a_given_b != p_a


def test_conditional_refuses_to_divide_by_a_zero_probability_event():
    with pytest.raises(ValueError):
        P.conditional(Fraction(0), Fraction(0))


# ---------------------------------------------------------------------------
# Exercise 6 -- conditioning by restriction
# ---------------------------------------------------------------------------


def test_conditional_by_formula_matches_filtering_the_space():
    a = P.event(SPACE, D.CONDITIONING_EVENT_A)
    b = P.event(SPACE, D.CONDITIONING_EVENT_B)
    p_ab = P.probability(a & b, SPACE)
    p_b = P.probability(b, SPACE)
    by_formula = P.conditional(p_ab, p_b)

    restricted_event = P.event(b, D.CONDITIONING_EVENT_A)
    by_filtering = P.probability(restricted_event, b)

    assert by_formula == by_filtering == Fraction(1, 6)


@pytest.mark.parametrize("sum_target", [4, 6, 8, 10])
def test_conditioning_on_first_die_even_matches_filtering_for_several_sums(sum_target):
    b = P.event(SPACE, D.first_die_even)
    a = P.event(SPACE, D.is_sum(sum_target))
    p_ab = P.probability(a & b, SPACE)
    p_b = P.probability(b, SPACE)
    by_formula = P.conditional(p_ab, p_b)
    by_filtering = P.probability(P.event(b, D.is_sum(sum_target)), b)
    assert by_formula == by_filtering


def test_conditioning_on_the_whole_space_changes_nothing():
    a = P.event(SPACE, D.is_sum(7))
    p_a = P.probability(a, SPACE)
    p_a_and_space = P.probability(a & frozenset(SPACE), SPACE)
    p_space = P.probability(SPACE, SPACE)
    assert P.conditional(p_a_and_space, p_space) == p_a


# ---------------------------------------------------------------------------
# Exercise 7 -- the law of total probability
# ---------------------------------------------------------------------------


def test_total_probability_matches_the_documented_answer():
    assert P.total_probability(D.URN_PRIOR, D.URN_CONDITIONAL_RED) == Fraction(9, 20)


def test_total_probability_matches_the_combined_enumeration():
    urn1 = ["red"] * D.URN_1_RED + ["blue"] * D.URN_1_BLUE
    urn2 = ["red"] * D.URN_2_RED + ["blue"] * D.URN_2_BLUE
    combined = [("urn1", b) for b in urn1] + [("urn2", b) for b in urn2]
    reds = [o for o in combined if o[1] == "red"]
    enumerated = Fraction(len(reds), len(combined))
    assert P.total_probability(D.URN_PRIOR, D.URN_CONDITIONAL_RED) == enumerated


def test_total_probability_with_a_certain_prior_reduces_to_one_conditional():
    priors = (Fraction(1), Fraction(0))
    conditionals = (Fraction(3, 10), Fraction(9, 10))
    assert P.total_probability(priors, conditionals) == Fraction(3, 10)


def test_total_probability_of_blue_plus_red_is_one():
    urn_conditional_blue = (
        Fraction(D.URN_1_BLUE, 10),
        Fraction(D.URN_2_BLUE, 10),
    )
    p_red = P.total_probability(D.URN_PRIOR, D.URN_CONDITIONAL_RED)
    p_blue = P.total_probability(D.URN_PRIOR, urn_conditional_blue)
    assert p_red + p_blue == 1


# ---------------------------------------------------------------------------
# Exercise 8 -- Monte Carlo error scaling
# ---------------------------------------------------------------------------


def test_standard_error_shrinks_as_n_grows():
    small = D.standard_error(0.5, 100)
    large = D.standard_error(0.5, 100_000)
    assert large < small


def test_standard_error_of_a_certain_event_is_zero():
    assert D.standard_error(1.0, 1000) == 0.0
    assert D.standard_error(0.0, 1000) == 0.0


def test_standard_error_is_maximised_at_p_one_half():
    assert D.standard_error(0.5, 1000) > D.standard_error(0.1, 1000)
    assert D.standard_error(0.5, 1000) > D.standard_error(0.9, 1000)


def test_monte_carlo_mean_error_decreases_across_the_four_sample_sizes():
    target = float(D.MONTE_CARLO_TARGET)
    means = []
    for n in D.MONTE_CARLO_SAMPLE_SIZES:
        errors = [
            abs(S.simulate_sum_seven(np.random.default_rng(seed), n) - target)
            for seed in D.MONTE_CARLO_SEEDS
        ]
        means.append(sum(errors) / len(errors))
    assert all(means[i + 1] < means[i] for i in range(len(means) - 1))


def test_monte_carlo_error_shrink_is_closer_to_sqrt_n_than_to_n():
    target = float(D.MONTE_CARLO_TARGET)
    n_small, n_large = D.MONTE_CARLO_SAMPLE_SIZES[0], D.MONTE_CARLO_SAMPLE_SIZES[-1]

    def mean_error(n):
        errors = [
            abs(S.simulate_sum_seven(np.random.default_rng(seed), n) - target)
            for seed in D.MONTE_CARLO_SEEDS
        ]
        return sum(errors) / len(errors)

    ratio = mean_error(n_small) / mean_error(n_large)
    n_ratio = n_large / n_small
    sqrt_prediction = n_ratio**0.5
    assert 0.33 * sqrt_prediction < ratio < 3.0 * sqrt_prediction
    assert ratio < n_ratio / 10.0


def test_simulate_sum_seven_is_close_to_one_sixth_at_a_large_sample():
    rng = np.random.default_rng(123)
    got = S.simulate_sum_seven(rng, 500_000)
    assert abs(got - 1.0 / 6.0) < 4.0 * D.standard_error(1.0 / 6.0, 500_000)


# ---------------------------------------------------------------------------
# Exercise 9 -- reproducibility
# ---------------------------------------------------------------------------


def test_same_seed_gives_byte_identical_results():
    a1 = S.simulate_sum_seven(np.random.default_rng(D.REPRODUCIBILITY_SEED_A), 10_000)
    a2 = S.simulate_sum_seven(np.random.default_rng(D.REPRODUCIBILITY_SEED_A), 10_000)
    assert a1 == a2


def test_different_seeds_give_different_results():
    a = S.simulate_sum_seven(np.random.default_rng(D.REPRODUCIBILITY_SEED_A), 10_000)
    b = S.simulate_sum_seven(np.random.default_rng(D.REPRODUCIBILITY_SEED_B), 10_000)
    assert a != b


def test_different_seeds_both_still_estimate_the_true_value():
    target = 1.0 / 6.0
    tol = 4.0 * D.standard_error(target, D.REPRODUCIBILITY_TRIALS)
    for seed in (D.REPRODUCIBILITY_SEED_A, D.REPRODUCIBILITY_SEED_B):
        got = S.simulate_sum_seven(np.random.default_rng(seed), D.REPRODUCIBILITY_TRIALS)
        assert abs(got - target) < tol


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4])
def test_reproducibility_holds_across_several_seeds(seed):
    a1 = S.simulate_at_least_one_six(np.random.default_rng(seed), 5_000)
    a2 = S.simulate_at_least_one_six(np.random.default_rng(seed), 5_000)
    assert a1 == a2


def test_two_generators_from_the_same_seed_produce_identical_raw_draws():
    rng1 = np.random.default_rng(7)
    rng2 = np.random.default_rng(7)
    draws1 = rng1.integers(1, 7, size=100)
    draws2 = rng2.integers(1, 7, size=100)
    assert np.array_equal(draws1, draws2)


def test_a_single_generator_does_not_repeat_its_own_draws():
    rng = np.random.default_rng(7)
    first = rng.integers(1, 7, size=100)
    second = rng.integers(1, 7, size=100)
    assert not np.array_equal(first, second)
