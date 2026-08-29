"""Fourteen exercises: one classification project, run properly, once.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`classification_lib.py` is complete -- it is the machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

import classification_lib as c  # noqa: F401  (you will need it)


@pytest.fixture(scope="module")
def dataset():
    return c.load_chosen_dataset()


@pytest.fixture(scope="module")
def split(dataset):
    X, y, _names = dataset
    return c.split_once(X, y, seed=0)


def test_01_the_dataset_choice_is_measured_not_assumed():
    pytest.skip(
        "Call c.candidate_summaries() and index it by name. Assert the iris row "
        "equals ('iris', 150, 4, 3, 0.3333, 30), wine equals ('wine', 178, 13, 3, "
        "0.3889, 36), and breast_cancer equals ('breast_cancer', 569, 30, 2, "
        "0.6316, 114). Then assert both iris and wine have fewer than 40 test "
        "rows, at 20 percent, while breast_cancer has more than 100 -- the "
        "headroom the rest of this exercise needs."
    )


def test_01b_the_chosen_dataset_gives_headroom_for_an_interval(dataset):
    pytest.skip(
        "Unpack (X, y, names) from the dataset fixture. Assert X.shape == "
        "(569, 30) and names == ['malignant', 'benign']. Then assert the "
        "positive rate (label 1) is strictly between 0.3 and 0.7 -- neither "
        "class is rare, so nothing here needs the stratification machinery "
        "Day 144 built for a 5 percent minority."
    )


def test_02_the_majority_baseline_before_any_model(split):
    pytest.skip(
        "Unpack (x_train, x_test, y_train, y_test) from the split fixture. "
        "Call c.majority_baseline and assert it rounds to 0.6316. Every model "
        "in the rest of this exercise has to beat this number to be worth "
        "building at all -- Day 141's whole point restated as a gate."
    )


def test_03_the_split_is_stratified_and_holds_the_test_rows_back(dataset):
    pytest.skip(
        "Unpack (X, y, _names) from the dataset fixture and call "
        "c.split_once(X, y, seed=0). Assert x_train.shape == (455, 30) and "
        "x_test.shape == (114, 30). Then assert the positive rate in y_train "
        "and in y_test both sit within 0.01 of the population's positive "
        "rate -- the stratification Day 144 said should be your default."
    )


def test_04_the_sweep_counts_thirty_six_candidate_pipelines():
    pytest.skip(
        "Assert c.candidate_count() == 36. Then unpack the (family, param, "
        "make) triples from c.candidate_configs() and assert there are 15 "
        "'knn', 11 'logreg' and 10 'tree' entries. K is the number nobody "
        "remembers, Day 144 said -- so this exercise counts it before doing "
        "anything else with it."
    )


def test_05_cross_validation_selects_the_winner_on_train_rows_only(split):
    pytest.skip(
        "Unpack (x_train, _x_test, y_train, _y_test) from the split fixture "
        "and call c.select_best(x_train, y_train, seed=0). Assert the "
        "returned (family, param) equals ('logreg', 1) and the cv_mean "
        "rounds to 0.978. The winner was chosen on cross-validated train "
        "rows -- the test rows have not been touched yet."
    )


def test_06_the_gate_permits_exactly_one_test_evaluation(split):
    pytest.skip(
        "Fit the winner from c.select_best on the train rows, wrap "
        "(x_test, y_test) in c.GatedTestSet, and assert the first evaluation "
        "rounds to 0.9825 and the counter becomes 1. Then assert a second "
        "evaluation raises c.TestSetTouchedTwice mentioning 'validation "
        "score', and that the counter did NOT advance on the refused "
        "attempt -- Day 144's discipline, made mechanical again."
    )


def test_07_the_predicted_optimism_from_day_144s_formula(split):
    pytest.skip(
        "Select the winner, then call c.predicted_selection_optimism with "
        "its cv_mean, len(y_train) and c.candidate_count(). Assert the "
        "result rounds to 0.0326 -- the optimism Day 144's formula predicts "
        "for a sweep of 36 candidates, computable before you ever look at "
        "the test set."
    )


def test_07b_predicted_vs_measured_over_twenty_seeds(dataset):
    pytest.skip(
        "Unpack (X, y, _names) and call c.selection_optimism_over_seeds(X, "
        "y, seeds=range(20)). Assert 20 rows come back. Compute the mean and "
        "sd of the measured drops and assert they round to -0.0001 and "
        "0.0149; assert the mean of the predicted column rounds to 0.033; "
        "assert exactly half the drops were positive. Then assert the "
        "predicted mean exceeds the measured mean by more than 0.02 -- the "
        "formula assumed independent, zero-skill candidates, and these 36 "
        "are correlated and genuinely skilled, so it overestimates badly."
    )


def test_08_error_analysis_the_confusion_matrix(split):
    pytest.skip(
        "Select and fit the winner, predict on x_test, and call "
        "c.confusion_and_errors(y_test, preds, ['malignant', 'benign']). "
        "Assert the matrix equals [[40, 2], [0, 72]], false_negatives == 2 "
        "and false_positives == 0. Every mistake this model makes is a "
        "missed malignancy -- the costlier error in this domain -- and "
        "accuracy alone would have hidden that."
    )


def test_09_the_verdict_has_an_interval(split):
    pytest.skip(
        "Select the winner, fit it, score it on the test rows exactly once, "
        "and call c.verdict_interval(test_acc, len(y_test)). Assert se == "
        "0.0123, half_width == 0.0241, and the interval equals (0.9584, "
        "1.0066). A point estimate without this interval is not a verdict."
    )


def test_09b_the_improvement_is_distinguishable_from_baseline(split):
    pytest.skip(
        "Compute the baseline and the test accuracy as before. Assert "
        "c.distinguishable_from_baseline(test_acc, baseline, len(y_test)) "
        "is True, and that the improvement rounds to 0.3509. Thirty-five "
        "points of improvement against a four-point interval is not a "
        "'cannot distinguish' verdict, and the arithmetic is how you would "
        "know if it had been."
    )


def test_10_the_leaky_version_selects_by_peeking_at_the_test_set(split):
    pytest.skip(
        "Select and fit the honest winner and score it once on test. Then "
        "call c.leaky_selection_test_score(x_train, y_train, x_test, "
        "y_test), which fits every one of the 36 candidates and lets the "
        "test set itself pick the winner. Assert the honest score rounds to "
        "0.9825, the leaky score rounds to 0.9825, and leaky >= honest -- "
        "the leak can only ever look as good or better, never worse."
    )


def test_10b_the_leaky_gap_over_twenty_seeds(dataset):
    pytest.skip(
        "Call c.leaky_vs_honest_over_seeds(X, y, seeds=range(20)). Assert 20 "
        "rows, mean gap rounding to 0.0096, sd 0.0103, min 0.0 and max "
        "0.0351. Then assert every single gap is non-negative -- across 20 "
        "independent seeds, selecting by peeking at the test set never once "
        "did worse than selecting honestly, and often did strictly better. "
        "That is the mechanism, not luck."
    )
