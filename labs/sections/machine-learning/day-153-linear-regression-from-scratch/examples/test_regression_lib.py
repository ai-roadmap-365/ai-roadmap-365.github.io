"""Machinery checks -- already solved, in both starter/ and examples/.

These confirm the library behaves as documented. They are not the
exercises; `test_regression_claims.py` is.
"""

import numpy as np

import regression_lib as r


def test_add_intercept_column_prepends_a_column_of_ones():
    X = np.arange(6.0).reshape(3, 2)
    A = r.add_intercept_column(X)
    assert A.shape == (3, 3)
    assert np.array_equal(A[:, 0], np.ones(3))
    assert np.array_equal(A[:, 1:], X)


def test_center_removes_the_mean_from_both_x_and_y():
    rng = np.random.default_rng(0)
    X = rng.normal(loc=5.0, scale=2.0, size=(50, 3))
    y = rng.normal(loc=-3.0, size=50)
    Xc, yc, X_mean, y_mean = r.center(X, y)
    assert np.allclose(Xc.mean(axis=0), 0.0, atol=1e-10)
    assert abs(float(yc.mean())) < 1e-10
    assert np.allclose(X_mean, X.mean(axis=0))
    assert y_mean == y.mean()


def test_make_dramatic_collinear_dataset_shape_and_true_coefficients():
    X, y, true_coef = r.make_dramatic_collinear_dataset(n=100, seed=0)
    assert X.shape == (100, 4)
    assert y.shape == (100,)
    assert np.array_equal(true_coef, np.array([1.0, 2.0, 3.0, 4.0]))
    # the fourth column is almost the first
    assert np.max(np.abs(X[:, 3] - X[:, 0])) < 1e-5


def test_normal_equations_and_lstsq_agree_on_a_well_conditioned_toy_problem():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(200, 4))
    true_coef = np.array([1.0, -2.0, 0.5, 3.0])
    y = X @ true_coef + rng.normal(scale=0.01, size=200)
    beta_ne = r.fit_normal_equations(X, y)
    beta_lstsq = r.fit_lstsq(X, y)
    assert np.max(np.abs(beta_ne - beta_lstsq)) < 1e-8
    assert np.max(np.abs(beta_ne - true_coef)) < 0.01


def test_ols_regressor_exposes_sklearn_style_learned_attributes():
    rng = np.random.default_rng(2)
    X = rng.normal(size=(60, 3))
    y = X @ np.array([1.0, 2.0, -1.0]) + 4.0
    model = r.OLSRegressor(method="normal").fit(X, y)
    assert hasattr(model, "coef_")
    assert hasattr(model, "intercept_")
    assert hasattr(model, "n_features_in_")
    assert model.n_features_in_ == 3
    # get_params/set_params come from BaseEstimator's __init__ introspection
    params = model.get_params()
    assert params["method"] == "normal"
    assert params["fit_intercept"] is True
