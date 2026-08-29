"""The reference solutions: one classification project, run properly, once.

Every number here was captured from a real run of this file on the
authoring machine. If a number changes, the claim in the lesson is wrong
and one of the two must be fixed.
"""

import numpy as np
import pytest

import classification_lib as c


@pytest.fixture(scope="module")
def dataset():
    return c.load_chosen_dataset()


@pytest.fixture(scope="module")
def split(dataset):
    X, y, _names = dataset
    return c.split_once(X, y, seed=0)


# --- 1. Choosing the dataset, by measuring --------------------------------


def test_01_the_dataset_choice_is_measured_not_assumed():
    rows = {row[0]: row for row in c.candidate_summaries()}
    assert rows["iris"] == ("iris", 150, 4, 3, 0.3333, 30)
    assert rows["wine"] == ("wine", 178, 13, 3, 0.3889, 36)
    assert rows["breast_cancer"] == ("breast_cancer", 569, 30, 2, 0.6316, 114)
    # iris and wine both have fewer than 40 test rows -- one wrong answer
    # moves accuracy by more than 2.5 points, too coarse for an honest interval.
    assert rows["iris"][5] < 40
    assert rows["wine"][5] < 40
    assert rows["breast_cancer"][5] > 100


def test_01b_the_chosen_dataset_gives_headroom_for_an_interval(dataset):
    X, y, names = dataset
    assert X.shape == (569, 30)
    assert names == ["malignant", "benign"]
    # The class split is real imbalance, not degenerate: neither class is rare.
    assert 0.3 < float(np.mean(y == 1)) < 0.7


# --- 2. The frame and the baseline -----------------------------------------


def test_02_the_majority_baseline_before_any_model(split):
    x_train, x_test, y_train, y_test = split
    baseline = c.majority_baseline(x_train, y_train, x_test, y_test)
    assert round(baseline, 4) == 0.6316
    # Any model worth building has to clear this, or it is worth nothing.


# --- 3. The split ------------------------------------------------------------


def test_03_the_split_is_stratified_and_holds_the_test_rows_back(dataset):
    X, y, _names = dataset
    x_train, x_test, y_train, y_test = c.split_once(X, y, seed=0)
    assert x_train.shape == (455, 30)
    assert x_test.shape == (114, 30)
    # Stratified: the positive rate in each half matches the population's.
    population_rate = float(np.mean(y == 1))
    assert abs(float(np.mean(y_train == 1)) - population_rate) < 0.01
    assert abs(float(np.mean(y_test == 1)) - population_rate) < 0.01


# --- 4. The sweep --------------------------------------------------------


def test_04_the_sweep_counts_thirty_six_candidate_pipelines():
    assert c.candidate_count() == 36
    families = [family for family, _param, _make in c.candidate_configs()]
    assert families.count("knn") == 15
    assert families.count("logreg") == 11
    assert families.count("tree") == 10


# --- 5. Cross-validate, then select --------------------------------------


def test_05_cross_validation_selects_the_winner_on_train_rows_only(split):
    x_train, _x_test, y_train, _y_test = split
    family, param, cv_mean, fitted = c.select_best(x_train, y_train, seed=0)
    assert (family, param) == ("logreg", 1)
    assert round(cv_mean, 4) == 0.978
    assert hasattr(fitted, "predict")
    # The winner was never fitted on -- let alone scored against -- test rows.


# --- 6. The gate -----------------------------------------------------------


def test_06_the_gate_permits_exactly_one_test_evaluation(split):
    x_train, x_test, y_train, y_test = split
    _family, _param, _cv, fitted = c.select_best(x_train, y_train, seed=0)
    gate = c.GatedTestSet(x_test, y_test)
    assert gate.evaluations == 0
    first = gate.evaluate(fitted)
    assert round(first, 4) == 0.9825
    assert gate.evaluations == 1
    with pytest.raises(c.TestSetTouchedTwice) as excinfo:
        gate.evaluate(fitted)
    assert "validation score" in str(excinfo.value)
    assert gate.evaluations == 1


# --- 7. The predicted optimism --------------------------------------------


