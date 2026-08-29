"""The reference solutions: the two failures, decomposed and measured.

Every number here was captured from a real run of this file on the
authoring machine. If a number changes, the claim in the lesson is wrong
and one of the two must be fixed.
"""

import numpy as np
import pytest

import fitting_lib as f


# --- 1. The capacity sweep -----------------------------------------------


def test_01_training_error_falls_with_capacity_and_test_error_does_not():
    rows = f.capacity_sweep([1, 2, 3, 4, 6, 8, 10, 14, 18, 24])
    assert rows == [
        (1, 11.3217, 9.8274, -1.4942),
        (2, 11.3173, 9.8801, -1.4372),
        (3, 2.7076, 6.123, 3.4154),
        (4, 2.4964, 5.4911, 2.9948),
        (6, 1.9569, 15.8217, 13.8648),
        (8, 1.701, 26.1708, 24.4697),
        (10, 1.357, 528.4798, 527.1227),
        (14, 0.9685, 31307.2782, 31306.3097),
        (18, 1.0037, 75539.3618, 75538.3581),
        (24, 1.0321, 226667.4689, 226666.4368),
    ]
    # Test error is U-shaped: it falls, bottoms, then explodes.
    assert f.best_degree(rows) == 4
    test = [row[2] for row in rows]
    assert test[0] > test[3] < test[-1]
    assert test[-1] / test[3] > 40_000


def test_01b_training_error_falls_until_the_numerics_give_out():
    rows = f.capacity_sweep([1, 2, 3, 4, 6, 8, 10, 14, 18, 24])
    train = [row[1] for row in rows]
    # Monotone through degree 14, then it wobbles by about 0.06.
    assert f.is_monotonically_decreasing(train[:8])
    assert not f.is_monotonically_decreasing(train)
    assert round(max(train[7:]) - min(train[7:]), 4) == 0.0636
    # That wobble is numerical, not statistical: the training set has 25
    # rows and degree 24 supplies exactly 25 features.
    assert train[7] < 1.0 < train[-1]


def test_01c_the_generalisation_gap_is_the_diagnostic():
    rows = f.capacity_sweep([1, 2, 3, 4, 6, 8, 10, 14, 18, 24])
    gaps = {degree: gap for degree, _tr, _te, gap in rows}
    # Underfitting: the gap is NEGATIVE. Test error is below training
    # error, because the model is too rigid to have chased any noise.
    assert gaps[1] < 0 and gaps[2] < 0
    # The best model has a small positive gap.
    assert 0 < gaps[4] < 3.0
    # Overfitting: the gap is the error.
    assert gaps[24] > 200_000


# --- 2. Regularisation ---------------------------------------------------


def test_02_a_penalty_rescues_the_same_model_class():
    rows = f.regularisation_sweep([0.0, 1e-6, 1e-3, 0.1, 1.0, 10.0, 100.0])
    assert rows == [
        (0.0, 1.0321, 226667.4689),
        (1e-06, 1.2031, 130776.6548),
        (0.001, 1.5741, 128.3127),
        (0.1, 2.2259, 15.8339),
        (1.0, 2.7461, 5.7257),
        (10.0, 3.9689, 6.1559),
        (100.0, 6.28, 6.784),
    ]
    # Same degree, same data. Only the penalty changed.
    assert f.best_alpha(rows) == 1.0
    unpenalised = rows[0][2]
    best = min(row[2] for row in rows)
    assert round(unpenalised / best, 0) == 39588.0


def test_02b_the_penalty_trades_training_error_for_test_error():
    rows = f.regularisation_sweep([0.0, 1e-6, 1e-3, 0.1, 1.0, 10.0, 100.0])
    train = [row[1] for row in rows]
    # Training error rises monotonically with the penalty, always.
    assert all(a < b for a, b in zip(train, train[1:]))
    # Test error is U-shaped in the penalty too: too much is also wrong.
    test = [row[2] for row in rows]
    assert test[4] < test[5] < test[6]
    # And the best-regularised degree-24 model is close to the best
    # unregularised degree-4 one, from a completely different direction.
    sweep = f.capacity_sweep([4])
    assert abs(min(test) - sweep[0][2]) < 0.3


# --- 3. What more data fixes ---------------------------------------------


def test_03_more_data_cures_overfitting_and_does_nothing_for_underfitting():
    rows = f.data_sweep([15, 25, 50, 100, 400, 2000])
    assert rows == [
        (15, {1: 8.5023, 4: 4.9218, 24: 215413.2388}),
        (25, {1: 8.862, 4: 6.1904, 24: 64631547.2994}),
        (50, {1: 8.2457, 4: 4.2661, 24: 6070.3302}),
        (100, {1: 8.3583, 4: 4.2934, 24: 5.3571}),
        (400, {1: 8.3007, 4: 3.9958, 24: 4.3139}),
        (2000, {1: 8.2393, 4: 3.988, 24: 4.0055}),
    ]
    underfit = [scores[1] for _n, scores in rows]
    overfit = [scores[24] for _n, scores in rows]
    # The underfit model is flat: 133 times more data buys 0.26.
    assert round(max(underfit) - min(underfit), 4) == 0.6227
    assert abs(underfit[0] - underfit[-1]) < 0.3
    # The overfit model falls by seven orders of magnitude.
    assert overfit[1] / overfit[-1] > 1e7


