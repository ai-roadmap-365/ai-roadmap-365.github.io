"""Overfitting and underfitting, decomposed and measured.

The two failures are usually described as a picture: a wiggly line through
every point, a straight line through none. That picture is true and it does
not tell you which one you have, because on your own data you cannot see
the true function.

What you can see is a decomposition. Every squared error splits into three
parts -- bias, variance and irreducible noise -- and the two failures are
one part each:

* **underfitting is bias**: the model class cannot represent the truth, so
  it is wrong in the same direction no matter what data you give it;
* **overfitting is variance**: the model class can represent the truth and
  much else besides, so it chases the noise and lands somewhere different
  for every training set;
* **noise is neither**, and it is the floor nothing can go below.

This module measures all three directly by fitting many models to many
independent training sets, and checks the decomposition against the error
that was actually observed. Everything is deterministic given a seed, and
everything runs on the CPU in seconds.
"""

from __future__ import annotations

import numpy as np

from sklearn.linear_model import LinearRegression, Ridge, SGDRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

#: The function the data is actually generated from. A cubic, so a
#: degree-3 model can represent it exactly and a straight line cannot.
NOISE_SD = 2.0


def true_function(x):
    """The relationship the data really has: a cubic, and nothing else."""
    return 0.5 * x**3 - 2.0 * x + 1.0


def irreducible_variance() -> float:
    """The floor. No model of any capacity can score below this."""
    return NOISE_SD**2


def make_data(n: int, seed: int, noise_sd: float = NOISE_SD):
    """n points from the true cubic, plus independent Gaussian noise."""
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-3.0, 3.0, n))
    y = true_function(x) + rng.normal(0.0, noise_sd, n)
    return x.reshape(-1, 1), y


def polynomial_model(degree: int, alpha: float = 0.0):
    """A polynomial fit of the given degree, optionally ridge-regularised.

    The `StandardScaler` between the features and the estimator is not
    decoration. Raw polynomial features up to degree 24 span many orders
    of magnitude and the normal equations become numerically hopeless;
    without scaling the *training* error starts rising with degree, which
    is a conditioning artefact masquerading as a result.
    """
    estimator = LinearRegression() if alpha == 0.0 else Ridge(alpha=alpha)
    return make_pipeline(PolynomialFeatures(degree), StandardScaler(), estimator)


def mse(model, X, y) -> float:
    """Mean squared error of a fitted model on the given rows."""
    return float(np.mean((model.predict(X) - y) ** 2))


# --------------------------------------------------------------------------
# 1. The capacity sweep
# --------------------------------------------------------------------------


def capacity_sweep(degrees, n_train: int = 25, train_seed: int = 145, test_seed: int = 246):
    """Train and test error at each polynomial degree.

    Rows are ``(degree, train_mse, test_mse, gap)``. Training error falls
    with capacity; test error does not, and where it turns is the whole
    subject.
    """
    X_train, y_train = make_data(n_train, train_seed)
    X_test, y_test = make_data(2000, test_seed)
    rows = []
    for degree in degrees:
        model = polynomial_model(degree).fit(X_train, y_train)
        train = mse(model, X_train, y_train)
        test = mse(model, X_test, y_test)
        rows.append((degree, round(train, 4), round(test, 4), round(test - train, 4)))
    return rows


def best_degree(rows) -> int:
    """The degree with the lowest test error in a capacity sweep."""
    return min(rows, key=lambda row: row[2])[0]


# --------------------------------------------------------------------------
# 2. Regularisation
# --------------------------------------------------------------------------


def regularisation_sweep(alphas, degree: int = 24, n_train: int = 25):
    """Train and test error at each ridge penalty, holding capacity fixed.

    The model class does not change here. Only how much the fit is
    discouraged from using it does -- which is the point: overfitting is
    not a property of the model class alone.
    """
    X_train, y_train = make_data(n_train, 145)
    X_test, y_test = make_data(2000, 246)
    rows = []
    for alpha in alphas:
        model = polynomial_model(degree, alpha=alpha).fit(X_train, y_train)
        rows.append((alpha, round(mse(model, X_train, y_train), 4), round(mse(model, X_test, y_test), 4)))
    return rows


def best_alpha(rows) -> float:
    """The penalty with the lowest test error."""
    return min(rows, key=lambda row: row[2])[0]


# --------------------------------------------------------------------------
# 3. What more data fixes, and what it does not
# --------------------------------------------------------------------------


