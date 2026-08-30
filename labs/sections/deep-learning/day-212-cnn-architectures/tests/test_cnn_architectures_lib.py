import pytest
import torch
from examples.cnn_architectures_lib import BasicResidualBlock, MiniResNet

def test_basic_residual_block_same_dim():
    block = BasicResidualBlock(in_channels=16, out_channels=16, stride=1)
    x = torch.randn(2, 16, 8, 8)
    out = block(x)
    assert out.shape == (2, 16, 8, 8)

def test_basic_residual_block_downsample():
    block = BasicResidualBlock(in_channels=16, out_channels=32, stride=2)
    x = torch.randn(2, 16, 8, 8)
    out = block(x)
    assert out.shape == (2, 32, 4, 4)

def test_mini_resnet_gradient_flow():
    model = MiniResNet(in_channels=3, num_classes=5)
    x = torch.randn(4, 3, 32, 32)
    y = torch.randint(0, 5, (4,))

    logits = model(x)
    loss = torch.nn.CrossEntropyLoss()(logits, y)
    loss.backward()

    # Verify every weight tensor in the stem and residual layers received gradients
    for name, p in model.named_parameters():
        if p.requires_grad:
            assert p.grad is not None
            assert torch.norm(p.grad).item() > 0.0
