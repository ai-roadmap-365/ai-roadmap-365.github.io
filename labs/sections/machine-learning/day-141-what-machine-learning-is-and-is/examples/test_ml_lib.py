"""Three checks on the machinery itself, so a failure elsewhere is a
failure of the claim under test and not of the helpers.

These three are already solved in `starter/` too: they are not exercises.
"""

import numpy as np

import ml_lib as m


def test_accuracy_counts_matches():
    assert m.accuracy([0, 1, 1, 0], [0, 1, 0, 0]) == 0.75
    assert m.accuracy([1, 1], [1, 1]) == 1.0
    assert m.accuracy([1, 1], [0, 0]) == 0.0


def test_exact_rule_is_exactly_correct_on_its_own_data():
    for seed in (1, 2, 3):
        X, y = m.rule_dataset(500, seed=seed)
        assert m.accuracy(y, m.exact_rule(X)) == 1.0


def test_flip_labels_flips_an_exact_count():
    _, y = m.rule_dataset(1000, seed=7)
    flipped = m.flip_labels(y, noise_rate=0.25, seed=7)
    assert int(np.sum(y != flipped)) == 250
    # Flipping is a relabelling, not a resampling: the feature matrix and
    # the array length are untouched.
    assert flipped.shape == y.shape
