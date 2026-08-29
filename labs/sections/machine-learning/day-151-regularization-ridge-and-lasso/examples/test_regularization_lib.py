"""Machinery checks: the helpers behave, before any claim is made.

These four tests are solved in both `starter/` and `examples/`. They exist
so that a broken helper reports itself as a broken helper rather than as a
surprising scientific result.
"""

import numpy as np

import regularization_lib as r


def test_the_diabetes_split_is_reproducible_and_shaped_right():
    a = r.load_train_test()
    b = r.load_train_test()
    X_train_a, X_test_a, y_train_a, y_test_a = a
    X_train_b, _X_test_b, _y_train_b, _y_test_b = b
    assert X_train_a.shape == (331, 10)
    assert X_test_a.shape == (111, 10)
    assert y_train_a.shape == (331,)
    assert y_test_a.shape == (111,)
    # same seed, same split -- every downstream measurement depends on this
    assert np.array_equal(X_train_a, X_train_b)


def test_the_near_duplicate_columns_really_are_near_duplicate():
    X, y, correlation = r.near_duplicate_dataset()
    assert X.shape == (300, 3)
    assert y.shape == (300,)
    assert correlation > 0.999
    # the third column is not part of the near-duplicate pair
    assert abs(float(np.corrcoef(X[:, 0], X[:, 2])[0, 1])) < 0.3


def test_the_synthetic_sparse_dataset_really_has_five_informative_features():
    from sklearn.datasets import make_regression

    X, y, coef = make_regression(
        n_samples=200, n_features=20, n_informative=5, noise=1.0, coef=True, random_state=0
    )
    assert X.shape == (200, 20)
    assert int(np.sum(coef != 0)) == 5


def test_ridge_solves_directly_and_lasso_iterates():
    info = r.ridge_has_no_iteration_count()
    assert info["ridge_has_n_iter"] is False
    assert info["lasso_has_n_iter"] is True
    counts = r.lasso_iteration_counts([0.001, 1.0])
    # every count is a positive number of iterations, and none of them
    # hit the ceiling -- so no ConvergenceWarning was silently swallowed
    for alpha, n_iter in counts.items():
        assert 0 < n_iter < 50000, f"alpha={alpha} iterated {n_iter} times"
