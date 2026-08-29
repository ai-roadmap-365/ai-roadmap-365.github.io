"""Machinery checks: the helpers behave, before any claim is made.

These four tests are solved in both `starter/` and `examples/`. They exist
so that a broken helper reports itself as a broken helper rather than as a
surprising scientific result.
"""

import numpy as np
import pytest

import splits_lib as s


def test_the_standard_error_formula_behaves_as_it_should():
    # Maximal at p = 0.5, and shrinking like one over root n.
    assert s.proportion_standard_error(0.5, 100) > s.proportion_standard_error(0.85, 100)
    assert s.proportion_standard_error(0.5, 100) > s.proportion_standard_error(0.5, 400)
    quartered = s.proportion_standard_error(0.5, 400) / s.proportion_standard_error(0.5, 100)
    assert round(quartered, 4) == 0.5
    # A certain outcome has no sampling error at all.
    assert s.proportion_standard_error(1.0, 100) == 0.0


def test_the_grouped_dataset_really_is_grouped():
    X, y, groups = s.grouped_dataset(n_people=10, rows_each=5, seed=1)
    assert X.shape == (50, 4) and y.shape == (50,) and groups.shape == (50,)
    assert len(set(groups.tolist())) == 10
    # Every row belonging to one person carries that person's single label.
    for person in range(10):
        member_labels = set(y[groups == person].tolist())
        assert len(member_labels) == 1


def test_the_regime_series_really_changes_its_rule():
    X, y = s.regime_series(length=600, n_regimes=3, seed=2)
    assert X.shape == (600, 4) and y.shape == (600,)
    # Each regime is internally consistent but the regimes disagree: a
    # linear model fitted on one block should do worse on another.
    from sklearn.linear_model import LogisticRegression

    first = LogisticRegression(max_iter=1000).fit(X[:200], y[:200])
    own = s.accuracy(y[:200], first.predict(X[:200]))
    other = s.accuracy(y[400:], first.predict(X[400:]))
    assert own > 0.9
    assert other < own - 0.2


def test_the_gated_test_set_counts_and_refuses():
    class AlwaysZero:
        def predict(self, X):
            return np.zeros(len(X), dtype=int)

    y = np.array([0, 0, 0, 1])
    gate = s.GatedTestSet(np.zeros((4, 2)), y)
    assert gate.evaluate(AlwaysZero()) == 0.75
    with pytest.raises(s.TestSetTouchedTwice):
        gate.evaluate(AlwaysZero())
    # A fresh gate is a fresh budget; the class holds no global state.
    assert s.GatedTestSet(np.zeros((4, 2)), y).evaluate(AlwaysZero()) == 0.75
