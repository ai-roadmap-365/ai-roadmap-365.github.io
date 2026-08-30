import pytest
import torch
from examples.sequence_to_sequence_and_early_attention_lib import BahdanauAttention

def test_attention_dimensions_and_sum():
    torch.manual_seed(42)
    attn = BahdanauAttention(enc_dim=10, dec_dim=20, attn_dim=15)
    query = torch.randn(4, 20)
    keys = torch.randn(4, 7, 10)

    context, weights = attn(query, keys)
    assert context.shape == (4, 10)
    assert weights.shape == (4, 7)
    
    # Softmax weights must sum to 1.0
    for s in weights.sum(dim=1):
        assert pytest.approx(s.item(), 1e-5) == 1.0

def test_attention_masking():
    torch.manual_seed(42)
    attn = BahdanauAttention(enc_dim=6, dec_dim=12, attn_dim=8)
    query = torch.randn(2, 12)
    keys = torch.randn(2, 4, 6)
    mask = torch.tensor([[1, 1, 0, 0], [1, 1, 1, 0]])

    _, weights = attn(query, keys, mask=mask)
    # Masked positions should have near-zero weights
    assert weights[0, 2].item() < 1e-4
    assert weights[0, 3].item() < 1e-4
    assert weights[1, 3].item() < 1e-4
