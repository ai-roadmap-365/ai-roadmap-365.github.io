"""Fourteen exercises in what each way of splitting a dataset costs.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`splits_lib.py` is complete -- it is the machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

from sklearn.linear_model import LogisticRegression  # noqa: F401

import splits_lib as s  # noqa: F401  (you will need it)


@pytest.fixture(scope="module")
def rare():
    return s.rare_class_dataset()


@pytest.fixture(scope="module")
def grouped():
    return s.grouped_dataset()


@pytest.fixture(scope="module")
def weak():
    return s.weak_signal_dataset()


def test_01_picking_the_best_of_k_inflates_the_score_you_picked_it_by():
    pytest.skip(
        "Assert s.selection_bias_curve([1, 2, 5, 10, 25, 50, 100, 500, 1000]) "
        "equals the nine rows in expected-output/measured-values.txt, from "
        "(1, 0.4984, 0.5011, -0.0028) to (1000, 0.572, 0.4992, 0.0728). Then "
        "assert the validation column is strictly increasing in K. Every "
        "candidate is a coin flip with exactly zero skill, so all of that "
        "climb is noise you selected."
    )


def test_01b_the_test_set_is_the_control_and_stays_at_chance():
    pytest.skip(
        "For K in [1, 10, 100, 1000], assert every test score is within "
        "0.005 of 0.5 and that the whole test column spans less than 0.005, "
        "while the validation column climbs by more than 0.07. The test set "
        "was never selected on, so it was never inflated -- and that is what "
        "makes the validation column mean anything."
    )


def test_01c_the_optimism_is_the_expected_maximum_of_k_noise_draws():
    pytest.skip(
        "Assert s.proportion_standard_error(0.5, 500) rounds to 0.0224. For "
        "each K in [2, 5, 10, 25, 50, 100, 500, 1000], divide the optimism "
        "by that standard error and assert it is within 0.2 of "
        "s.expected_max_of_normals(k), and that s.sqrt_two_log_k(k) is "
        "LARGER than the simulated expectation at every K. Then assert the "
        "concrete case: at K=100 the measured optimism is 2.57 standard "
        "errors, the simulated expectation is 2.50, and the textbook "
        "approximation says 3.03."
    )


def test_02_a_random_split_of_a_rare_class_sometimes_has_no_positives(rare):
    pytest.skip(
        "The population positive rate is 0.05. Assert s.split_positive_rates "
        "gives random spread {'mean': 0.0504, 'sd': 0.0265, 'min': 0.0, "
        "'max': 0.16} and stratified spread {'mean': 0.05, 'sd': 0.01, "
        "'min': 0.04, 'max': 0.06}, and that exactly 21 of the 500 random "
        "splits produced a test half with no positives at all. Recall is "
        "undefined on those."
    )


def test_02b_stratifying_shrinks_the_spread_without_changing_the_mean(rare):
    pytest.skip(
        "Assert the two means agree to within 0.001 while the stratified "
        "standard deviation is smaller, with a ratio of exactly 2.65. Then "
        "assert the random split's worst case is 3.2 times the population "
        "positive rate. Stratifying does not change what you are estimating; "
        "it changes how much the estimate wobbles."
    )


def test_03_splitting_rows_when_the_unit_is_a_person_invents_fifty_six_points(grouped):
    pytest.skip(
        "Assert s.rowwise_vs_group_split gives 0.976 for the row-wise split "
        "and 0.4112 for the group-aware one, a gap of 0.5648. Then assert "
        "the group-aware score is below 0.5 and the row-wise one above it. "
        "Each person's label is a coin flip, so there is nothing "
        "generalisable here at all -- and a row-wise split reports 97.6 "
        "percent."
    )


def test_03b_every_single_person_appears_in_both_halves(grouped):
    pytest.skip(
        "Assert s.groups_shared_between_halves returns 50, that there are 50 "
        "distinct people, and that the dataset has 1000 rows. With twenty "
        "rows each, a random quarter cannot miss anybody -- which is the "
        "mechanism behind exercise 3, stated as a count rather than as an "
        "intuition."
    )


def test_04_a_shuffled_split_beats_a_chronological_one_every_single_time():
    pytest.skip(
        "Call s.temporal_inflation_over_constructions(). Assert there are 20 "
        "rows and that the inflation is positive in every single one. The "
        "direction of this effect is universal; the next exercise is about "
        "its size."
    )


def test_04b_but_the_size_of_the_effect_varies_by_an_order_of_magnitude():
    pytest.skip(
        "Assert the means across 20 constructions are shuffled 0.5961, "
        "chronological 0.5233 and baseline 0.5235, with inflation mean "
        "0.0728, sd 0.0596, min 0.016 and max 0.2557 -- a factor of 16.0 "
        "between smallest and largest. Assert the chronological score is "
        "within 0.005 of the baseline while the shuffled one is above it. "
        "Quoting the 0.2557 seed alone would be the forking-paths problem, "
        "in a lab against it."
    )


def test_05_one_holdout_swings_nineteen_points_on_identical_data(weak):
    pytest.skip(
        "Assert s.holdout_vs_cross_validation gives holdout spread {'mean': "
        "0.7519, 'sd': 0.0381, 'min': 0.66, 'max': 0.85} and 5-fold spread "
        "{'mean': 0.7546, 'sd': 0.0061, 'min': 0.7375, 'max': 0.77}. Assert "
        "the holdout range is exactly 0.19 and the cross-validated range "
        "0.0325. Same data, same model: only which rows landed where changed."
    )


def test_05b_cross_validation_is_six_times_steadier_for_the_same_data(weak):
    pytest.skip(
        "Assert the ratio of the two standard deviations is 6.2344, and that "
        "the two means agree to within 0.003. Cross-validation estimates the "
        "same quantity; it just estimates it with far less noise, because "
        "every row serves as test data exactly once."
    )


def test_06_the_standard_error_formula_predicts_the_measured_spread():
    pytest.skip(
        "Assert s.test_size_table([50, 100, 200, 500, 1000, 5000]) matches "
        "the captured rows, and that theory and measurement differ by at "
        "most 0.0002 at every size. Then assert the scaling: quadrupling the "
        "rows halves the error (200 against 50 gives a ratio of 0.5), and "
        "5000 against 500 gives 0.31. This is Day 117's formula arriving "
        "where the decisions are."
    )


def test_06b_a_hundred_row_test_set_cannot_resolve_a_five_point_difference():
    pytest.skip(
        "Assert the 95 percent half-width at n=100 is 0.07, which is wider "
        "than 0.05 -- so two models five points apart are indistinguishable "
        "on it. Then assert s.rows_needed_for_precision(0.85, 0.02) is 1225 "
        "and (0.85, 0.01) is 4899. Decide how big your test set must be "
        "BEFORE you split, from the difference you need to detect."
    )


def test_07_the_test_set_permits_exactly_one_evaluation(weak):
    pytest.skip(
        "Fit LogisticRegression(max_iter=1000) on the weak-signal data, wrap "
        "the data in s.GatedTestSet, and assert the first evaluation is "
        "0.7575 and the counter becomes 1. Then assert a second evaluation "
        "raises s.TestSetTouchedTwice with a message mentioning 'validation "
        "score', and that the counter did NOT advance on the refused "
        "attempt. The gate is not a substitute for discipline; it is the "
        "discipline made mechanical."
    )
