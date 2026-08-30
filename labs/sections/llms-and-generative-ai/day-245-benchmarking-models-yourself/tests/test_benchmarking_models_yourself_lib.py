import pytest
from examples.benchmarking_models_yourself_lib import (
    ELOEvaluator,
    compute_pass_at_k
)

def test_elo_update_symmetry():
    evaluator = ELOEvaluator(initial_elo=1000.0, k_factor=32.0)
    # Match where Model A wins (score 1.0)
    r_a, r_b = evaluator.update_match("ModelA", "ModelB", 1.0)
    assert r_a == 1016.0
    assert r_b == 984.0
    assert (r_a + r_b) == 2000.0 # Zero-sum conservation

def test_pass_at_k_exact_values():
    # n = 10, c = 4, k = 1 -> 4/10 = 0.40
    assert compute_pass_at_k(10, 4, 1) == 0.40

    # n = 10, c = 4, k = 3 -> 1 - (6/10 * 5/9 * 4/8) = 1 - 0.16666 = 0.8333
    assert compute_pass_at_k(10, 4, 3) == pytest.approx(0.8333, rel=1e-3)

def test_pass_at_k_edge_case():
    # n = 5, c = 5, k = 1 -> 1.0
    assert compute_pass_at_k(5, 5, 1) == 1.0
    # n = 5, c = 0, k = 2 -> 0.0
    assert compute_pass_at_k(5, 0, 2) == 0.0
