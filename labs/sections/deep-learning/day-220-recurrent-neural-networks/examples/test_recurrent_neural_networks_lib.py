import pytest
import torch
from examples.recurrent_neural_networks_lib import SimpleRNNModel, clip_gradient_norm

def test_rnn_forward_pass_dimensions():
    torch.manual_seed(42)
    model = SimpleRNNModel(input_dim=8, hidden_dim=16, num_classes=3)
    x = torch.randn(4, 10, 8)
    logits = model(x)
    assert logits.shape == (4, 3)

def test_gradient_norm_clipping():
    torch.manual_seed(42)
    model = SimpleRNNModel(input_dim=4, hidden_dim=4, num_classes=2)
    x = torch.randn(2, 3, 4)
    loss = model(x).sum() * 100.0 # Force huge gradient
    loss.backward()

    orig_norm = clip_gradient_norm(model.parameters(), max_norm=1.0)
    assert orig_norm > 1.0

    # Verify post-clip norm is <= 1.0
    params = [p for p in model.parameters() if p.grad is not None]
    post_norm = torch.norm(torch.stack([torch.norm(p.grad.detach(), 2) for p in params]), 2).item()
    assert pytest.approx(post_norm, 1e-3) == 1.0
