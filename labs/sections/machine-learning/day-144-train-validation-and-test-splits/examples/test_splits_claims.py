"""The reference solutions: what each way of splitting a dataset costs.

Every number here was captured from a real run of this file on the
authoring machine. If a number changes, the claim in the lesson is wrong
and one of the two must be fixed.
"""

import numpy as np
import pytest

from sklearn.linear_model import LogisticRegression

import splits_lib as s


@pytest.fixture(scope="module")
def rare():
    return s.rare_class_dataset()


@pytest.fixture(scope="module")
def grouped():
    return s.grouped_dataset()


@pytest.fixture(scope="module")
def weak():
    return s.weak_signal_dataset()


# --- 1. Why three sets and not two --------------------------------------


def test_01_picking_the_best_of_k_inflates_the_score_you_picked_it_by():
    rows = s.selection_bias_curve([1, 2, 5, 10, 25, 50, 100, 500, 1000])
    assert rows == [
        (1, 0.4984, 0.5011, -0.0028),
        (2, 0.5115, 0.4992, 0.0123),
        (5, 0.5256, 0.5005, 0.0251),
        (10, 0.5331, 0.4999, 0.0332),
        (25, 0.5436, 0.5009, 0.0427),
        (50, 0.5508, 0.5014, 0.0493),
        (100, 0.5567, 0.4992, 0.0575),
        (500, 0.5682, 0.4978, 0.0704),
        (1000, 0.572, 0.4992, 0.0728),
    ]
    validation = [v for _k, v, _t, _o in rows]
    # The validation score climbs with every extra candidate considered.
    assert all(a < b for a, b in zip(validation, validation[1:]))
    # Every candidate has exactly zero skill: these are coin flips.
    assert rows[-1][1] > rows[0][1] + 0.07


def test_01b_the_test_set_is_the_control_and_stays_at_chance():
    rows = s.selection_bias_curve([1, 10, 100, 1000])
    test_scores = [t for _k, _v, t, _o in rows]
    # Never selected on, therefore never inflated -- at any K.
    for score in test_scores:
        assert abs(score - 0.5) < 0.005
    assert max(test_scores) - min(test_scores) < 0.005
    # This is what makes the validation column mean something.
    validation = [v for _k, v, _t, _o in rows]
    assert validation[-1] - validation[0] > 0.07


def test_01c_the_optimism_is_the_expected_maximum_of_k_noise_draws():
    """And the usual closed-form approximation overestimates it."""
    standard_error = s.proportion_standard_error(0.5, 500)
    assert round(standard_error, 4) == 0.0224

    rows = s.selection_bias_curve([2, 5, 10, 25, 50, 100, 500, 1000])
    for k, _validation, _test, optimism in rows:
        in_errors = optimism / standard_error
        simulated = s.expected_max_of_normals(k)
        approximation = s.sqrt_two_log_k(k)
        # Measurement tracks the simulated expected maximum closely.
        assert abs(in_errors - simulated) < 0.2, (k, in_errors, simulated)
        # The sqrt(2 ln K) asymptotic is above it at every K tried here.
        assert approximation > simulated

    # Concretely, at K = 100: 2.57 standard errors measured, 2.50 expected,
    # against the approximation's 3.03.
    optimism_100 = dict((k, o) for k, _v, _t, o in rows)[100]
    assert round(optimism_100 / standard_error, 2) == 2.57
    assert round(s.expected_max_of_normals(100), 2) == 2.5
    assert round(s.sqrt_two_log_k(100), 2) == 3.03


# --- 2. Stratification ---------------------------------------------------


def test_02_a_random_split_of_a_rare_class_sometimes_has_no_positives(rare):
    X, y = rare
    assert round(float(y.mean()), 4) == 0.05
    random_rates, stratified_rates, empty = s.split_positive_rates(X, y)
    assert s.spread(random_rates) == {"mean": 0.0504, "sd": 0.0265, "min": 0.0, "max": 0.16}
    assert s.spread(stratified_rates) == {"mean": 0.05, "sd": 0.01, "min": 0.04, "max": 0.06}
    # Twenty-one splits in five hundred produced a test set with no
    # positives at all, on which recall is undefined.
    assert empty == 21
    assert 0 in [round(r, 4) for r in random_rates]
    assert 0 not in [round(r, 4) for r in stratified_rates]


def test_02b_stratifying_shrinks_the_spread_without_changing_the_mean(rare):
    X, y = rare
    random_rates, stratified_rates, _empty = s.split_positive_rates(X, y)
    random = s.spread(random_rates)
    stratified = s.spread(stratified_rates)
    assert abs(random["mean"] - stratified["mean"]) < 0.001
    assert stratified["sd"] < random["sd"]
    assert round(random["sd"] / stratified["sd"], 2) == 2.65
    # The random split's worst case is three times the population rate.
    assert round(random["max"] / float(y.mean()), 2) == 3.2


# --- 3. Groups -----------------------------------------------------------


def test_03_splitting_rows_when_the_unit_is_a_person_invents_fifty_six_points(grouped):
    X, y, groups = grouped
    rowwise, group_aware = s.rowwise_vs_group_split(X, y, groups)
    assert round(rowwise, 4) == 0.976
    assert round(group_aware, 4) == 0.4112
    assert round(rowwise - group_aware, 4) == 0.5648
    # There is nothing generalisable in this data at all: each person's
    # label is a coin flip, so the group-aware score is chance, and low.
    assert group_aware < 0.5 < rowwise


