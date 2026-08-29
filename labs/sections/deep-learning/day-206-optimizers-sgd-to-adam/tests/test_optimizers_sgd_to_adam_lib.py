import pytest
import torch
from examples.optimizers_sgd_to_adam_lib import CustomAdamW

def test_custom_adamw_initialization():
    w = torch.randn(10, requires_grad=True)
    opt = CustomAdamW([w], lr=0.01, weight_decay=0.05)
    assert opt.defaults['lr'] == 0.01
    assert opt.defaults['weight_decay'] == 0.05
    assert len(opt.param_groups) == 1

def test_custom_adamw_matches_torch_adamw():
    torch.manual_seed(42)
    w1 = torch.randn(5, 5, requires_grad=True)
    w2 = w1.clone().detach().requires_grad_(True)

    opt1 = CustomAdamW([w1], lr=0.05, weight_decay=0.01)
    opt2 = torch.optim.AdamW([w2], lr=0.05, weight_decay=0.01)

    for _ in range(5):
        opt1.zero_grad()
        opt2.zero_grad()

        loss1 = (w1 ** 2).sum()
        loss2 = (w2 ** 2).sum()

        loss1.backward()
        loss2.backward()

        opt1.step()
        opt2.step()

        assert torch.allclose(w1, w2, atol=1e-6)

def test_custom_adamw_reduces_loss():
    w = torch.tensor([5.0, -3.0], requires_grad=True)
    opt = CustomAdamW([w], lr=0.1)

    loss_start = float((w ** 2).sum().item())
    for _ in range(10):
        opt.zero_grad()
        loss = (w ** 2).sum()
        loss.backward()
        opt.step()

    loss_end = float((w ** 2).sum().item())
    assert loss_end < loss_start

def test_decoupled_weight_decay():
    w = torch.tensor([10.0], requires_grad=True)
    # Zero gradient scenario: only weight decay should act
    opt = CustomAdamW([w], lr=0.1, weight_decay=0.1)
    w.grad = torch.zeros_like(w)
    opt.step()
    # w_new = w * (1 - 0.1 * 0.1) = 10.0 * 0.99 = 9.9
    assert torch.isclose(w, torch.tensor([9.9]))
