"""Nine exercises in what an accuracy number is not telling you.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real
code. `ml_lib.py` is complete -- it is the machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

import ml_lib as m  # noqa: F401  (you will need it)


def test_01_one_nn_scores_a_perfect_1_000_having_learned_nothing():
    pytest.skip(
        "Build m.pure_noise_dataset(200, seed=141) for training and "
        "m.pure_noise_dataset(1000, seed=242) for test. Fit "
        "m.HandwrittenNearestNeighbour on the training set. Assert the "
        "training accuracy is exactly 1.0 and the test accuracy is 0.518, "
        "and that the test accuracy is within 0.06 of chance (0.5). Then "
        "assert m.one_nn() -- scikit-learn's KNeighborsClassifier(1) -- "
        "reproduces both numbers exactly. Print both."
    )


def test_01b_the_only_way_a_1_nn_misses_a_training_row_is_a_duplicate():
    pytest.skip(
        "Load iris with sklearn.datasets.load_iris(return_X_y=True). "
        "Assert X.shape == (150, 4) and that the number of unique feature "
        "rows is 149 -- iris contains exactly one duplicated row. Assert a "
        "hand-written 1-NN scores 1.0 on the real labels (the duplicate "
        "pair shares a class), then permute the labels with "
        "np.random.default_rng(141) and assert the same model now scores "
        "below 1.0. That is the single exception to '1.000 by construction'."
    )


def test_02_a_three_line_rule_scores_1_000_and_every_model_scores_less():
    pytest.skip(
        "Train on m.rule_dataset(300, seed=11), test on "
        "m.rule_dataset(2000, seed=12). Assert m.exact_rule scores exactly "
        "1.0 on the test set. Assert m.shallow_tree(3) scores 0.8855 and "
        "is strictly less than the rule. Then score m.shallow_tree(8), "
        "m.deep_tree() and m.smooth_knn(15) too, assert the best of the "
        "four is 0.9675, and assert every one of them loses to the rule."
    )


def test_03_train_accuracy_exceeds_test_accuracy_and_the_gap_is_the_story():
    pytest.skip(
        "Split iris 100/50 with np.random.default_rng(141).permutation. "
        "Fit m.deep_tree(); assert train accuracy 1.0, test accuracy 0.96, "
        "gap 0.04. Then do the same on m.noisy_rule_dataset(300, seed=21, "
        "noise_rate=0.2) against m.noisy_rule_dataset(2000, seed=22, "
        "noise_rate=0.2): assert train 1.0, test 0.6535, gap 0.3465. "
        "Assert the two training scores are identical and the second gap "
        "is more than eight times the first. Report both gaps. Finally "
        "fit m.linear_classifier() on the SAME noisy training set and "
        "assert it scores 0.78 in training (worse than the tree) and "
        "0.7655 on the test set (better than the tree) -- the better "
        "training score belongs to the worse model."
    )


def test_04_accuracy_collapses_when_the_input_region_moves():
    pytest.skip(
        "Train m.deep_tree() on m.rule_dataset(400, seed=31). Score it on "
        "m.rule_dataset(2000, seed=32) -- assert 0.948 -- and on "
        "m.rule_dataset(2000, seed=33, offset=3.0), the identical problem "
        "translated by 3.0 -- assert 0.4895, which is below chance. Assert "
        "the drop exceeds 0.4, and that m.exact_rule still scores 1.0 on "
        "the shifted region. Report both accuracies."
    )


def test_05_a_model_interpolates_beautifully_and_extrapolates_not_at_all():
    pytest.skip(
        "Fit m.knn_regressor(5) on m.quadratic_curve(300, 0.0, 10.0, "
        "seed=41). Assert its mean absolute error is 0.180 on "
        "m.quadratic_curve(200, 0.0, 10.0, seed=42) and 139.704 on "
        "m.quadratic_curve(200, 10.0, 20.0, seed=43), both rounded to "
        "three places, and that the outside error is more than 700 times "
        "the inside one. Assert its largest prediction outside the range "
        "does not exceed the largest target it ever saw. Then check "
        "m.linear_regressor(): 6.007 inside, 101.643 outside."
    )


def test_06_a_good_looking_accuracy_that_loses_to_predicting_the_majority():
    pytest.skip(
        "Use m.imbalanced_noise_dataset(1000, seed=51) and (1000, "
        "seed=52). Assert m.majority_baseline() scores exactly 0.9 and "
        "that exactly 90 percent of the test labels are class 0. Assert "
        "m.one_nn() scores 0.821 and m.deep_tree() scores 0.817, and that "
        "BOTH are below the baseline. Then repeat the comparison on the "
        "iris split from exercise 3: baseline 0.26, 1-NN 0.98. Report all "
        "five numbers."
    )


def test_07_no_model_beats_the_label_noise_ceiling():
    pytest.skip(
        "With noise_rate=0.25, train on m.noisy_rule_dataset(2000, "
        "seed=61) and test on m.noisy_rule_dataset(4000, seed=62). The "
        "ceiling is 1 - noise_rate = 0.75. Score m.linear_classifier() "
        "(0.73725), m.smooth_knn(15) (0.72675), m.shallow_tree(3) "
        "(0.68825) and m.deep_tree() (0.60875), and assert every one is "
        "at or below the ceiling. Assert the best is within 0.02 of it. "
        "Finally assert the ceiling is exact, not estimated: compare "
        "against m.rule_dataset(4000, seed=62) and confirm exactly 1000 "
        "of the 4000 test labels were flipped."
    )


def test_08_more_data_fixes_variance_and_does_nothing_for_label_noise():
    pytest.skip(
        "Variance-limited: test on m.checkerboard_dataset(4000, seed=71); "
        "train m.deep_tree() on m.checkerboard_dataset(50, seed=120) "
        "(assert 0.5995) and on m.checkerboard_dataset(5000, seed=5070) "
        "(assert 0.99725). Noise-limited: test on "
        "m.noisy_rule_dataset(4000, seed=81, noise_rate=0.30); train "
        "m.linear_classifier() on (200, seed=280) (assert 0.6655) and on "
        "(5000, seed=5080) (assert 0.68675). Assert the first gain exceeds "
        "0.30, the second is below 0.05, and the small-sample "
        "noise-limited model already sits within 0.05 of its 0.70 ceiling."
    )


def test_09_should_use_ml_gives_the_verdict_the_case_deserves():
    pytest.skip(
        "Build a table of at least six cases with m.problem(...), one for "
        "each verdict m.should_use_ml can return plus a case where a rule "
        "exists and nothing else does. Justify each in a comment. Assert "
        "the verdicts. Then assert that a problem missing one of the four "
        "keys raises KeyError naming the missing key -- a missing question "
        "is an error, not a default."
    )
