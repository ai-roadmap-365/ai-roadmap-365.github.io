import pytest
import torch
from examples.transfer_learning_lib import build_transfer_learning_model, configure_differential_optimizer

def test_frozen_backbone_parameters():
    model = build_transfer_learning_model(num_classes=5, freeze_backbone=True)
    # Check that backbone is frozen
    for p in model.backbone.parameters():
        assert p.requires_grad is False
    # Check that head is trainable
    for p in model.fc.parameters():
        assert p.requires_grad is True

def test_gradient_isolation():
    model = build_transfer_learning_model(num_classes=5, freeze_backbone=True)
    x = torch.randn(4, 3, 32, 32)
    y = torch.randint(0, 5, (4,))

    logits = model(x)
    loss = torch.nn.CrossEntropyLoss()(logits, y)
    loss.backward()

    # Backbone weights must have None grad
    for p in model.backbone.parameters():
        assert p.grad is None
    # Head weights must have non-zero grad
    for p in model.fc.parameters():
        assert p.grad is not None

def test_differential_optimizer_groups():
    model = build_transfer_learning_model(num_classes=5, freeze_backbone=False)
    opt = configure_differential_optimizer(model, head_lr=1e-3, backbone_lr=1e-5)
    assert len(opt.param_groups) == 2
    assert opt.param_groups[0]["lr"] == 1e-5
    assert opt.param_groups[1]["lr"] == 1e-3