def test_03b_every_single_person_appears_in_both_halves(grouped):
    _X, _y, groups = grouped
    shared = s.groups_shared_between_halves(groups)
    assert shared == 50
    assert len(set(groups.tolist())) == 50
    # Twenty rows each: a random quarter cannot miss anybody.
    assert len(groups) == 1000


# --- 4. Time -------------------------------------------------------------


def test_04_a_shuffled_split_beats_a_chronological_one_every_single_time():
    rows = s.temporal_inflation_over_constructions()
    assert len(rows) == 20
    inflation = [gap for _seed, _sh, _ch, _base, gap in rows]
    # The direction is universal across twenty independent constructions.
    assert all(gap > 0 for gap in inflation)
    assert sum(1 for gap in inflation if gap > 0) == 20


def test_04b_but_the_size_of_the_effect_varies_by_an_order_of_magnitude():
    rows = s.temporal_inflation_over_constructions()
    shuffled = float(np.mean([sh for _s, sh, _c, _b, _g in rows]))
    chronological = float(np.mean([ch for _s, _sh, ch, _b, _g in rows]))
    baseline = float(np.mean([b for _s, _sh, _ch, b, _g in rows]))
    inflation = [gap for _s, _sh, _ch, _b, gap in rows]
    assert round(shuffled, 4) == 0.5961
    assert round(chronological, 4) == 0.5233
    assert round(baseline, 4) == 0.5235
    assert round(float(np.mean(inflation)), 4) == 0.0728
    assert round(float(np.std(inflation)), 4) == 0.0596
    assert round(min(inflation), 4) == 0.016
    assert round(max(inflation), 4) == 0.2557
    # Sixteen times between the smallest and largest effect: reporting the
    # largest would be the forking-paths problem in a lesson against it.
    assert round(max(inflation) / min(inflation), 1) == 16.0
    # The honest verdict: chronologically, the model has learned nothing.
    assert abs(chronological - baseline) < 0.005
    assert shuffled > baseline


# --- 5. One holdout, or many folds --------------------------------------


def test_05_one_holdout_swings_nineteen_points_on_identical_data(weak):
    X, y = weak
    holdout, cross = s.holdout_vs_cross_validation(X, y)
    assert s.spread(holdout) == {"mean": 0.7519, "sd": 0.0381, "min": 0.66, "max": 0.85}
    assert s.spread(cross) == {"mean": 0.7546, "sd": 0.0061, "min": 0.7375, "max": 0.77}
    # Same data, same model. Only which rows landed where changed.
    assert round(max(holdout) - min(holdout), 4) == 0.19
    assert round(max(cross) - min(cross), 4) == 0.0325


def test_05b_cross_validation_is_six_times_steadier_for_the_same_data(weak):
    X, y = weak
    holdout, cross = s.holdout_vs_cross_validation(X, y)
    ratio = float(np.std(holdout) / np.std(cross))
    assert round(ratio, 4) == 6.2344
    # It estimates the same thing -- the means agree to within 0.003.
    assert abs(float(np.mean(holdout)) - float(np.mean(cross))) < 0.003


# --- 6. How big must the test set be? -----------------------------------


def test_06_the_standard_error_formula_predicts_the_measured_spread():
    rows = s.test_size_table([50, 100, 200, 500, 1000, 5000])
    assert rows == [
        (50, 0.0505, 0.0505, 0.099),
        (100, 0.0357, 0.0357, 0.07),
        (200, 0.0252, 0.0254, 0.0495),
        (500, 0.016, 0.016, 0.0313),
        (1000, 0.0113, 0.0112, 0.0221),
        (5000, 0.005, 0.0051, 0.0099),
    ]
    for _n, theory, measured, _half in rows:
        assert abs(theory - measured) <= 0.0002
    # Four times the rows halves the error, not quarters it.
    by_n = {n: theory for n, theory, _m, _h in rows}
    assert round(by_n[200] / by_n[50], 2) == 0.5
    assert round(by_n[5000] / by_n[500], 2) == 0.31


def test_06b_a_hundred_row_test_set_cannot_resolve_a_five_point_difference():
    half_width = s.test_size_table([100])[0][3]
    assert half_width == 0.07
    # Plus or minus seven points: two models five points apart are
    # indistinguishable on it.
    assert half_width > 0.05
    assert s.rows_needed_for_precision(0.85, 0.02) == 1225
    assert s.rows_needed_for_precision(0.85, 0.01) == 4899


# --- 7. The rule, made mechanical ---------------------------------------


def test_07_the_test_set_permits_exactly_one_evaluation(weak):
    X, y = weak
    model = LogisticRegression(max_iter=1000).fit(X, y)
    gate = s.GatedTestSet(X, y)
    assert gate.evaluations == 0
    first = gate.evaluate(model)
    assert round(first, 4) == 0.7575
    assert gate.evaluations == 1
    with pytest.raises(s.TestSetTouchedTwice) as excinfo:
        gate.evaluate(model)
    assert "validation score" in str(excinfo.value)
    # And the counter does not advance on a refused attempt.
    assert gate.evaluations == 1
