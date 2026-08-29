import pytest
import numpy as np
from examples.building_datasets_and_labeling_lib import compute_shannon_entropy, compute_cohen_kappa, MajorityVoteLabelModel

def test_entropy_and_cohen_kappa():
    # 50/50 probability has maximum entropy 1.0
    p_equal = np.array([[0.5, 0.5]])
    ent = compute_shannon_entropy(p_equal)
    assert np.isclose(ent[0], 1.0, atol=1e-3)

    # Identical ratings have kappa 1.0
    y1 = np.array([1, 0, 1, 1, 0])
    y2 = np.array([1, 0, 1, 1, 0])
    assert compute_cohen_kappa(y1, y2) == 1.0

def test_majority_vote_label_model():
    # 3 samples, 3 LFs with votes {-1, +1, 0 (abstain)}
    L = np.array([
        [1, 1, -1],  # Sum = +1 -> Output +1
        [-1, -1, 0], # Sum = -2 -> Output -1
        [0, 0, 0]    # All abstain -> Output 0
    ])
    model = MajorityVoteLabelModel()
    preds = model.fit_predict(L)
    assert np.array_equal(preds, [1, -1, 0])