def data_sweep(sizes, degrees=(1, 4, 24), test_seed: int = 246):
    """Test error against training-set size, at three capacities.

    Rows are ``(n, {degree: test_mse})``. The three columns behave
    completely differently, and the difference is the practical content of
    the whole lesson.
    """
    X_test, y_test = make_data(2000, test_seed)
    rows = []
    for n in sizes:
        X_train, y_train = make_data(n, 900 + n)
        scores = {}
        for degree in degrees:
            model = polynomial_model(degree).fit(X_train, y_train)
            scores[degree] = round(mse(model, X_test, y_test), 4)
        rows.append((n, scores))
    return rows


# --------------------------------------------------------------------------
# 4. The decomposition itself
# --------------------------------------------------------------------------


def bias_variance(degree: int, n_train: int = 25, datasets: int = 200, grid: int = 200):
    """Measure bias squared, variance and noise for one model class.

    Fit ``datasets`` models, each to its own independent training set, and
    predict the same fixed grid of query points with all of them. Then:

    * **bias squared** is how far the *average* prediction sits from the
      truth -- an error the model class makes every time;
    * **variance** is how much the predictions scatter around their own
      average -- an error that changes with the training set;
    * **noise** is the irreducible term, known here because we generated it.

    Returns a dict with all three, their sum, and the squared error
    actually observed against freshly noisy targets. Those last two should
    agree, and checking that they do is what makes this a measurement
    rather than a recitation.
    """
    query = np.linspace(-3.0, 3.0, grid).reshape(-1, 1)
    truth = true_function(query.ravel())

    predictions = np.empty((datasets, grid))
    for i in range(datasets):
        X_train, y_train = make_data(n_train, 10_000 + i)
        model = polynomial_model(degree).fit(X_train, y_train)
        predictions[i] = model.predict(query)

    mean_prediction = predictions.mean(axis=0)
    bias_squared = float(np.mean((mean_prediction - truth) ** 2))
    variance = float(np.mean(predictions.var(axis=0)))
    noise = irreducible_variance()

    observed_rng = np.random.default_rng(7)
    noisy_targets = truth + observed_rng.normal(0.0, NOISE_SD, predictions.shape)
    observed = float(np.mean((predictions - noisy_targets) ** 2))

    return {
        "bias_squared": round(bias_squared, 4),
        "variance": round(variance, 4),
        "noise": round(noise, 4),
        "predicted_total": round(bias_squared + variance + noise, 4),
        "observed": round(observed, 4),
    }


def decomposition_table(degrees, n_train: int = 25, datasets: int = 200):
    """The decomposition at several capacities, as one table."""
    return [(degree, bias_variance(degree, n_train, datasets)) for degree in degrees]


# --------------------------------------------------------------------------
# 5. Early stopping
# --------------------------------------------------------------------------


def training_history(epochs: int = 600, degree: int = 14, n_train: int = 25, seed: int = 0):
    """Train and test error after every epoch of gradient descent.

    Capacity is fixed and the data is fixed. The only thing that changes is
    how long the fit has been allowed to run -- which turns out to be a
    capacity knob of its own.
    """
    X_train, y_train = make_data(n_train, 145)
    X_test, y_test = make_data(2000, 246)

    features = PolynomialFeatures(degree)
    scaler = StandardScaler()
    P_train = scaler.fit_transform(features.fit_transform(X_train))
    P_test = scaler.transform(features.transform(X_test))

    model = SGDRegressor(
        learning_rate="constant", eta0=0.003, penalty=None, random_state=seed
    )
    train_history, test_history = [], []
    for _epoch in range(epochs):
        model.partial_fit(P_train, y_train)
        train_history.append(float(np.mean((model.predict(P_train) - y_train) ** 2)))
        test_history.append(float(np.mean((model.predict(P_test) - y_test) ** 2)))
    return train_history, test_history


def is_monotonically_decreasing(values, tolerance: float = 1e-9) -> bool:
    """Whether a sequence never increases, within a numerical tolerance."""
    return all(a >= b - tolerance for a, b in zip(values, values[1:]))


def first_increase(values) -> int:
    """The index of the first value larger than the one before it."""
    for i, (a, b) in enumerate(zip(values, values[1:]), start=1):
        if b > a:
            return i
    return len(values)


def stop_with_patience(values, patience: int) -> int:
    """Index of the epoch a patience-based early stop would have chosen.

    Stops once ``patience`` consecutive epochs have failed to improve on
    the best seen so far, and returns the best epoch rather than the epoch
    it stopped at -- which is what a real implementation restores.
    """
    best_index, best_value, waited = 0, values[0], 0
    for i, value in enumerate(values[1:], start=1):
        if value < best_value:
            best_index, best_value, waited = i, value, 0
        else:
            waited += 1
            if waited >= patience:
                break
    return best_index
