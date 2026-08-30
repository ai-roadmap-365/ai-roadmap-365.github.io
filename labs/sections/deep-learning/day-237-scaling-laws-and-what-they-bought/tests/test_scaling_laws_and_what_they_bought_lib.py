import pytest
from examples.scaling_laws_and_what_they_bought_lib import (
    calculate_training_flops,
    compute_chinchilla_optimal
)

def test_training_flops_calculation():
    # 7B params on 140B tokens: 6 * 7e9 * 140e9 = 5.88e21 FLOPs
    flops = calculate_training_flops(7.0, 140.0)
    assert flops == pytest.approx(5.88e21, rel=1e-3)

def test_chinchilla_optimal_reconstruction():
    flops = 5.88e21
    alloc = compute_chinchilla_optimal(flops)
    assert alloc["optimal_params_billions"] == pytest.approx(7.0, rel=1e-2)
    assert alloc["optimal_tokens_billions"] == pytest.approx(140.0, rel=1e-2)
    assert alloc["token_to_param_ratio"] == 20.0

def test_predicted_loss_bounds():
    flops = 5.88e21
    alloc = compute_chinchilla_optimal(flops)
    # Loss should be greater than irreducible entropy E (1.69)
    assert alloc["predicted_loss"] > 1.69
    assert alloc["predicted_loss"] < 4.0
