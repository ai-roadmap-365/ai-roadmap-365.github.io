"""Machinery checks: the helpers behave, before any claim is made.

These four tests are solved in both `starter/` and `examples/`. They exist
so that a broken helper reports itself as a broken helper rather than as a
surprising scientific result.
"""

import numpy as np
import pytest

import classification_lib as c


def test_the_standard_error_formula_behaves_as_it_should():
    assert c.proportion_standard_error(0.5, 100) > c.proportion_standard_error(0.85, 100)
    assert c.proportion_standard_error(0.5, 100) > c.proportion_standard_error(0.5, 400)
    assert c.proportion_standard_error(1.0, 100) == 0.0


def test_candidate_configs_really_are_thirty_six_distinct_pipelines():
    configs = c.candidate_configs()
    assert len(configs) == 36
    seen = set()
    for family, param, make in configs:
        pipe = make()
        assert hasattr(pipe, "fit") and hasattr(pipe, "predict")
        seen.add((family, param))
    # No two configs share a (family, hyperparameter) pair.
    assert len(seen) == 36


def test_the_gated_test_set_counts_and_refuses():
    class AlwaysBenign:
        def score(self, X, y):
            return float(np.mean(np.asarray(y) == 1))

    y = np.array([0, 1, 1, 1])
    gate = c.GatedTestSet(np.zeros((4, 2)), y)
    assert gate.evaluate(AlwaysBenign()) == 0.75
    with pytest.raises(c.TestSetTouchedTwice):
        gate.evaluate(AlwaysBenign())
    # A fresh gate is a fresh budget; the class holds no global state.
    assert c.GatedTestSet(np.zeros((4, 2)), y).evaluate(AlwaysBenign()) == 0.75


def test_the_chosen_dataset_loads_offline_and_matches_its_shape():
    X, y, names = c.load_chosen_dataset()
    assert X.shape == (569, 30)
    assert y.shape == (569,)
    assert names == ["malignant", "benign"]
    assert set(y.tolist()) == {0, 1}
