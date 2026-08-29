"""
Tests for reference feature engineering implementation.
"""
import pytest
import numpy as np
import engineering_lib as fe


def test_cyclical_time_distance_continuity():
    # Hour 23.0 and Hour 0.0 (1 hour apart across midnight boundary)
    times = np.array([23.0, 0.0, 1.0, 12.0])
    sin_feat, cos_feat = fe.encode_cyclical_time(times, period=24.0)
    
    pt_23 = np.array([sin_feat[0], cos_feat[0]])
    pt_0 = np.array([sin_feat[1], cos_feat[1]])
    pt_1 = np.array([sin_feat[2], cos_feat[2]])
    pt_12 = np.array([sin_feat[3], cos_feat[3]])
    
    # Distance between 23:00 and 00:00 must equal distance between 00:00 and 01:00
    dist_23_0 = np.linalg.norm(pt_23 - pt_0)
    dist_0_1 = np.linalg.norm(pt_0 - pt_1)
    dist_0_12 = np.linalg.norm(pt_0 - pt_12)
    
    assert np.isclose(dist_23_0, dist_0_1, atol=1e-5)
    # Opposite times (00:00 vs 12:00) should be at maximum diameter distance 2.0
    assert np.isclose(dist_0_12, 2.0, atol=1e-5)


def test_polynomial_interactions_shape():
    # 3 features: original (3) + pairwise products 3*(3+1)/2 = 6 interactions -> total 9 columns
    X = np.ones((10, 3))
    X_poly = fe.compute_polynomial_interactions(X)
    assert X_poly.shape == (10, 9)


def test_group_aggregations_leak_free():
    groups_tr = np.array(["A", "A", "B", "B"])
    vals_tr = np.array([10.0, 20.0, 100.0, 200.0]) # Mean A = 15, Mean B = 150
    groups_te = np.array(["A", "B", "C"]) # C is unseen
    
    stats_te = fe.compute_group_aggregations(groups_tr, vals_tr, groups_te)
    
    assert np.isclose(stats_te[0, 0], 15.0)  # A mean
    assert np.isclose(stats_te[1, 0], 150.0) # B mean
    # C should fallback to global training mean: (10+20+100+200)/4 = 82.5
    assert np.isclose(stats_te[2, 0], 82.5)
