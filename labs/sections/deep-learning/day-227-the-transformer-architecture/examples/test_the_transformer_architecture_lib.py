import pytest
import torch
from examples.the_transformer_architecture_lib import TransformerEncoderLayer

def test_transformer_encoder_layer_shapes():
    torch.manual_seed(42)
    layer = TransformerEncoderLayer(d_model=32, num_heads=4, d_ffn=128)
    x = torch.randn(2, 5, 32)
    out = layer(x)
    assert out.shape == (2, 5, 32)

def test_residual_gradient_flow():
    torch.manual_seed(42)
    layer = TransformerEncoderLayer(d_model=16, num_heads=2, d_ffn=64)
    x = torch.randn(2, 4, 16, requires_grad=True)
    out = layer(x)
    loss = out.sum()
    loss.backward()
    
    assert x.grad is not None
    assert (x.grad.abs() > 0).all()
