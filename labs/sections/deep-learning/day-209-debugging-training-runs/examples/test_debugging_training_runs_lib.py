import pytest
import torch
import torch.nn as nn
from examples.debugging_training_runs_lib import (
    compute_global_gradient_norm, custom_clip_grad_norm, single_batch_overfit_test
)

def test_compute_global_gradient_norm():
    model = nn.Sequential(nn.Linear(2, 2, bias=False))
    model[0].weight.grad = torch.tensor([[3.0, 4.0], [0.0, 0.0]])
    # Norm = sqrt(3^2 + 4^2) = 5.0
    norm = compute_global_gradient_norm(model)
    assert pytest.approx(norm, abs=1e-5) == 5.0

def test_custom_clip_grad_norm_matches_torch():
    torch.manual_seed(42)
    model1 = nn.Sequential(nn.Linear(10, 10), nn.ReLU(), nn.Linear(10, 2))
    model2 = nn.Sequential(nn.Linear(10, 10), nn.ReLU(), nn.Linear(10, 2))

    # Set identical weights
    model2.load_state_dict(model1.state_dict())

    x = torch.randn(16, 10)
    y = torch.randint(0, 2, (16,))

    loss1 = nn.CrossEntropyLoss()(model1(x), y) * 50.0
    loss2 = nn.CrossEntropyLoss()(model2(x), y) * 50.0

    loss1.backward()
    loss2.backward()

    norm1 = custom_clip_grad_norm(model1, max_norm=1.0)
    norm2 = float(torch.nn.utils.clip_grad_norm_(model2.parameters(), max_norm=1.0).item())

    assert pytest.approx(norm1, abs=1e-4) == norm2
    # Verify parameter gradients match
    for p1, p2 in zip(model1.parameters(), model2.parameters()):
        assert torch.allclose(p1.grad, p2.grad, atol=1e-5)

def test_single_batch_overfit_test_success():
    model = nn.Sequential(
        nn.Linear(16, 32),
        nn.ReLU(),
        nn.Linear(32, 4)
    )
    assert single_batch_overfit_test(model, in_features=16, num_classes=4, batch_size=8, max_steps=40)
