import pytest
import torch
from examples.quantization_and_distillation_lib import (
    quantize_symmetric_int8,
    dequantize_symmetric_int8,
    KnowledgeDistillationLoss
)

def test_symmetric_int8_exactness():
    x = torch.tensor([-1.27, 0.0, 1.27], dtype=torch.float32)
    q, s = quantize_symmetric_int8(x)
    assert s == pytest.approx(0.01, rel=1e-3)
    assert q.tolist() == [-127, 0, 127]
    
    x_hat = dequantize_symmetric_int8(q, s)
    torch.testing.assert_close(x, x_hat, rtol=1e-3, atol=1e-3)

def test_kd_loss_formulation():
    kd = KnowledgeDistillationLoss(temperature=2.0, alpha=0.5)
    s_log = torch.tensor([[2.0, 0.0], [0.0, 2.0]], dtype=torch.float32)
    t_log = torch.tensor([[2.0, 0.0], [0.0, 2.0]], dtype=torch.float32)
    y = torch.tensor([0, 1])

    loss = kd(s_log, t_log, y)
    # When teacher and student match exactly, soft loss is 0.0
    # Hard loss is standard CE
    assert loss.item() > 0.0
    assert loss.item() < 1.0

def test_kd_loss_temperature_gradient_scaling():
    kd_high_t = KnowledgeDistillationLoss(temperature=10.0, alpha=1.0)
    s_log = torch.randn(4, 5, requires_grad=True)
    t_log = torch.randn(4, 5)
    y = torch.tensor([0, 1, 2, 3])

    loss = kd_high_t(s_log, t_log, y)
    loss.backward()
    assert s_log.grad is not None
    assert torch.isfinite(s_log.grad).all()
