import pytest
import numpy as np
from examples.recommender_systems_lib import MatrixFactorizationSGD

def test_recommender_prediction_shape_and_range():
    ratings = [
        (0, 0, 5.0), (0, 1, 4.0), (0, 2, 1.0),
        (1, 0, 4.5), (1, 1, 5.0), (1, 3, 2.0),
        (2, 2, 4.0), (2, 3, 5.0), (2, 0, 1.0)
    ]
    mf = MatrixFactorizationSGD(n_factors=2, lr=0.02, reg=0.05, n_epochs=20).fit(ratings)
    pred = mf.predict(0, 0)

    assert isinstance(pred, float)
    assert not np.isnan(pred)
    assert 0.0 <= pred <= 6.0

def test_recommender_error_reduction():
    ratings = [(u, i, 4.0) for u in range(5) for i in range(4)]
    mf = MatrixFactorizationSGD(n_factors=2, lr=0.05, reg=0.01, n_epochs=30).fit(ratings)
    preds = [mf.predict(u, i) for u, i, r in ratings]

    rmse = np.sqrt(np.mean([(r - p)**2 for (_, _, r), p in zip(ratings, preds)]))
    assert rmse < 0.5