def test_03b_both_good_models_converge_to_the_irreducible_floor():
    rows = f.data_sweep([15, 25, 50, 100, 400, 2000])
    floor = f.irreducible_variance()
    assert floor == 4.0
    at_2000 = dict(rows[-1][1])
    # Degree 4 and degree 24 both land on the floor, from opposite sides.
    assert abs(at_2000[4] - floor) < 0.02
    assert abs(at_2000[24] - floor) < 0.01
    # The underfit model never gets near it, at any amount of data.
    assert at_2000[1] > floor * 2


def test_03c_the_overfit_column_peaks_at_the_interpolation_threshold():
    """Degree 24 supplies exactly 25 features, so n=25 is the worst case."""
    rows = f.data_sweep([15, 25, 50, 100, 400, 2000])
    overfit = [scores[24] for _n, scores in rows]
    # Not monotone: it gets worse before it gets better.
    assert overfit[1] > overfit[0]
    assert overfit[1] == max(overfit)
    # And the peak is exactly where features equal rows.
    from sklearn.preprocessing import PolynomialFeatures

    n_features = PolynomialFeatures(24).fit_transform(np.zeros((3, 1))).shape[1]
    assert n_features == 25
    assert rows[1][0] == n_features


# --- 4. The decomposition ------------------------------------------------


def test_04_underfitting_is_bias_and_overfitting_is_variance():
    underfit = f.bias_variance(1)
    right = f.bias_variance(3)
    overfit = f.bias_variance(12)

    assert underfit["bias_squared"] == 4.2985
    assert underfit["variance"] == 0.7112
    assert right["bias_squared"] == 0.0033
    assert right["variance"] == 0.8399
    assert overfit["bias_squared"] == 2803.5354
    assert overfit["variance"] == 452183.1336

    # Underfitting: bias dominates variance by a factor of six.
    assert underfit["bias_squared"] / underfit["variance"] > 6
    # The true function is a cubic, so at degree 3 the bias vanishes.
    assert right["bias_squared"] < 0.01
    # Overfitting: variance dominates bias by a factor of a hundred.
    assert overfit["variance"] / overfit["bias_squared"] > 100


def test_04b_the_decomposition_predicts_the_error_that_was_observed():
    """Bias squared plus variance plus noise equals the error, measured.

    The tolerance is 1.1 percent rather than something tighter because the
    observed term is itself a Monte Carlo estimate over 40,000 noisy
    targets and carries its own sampling error. The worst disagreement
    across seven capacities is 1.003 percent, at degree 6; five of the
    seven agree to better than a quarter of a percent.
    """
    worst = 0.0
    for degree in (1, 2, 3, 4, 6, 8, 12):
        result = f.bias_variance(degree)
        predicted = result["predicted_total"]
        observed = result["observed"]
        relative = abs(predicted - observed) / observed
        worst = max(worst, relative)
        assert relative < 0.011, (degree, result)
        # And the three parts sum to the total. The tolerance is 0.0002
        # because each part is stored already rounded to four places, so
        # summing the rounded parts can differ from the rounded sum by up
        # to half a unit in the last place per part.
        parts = result["bias_squared"] + result["variance"] + result["noise"]
        assert abs(parts - predicted) <= 0.0002, (degree, parts, predicted)
    assert round(worst, 5) == 0.01003


def test_04c_a_bigger_model_class_is_not_always_less_biased():
    """Degree 2 has MORE bias than degree 1, on an odd true function."""
    one = f.bias_variance(1)
    two = f.bias_variance(2)
    assert one["bias_squared"] == 4.2985
    assert two["bias_squared"] == 4.3342
    assert two["bias_squared"] > one["bias_squared"]
    # And it pays for that with double the variance.
    assert two["variance"] > 2 * one["variance"] - 0.01
    # So degree 2 is worse than degree 1 on both counts.
    assert two["predicted_total"] > one["predicted_total"]


# --- 5. Early stopping ---------------------------------------------------


def test_05_training_longer_makes_training_error_better_and_the_model_worse():
    train, test = f.training_history()
    assert len(train) == len(test) == 600
    # Training error falls at every single epoch, for six hundred epochs.
    assert f.is_monotonically_decreasing(train)
    assert round(train[0], 4) == 7.3906
    assert round(train[-1], 4) == 2.4744
    # Test error bottoms at epoch 14 and is worse at 600.
    best = int(np.argmin(test))
    assert best == 13
    assert round(test[best], 4) == 5.4555
    assert round(test[-1], 4) == 5.8978
    assert test[-1] > test[best]


def test_05b_the_generalisation_gap_grows_while_training_error_falls():
    train, test = f.training_history()
    first_gap = test[0] - train[0]
    last_gap = test[-1] - train[-1]
    assert round(first_gap, 4) == 0.6771
    assert round(last_gap, 4) == 3.4234
    assert last_gap / first_gap > 5


def test_05c_the_test_curve_is_not_a_clean_u_which_is_why_patience_exists():
    _train, test = f.training_history()
    best = int(np.argmin(test))
    after = test[best + 1 :]
    # It rises to 7.1435, then recovers to 5.8978 -- without ever again
    # beating the 5.4555 it reached at epoch 14.
    assert round(max(after), 4) == 7.1435
    assert round(test[-1], 4) == 5.8978
    assert min(after) > test[best]
    # 599 of the 600 epochs are worse than the best one.
    assert sum(1 for v in test if v > min(test)) == 599
    # Here every patience from 5 to 50 recovers the true best epoch --
    # but that is luck on this run, not a property of the rule.
    for patience in (5, 10, 20, 50):
        assert f.stop_with_patience(test, patience) == best
    assert f.first_increase(test) == best + 1
