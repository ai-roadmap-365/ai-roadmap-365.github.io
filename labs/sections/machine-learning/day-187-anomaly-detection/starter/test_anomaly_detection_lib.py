import pytest
import numpy as np
from examples.anomaly_detection_lib import c_factor, IsolationForestFromScratch

def test_c_factor_values():
    assert c_factor(1) == 0.0
    assert c_factor(2) == 1.0
    assert c_factor(256) > 5.0

def test_isolation_forest_scores_outliers_higher():
    np.random.seed(42)
    inliers = np.random.normal(0, 1, (200, 2))
    outliers = np.array([[10.0, 10.0], [-10.0, -10.0], [15.0, 0.0]])
    X = np.vstack([inliers, outliers])

    clf = IsolationForestFromScratch(n_estimators=50, max_samples=128, contamination=0.05).fit(X)
    scores = clf.decision_function(X)

    assert scores[-1] > np.median(scores[:200])
    assert scores[-2] > np.median(scores[:200])
    assert scores[-3] > np.median(scores[:200])