def test_07_the_predicted_optimism_from_day_144s_formula(split):
    x_train, _x_test, y_train, _y_test = split
    _family, _param, cv_mean, _fitted = c.select_best(x_train, y_train, seed=0)
    predicted = c.predicted_selection_optimism(cv_mean, len(y_train), c.candidate_count())
    assert round(predicted, 4) == 0.0326
    # The measured drop at this seed (-0.0045) is far smaller than the
    # prediction: real, correlated candidates do not behave like coin flips.


def test_07b_predicted_vs_measured_over_twenty_seeds(dataset):
    X, y, _names = dataset
    rows = c.selection_optimism_over_seeds(X, y, seeds=range(20))
    assert len(rows) == 20
    drops = np.array([r[3] for r in rows])
    predicted = np.array([r[4] for r in rows])
    assert round(float(drops.mean()), 4) == -0.0001
    assert round(float(drops.std()), 4) == 0.0149
    assert round(float(predicted.mean()), 4) == 0.033
    assert round(float((drops > 0).mean()), 4) == 0.5
    # The formula, built for independent zero-skill candidates, overestimates
    # the real optimism here by more than 300-fold on average -- these 36
    # candidates are correlated and genuinely skilled, not coin flips.
    assert float(predicted.mean()) > float(drops.mean()) + 0.02


# --- 8. Error analysis -----------------------------------------------------


def test_08_error_analysis_the_confusion_matrix(split):
    x_train, x_test, y_train, y_test = split
    _family, _param, _cv, fitted = c.select_best(x_train, y_train, seed=0)
    preds = fitted.predict(x_test)
    matrix, false_negatives, false_positives = c.confusion_and_errors(y_test, preds, ["malignant", "benign"])
    assert matrix.tolist() == [[40, 2], [0, 72]]
    assert false_negatives == 2
    assert false_positives == 0
    # Every error this model makes is the costlier kind: a missed malignancy.


# --- 9. The verdict ----------------------------------------------------------


def test_09_the_verdict_has_an_interval(split):
    x_train, x_test, y_train, y_test = split
    _family, _param, _cv, fitted = c.select_best(x_train, y_train, seed=0)
    test_acc = float(fitted.score(x_test, y_test))
    se, half_width, lower, upper = c.verdict_interval(test_acc, len(y_test))
    assert se == 0.0123
    assert half_width == 0.0241
    assert (lower, upper) == (0.9584, 1.0066)


def test_09b_the_improvement_is_distinguishable_from_baseline(split):
    x_train, x_test, y_train, y_test = split
    baseline = c.majority_baseline(x_train, y_train, x_test, y_test)
    _family, _param, _cv, fitted = c.select_best(x_train, y_train, seed=0)
    test_acc = float(fitted.score(x_test, y_test))
    assert c.distinguishable_from_baseline(test_acc, baseline, len(y_test)) is True
    # Thirty-five points of improvement against a four-point interval: this
    # is not a "cannot distinguish" verdict, and the arithmetic says so.
    assert round(test_acc - baseline, 4) == 0.3509


# --- 10. The leaky version -------------------------------------------------


def test_10_the_leaky_version_selects_by_peeking_at_the_test_set(split):
    x_train, x_test, y_train, y_test = split
    _family, _param, _cv, fitted = c.select_best(x_train, y_train, seed=0)
    honest = round(float(fitted.score(x_test, y_test)), 4)
    leaky = c.leaky_selection_test_score(x_train, y_train, x_test, y_test)
    assert honest == 0.9825
    assert leaky == 0.9825
    assert leaky >= honest


def test_10b_the_leaky_gap_over_twenty_seeds(dataset):
    X, y, _names = dataset
    rows = c.leaky_vs_honest_over_seeds(X, y, seeds=range(20))
    assert len(rows) == 20
    gaps = np.array([r[3] for r in rows])
    assert round(float(gaps.mean()), 4) == 0.0096
    assert round(float(gaps.std()), 4) == 0.0103
    assert round(float(gaps.min()), 4) == 0.0
    assert round(float(gaps.max()), 4) == 0.0351
    # The leak never once helped the honest number and never hurt the leaky
    # one: every seed's gap is non-negative, exactly as the mechanism predicts.
    assert (gaps >= 0).all()
