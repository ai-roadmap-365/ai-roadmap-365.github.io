"""Fourteen exercises in the two ways a model can be wrong.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`fitting_lib.py` is complete -- it is the machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

import fitting_lib as f  # noqa: F401  (you will need it)


def test_01_training_error_falls_with_capacity_and_test_error_does_not():
    pytest.skip(
        "Assert f.capacity_sweep([1, 2, 3, 4, 6, 8, 10, 14, 18, 24]) equals "
        "the ten rows in expected-output/measured-values.txt, from (1, "
        "11.3217, 9.8274, -1.4942) to (24, 1.0321, 226667.4689, "
        "226666.4368). Assert f.best_degree is 4 and that the test error at "
        "degree 24 is more than 40000 times the test error at degree 4."
    )


def test_01b_training_error_falls_until_the_numerics_give_out():
    pytest.skip(
        "Take the training column of that sweep. Assert it is monotonically "
        "decreasing through degree 14 but NOT over the whole range, and that "
        "the wobble after degree 14 is 0.0636. That wobble is numerical, not "
        "statistical: 25 training rows, and degree 24 supplies exactly 25 "
        "features. Say so in a comment."
    )


def test_01c_the_generalisation_gap_is_the_diagnostic():
    pytest.skip(
        "Take the gap column. Assert the gap is NEGATIVE at degrees 1 and 2 "
        "-- test error below training error, because a model too rigid to "
        "chase noise has none to be flattered by. Assert it is between 0 and "
        "3 at the best degree, and above 200000 at degree 24. The gap tells "
        "you which failure you have without ever seeing the true function."
    )


def test_02_a_penalty_rescues_the_same_model_class():
    pytest.skip(
        "Assert f.regularisation_sweep([0.0, 1e-6, 1e-3, 0.1, 1.0, 10.0, "
        "100.0]) matches the captured rows, that f.best_alpha is 1.0, and "
        "that the ratio of the unpenalised test error to the best one is "
        "39588. The degree never changed. Only how strongly the fit was "
        "discouraged from using it."
    )


def test_02b_the_penalty_trades_training_error_for_test_error():
    pytest.skip(
        "Assert the training column rises monotonically with the penalty -- "
        "always true, since the penalty can only make the training fit "
        "worse. Assert the test column is U-shaped too, with alpha 1.0 "
        "beating 10.0 beating 100.0. Then assert the best-regularised "
        "degree-24 model lands within 0.3 of the best unregularised "
        "degree-4 model from f.capacity_sweep([4])."
    )


def test_03_more_data_cures_overfitting_and_does_nothing_for_underfitting():
    pytest.skip(
        "Assert f.data_sweep([15, 25, 50, 100, 400, 2000]) matches the "
        "captured rows. Then assert the two things that matter: the "
        "degree-1 column spans only 0.6227 across a 133-fold increase in "
        "data and starts and ends within 0.3 of itself, while the degree-24 "
        "column falls by more than seven orders of magnitude."
    )


def test_03b_both_good_models_converge_to_the_irreducible_floor():
    pytest.skip(
        "Assert f.irreducible_variance() is 4.0. At n=2000, assert degree 4 "
        "is within 0.02 of that floor and degree 24 within 0.01 -- they "
        "arrive from opposite sides, one from below the floor's own noise "
        "and one from far above. Assert the degree-1 model is still more "
        "than twice the floor at n=2000, and will be at any n."
    )


def test_03c_the_overfit_column_peaks_at_the_interpolation_threshold():
    pytest.skip(
        "The degree-24 column is NOT monotone in n: it is worse at n=25 "
        "than at n=15. Assert that, and assert n=25 is its maximum. Then "
        "explain it: use sklearn.preprocessing.PolynomialFeatures(24) on a "
        "dummy array to assert it produces exactly 25 features, and assert "
        "the peak row's n equals that count. Features equal to rows is the "
        "worst-conditioned case there is."
    )


def test_04_underfitting_is_bias_and_overfitting_is_variance():
    pytest.skip(
        "Call f.bias_variance at degrees 1, 3 and 12. Assert bias squared "
        "is 4.2985, 0.0033 and 2803.5354 and variance is 0.7112, 0.8399 and "
        "452183.1336. Then assert the shape of the story: at degree 1 bias "
        "exceeds variance sixfold, at degree 3 the bias is below 0.01 "
        "because the true function IS a cubic, and at degree 12 variance "
        "exceeds bias a hundredfold."
    )


def test_04b_the_decomposition_predicts_the_error_that_was_observed():
    pytest.skip(
        "For each degree in (1, 2, 3, 4, 6, 8, 12), assert the predicted "
        "total agrees with the observed squared error to within 1.1 percent, "
        "and that the worst disagreement across all seven is exactly "
        "0.01003. Also assert the three parts sum to the total to within "
        "0.0002 -- not exactly, because each part is stored already rounded "
        "to four places."
    )


def test_04c_a_bigger_model_class_is_not_always_less_biased():
    pytest.skip(
        "Assert degree 2 has bias squared 4.3342 against degree 1's 4.2985 "
        "-- MORE bias from a strictly larger model class. Assert it also "
        "carries roughly double the variance, and that its predicted total "
        "is therefore worse on both counts. The true function is odd, so a "
        "quadratic term can buy nothing and still costs. Capacity is not a "
        "single dial."
    )


def test_05_training_longer_makes_training_error_better_and_the_model_worse():
    pytest.skip(
        "Call f.training_history(). Assert both histories have 600 entries, "
        "that the training history is monotonically decreasing over all 600 "
        "epochs, and that it runs 7.3906 -> 2.4744. Then assert the test "
        "error bottoms at index 13 (epoch 14) with 5.4555 and is 5.8978 at "
        "epoch 600. Nothing about the model or the data changed; only how "
        "long the fit ran."
    )


def test_05b_the_generalisation_gap_grows_while_training_error_falls():
    pytest.skip(
        "Assert the gap between test and training error is 0.6771 at epoch "
        "1 and 3.4234 at epoch 600, a factor of more than five. Training "
        "time is a capacity knob, and the gap is what it is spending."
    )


def test_05c_the_test_curve_is_not_a_clean_u_which_is_why_patience_exists():
    pytest.skip(
        "After the best epoch, assert the test error rises to 7.1435 and "
        "then partly recovers to 5.8978 -- without ever again beating the "
        "5.4555 it reached at epoch 14, so assert min(after) is still above "
        "it and that 599 of the 600 epochs are worse than the best. Then "
        "assert every patience in (5, 10, 20, 50) recovers epoch 14 exactly, "
        "and that f.first_increase does too. Note in a comment that this is "
        "luck on this run rather than a property of the rule -- a curve that "
        "wanders like this one can defeat a naive stop-on-first-rise."
    )
