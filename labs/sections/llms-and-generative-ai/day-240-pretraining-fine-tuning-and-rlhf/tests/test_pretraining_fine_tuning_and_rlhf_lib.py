import pytest
import torch
from examples.pretraining_fine_tuning_and_rlhf_lib import (
    compute_bradley_terry_probability,
    compute_dpo_loss
)

def test_bradley_terry_probabilities():
    p_equal = compute_bradley_terry_probability(1.0, 1.0)
    p_higher = compute_bradley_terry_probability(2.4, -1.2)
    p_lower = compute_bradley_terry_probability(-1.0, 2.0)

    assert p_equal == pytest.approx(0.5, rel=1e-3)
    assert p_higher > 0.95
    assert p_lower < 0.10

def test_dpo_loss_mechanics():
    # Setup batch where policy strongly prefers chosen over reference
    pol_chosen = torch.tensor([-10.0])
    pol_rejected = torch.tensor([-20.0])
    ref_chosen = torch.tensor([-10.0])
    ref_rejected = torch.tensor([-15.0])

    loss, margin = compute_dpo_loss(pol_chosen, pol_rejected, ref_chosen, ref_rejected, beta=0.1)
    
    assert loss.item() > 0.0
    assert margin.item() > 0.0

def test_dpo_loss_symmetry_when_identical():
    # If policy matches reference, logits = 0 -> loss = -log(sigmoid(0)) = log(2) ≈ 0.6931
    logps = torch.tensor([-10.0])
    loss, margin = compute_dpo_loss(logps, logps, logps, logps, beta=0.1)
    assert loss.item() == pytest.approx(0.6931, rel=1e-3)
    assert margin.item() == pytest.approx(0.0, abs=1e-5)
