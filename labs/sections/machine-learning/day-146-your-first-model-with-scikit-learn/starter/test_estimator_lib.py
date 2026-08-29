"""Machinery checks: the helpers behave, before any claim is made.

These five tests are solved in both `starter/` and `examples/`. They exist
so that a broken helper reports itself as a broken helper rather than as a
surprising scientific result.
"""

import numpy as np

import estimator_lib as e


def test_the_datasets_have_the_shapes_they_claim():
    X, y = e.classification_dataset(n=150, n_features=4, n_classes=3, seed=42)
    assert X.shape == (150, 4) and y.shape == (150,)
    assert set(np.unique(y).tolist()) == {0, 1, 2}

    Xs, ys = e.skewed_dataset(n=60, seed=0)
    assert Xs.shape == (60, 3) and ys.shape == (60,)
    # A genuine majority class, by construction.
    values, counts = np.unique(ys, return_counts=True)
    assert counts.max() > len(ys) / 2


def test_majority_classifier_predicts_the_class_it_saw_most_often():
    X = np.zeros((6, 2))
    y = np.array([0, 0, 0, 1, 1, 2])
    clf = e.MajorityClassifier().fit(X, y)
    assert clf.majority_class_ == 0
    assert np.array_equal(clf.predict(X), np.zeros(6, dtype=int))
    assert clf.score(X, y) == 3 / 6


def test_majority_classifier_get_params_and_set_params_agree():
    clf = e.MajorityClassifier(strategy="most_frequent")
    assert clf.get_params() == {"strategy": "most_frequent"}
    clf.set_params(strategy="prior")
    assert clf.get_params() == {"strategy": "prior"}


def test_the_counting_scaler_counts_direct_fit_calls():
    e._CountingScaler.calls = 0
    X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    scaler = e._CountingScaler()
    scaler.fit(X)
    scaler.fit(X)
    assert e._CountingScaler.calls == 2


def test_estimator_census_finds_known_members_in_both_lists():
    census = e.estimator_census()
    assert census["total"] == census["has_fit"], "every discovered estimator implements fit"
    assert "KMeans" in census["both_transform_and_predict"]
    assert "Pipeline" in census["both_transform_and_predict"]
    assert "LogisticRegression" not in census["both_transform_and_predict"]
