import pytest
import torch
from examples.attention_is_all_you_need_lib import ScaledDotProductAttention

def test_scaled_dot_product_attention_shapes():
    torch.manual_seed(42)
    attn = ScaledDotProductAttention()
    q = torch.randn(2, 4, 5, 16)
    k = torch.randn(2, 4, 5, 16)
    v = torch.randn(2, 4, 5, 16)

    out, weights = attn(q, k, v)
    assert out.shape == (2, 4, 5, 16)
    assert weights.shape == (2, 4, 5, 5)
    
    # Softmax rows must sum to 1.0
    row_sums = weights.sum(dim=-1)
    for val in row_sums.flatten():
        assert pytest.approx(val.item(), 1e-5) == 1.0

def test_causal_masking():
    torch.manual_seed(42)
    attn = ScaledDotProductAttention()
    seq_len = 4
    q = torch.randn(1, 1, seq_len, 8)
    k = torch.randn(1, 1, seq_len, 8)
    v = torch.randn(1, 1, seq_len, 8)

    # Causal lower-triangular mask
    mask = torch.tril(torch.ones(seq_len, seq_len)).unsqueeze(0).unsqueeze(0)
    out, weights = attn(q, k, v, mask=mask)

    # Upper triangular values must be strictly 0.0
    for i in range(seq_len):
        for j in range(i + 1, seq_len):
            assert weights[0, 0, i, j].item() < 1e-5
