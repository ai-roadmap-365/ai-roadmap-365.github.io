import pytest
import torch
from examples.self_attention_step_by_step_lib import MultiHeadAttention, get_sinusoidal_positional_encoding

def test_multi_head_attention_shapes():
    torch.manual_seed(42)
    mha = MultiHeadAttention(d_model=32, num_heads=4)
    x = torch.randn(2, 5, 32)
    out, weights = mha(x, x, x)
    
    assert out.shape == (2, 5, 32)
    assert weights.shape == (2, 4, 5, 5)

def test_sinusoidal_positional_encoding():
    pe = get_sinusoidal_positional_encoding(seq_len=8, d_model=16)
    assert pe.shape == (1, 8, 16)
    # Values should lie between -1.0 and 1.0
    assert (pe >= -1.0).all() and (pe <= 1.0).all()
