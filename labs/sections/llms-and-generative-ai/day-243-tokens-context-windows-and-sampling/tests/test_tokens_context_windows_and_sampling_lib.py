import pytest
import torch
from examples.tokens_context_windows_and_sampling_lib import (
    calculate_kv_cache_bytes,
    sample_next_token
)

def test_kv_cache_calculation():
    # 1 batch, 1024 seq, 32 layers, 32 heads, 64 dim, 2 bytes
    # 2 * 1 * 1024 * 32 * (32 * 64) * 2 = 2 * 1024 * 32 * 2048 * 2 = 268,435,456 bytes = 256 MB
    kv_bytes = calculate_kv_cache_bytes(1, 1024, 32, 32, 64, bytes_per_elem=2)
    assert kv_bytes == 268435456

def test_greedy_sampling_determinism():
    logits = torch.tensor([1.0, 2.0, 5.0, 3.0])
    for _ in range(10):
        # Index 2 has highest logit (5.0)
        tok = sample_next_token(logits, temperature=0.0)
        assert tok == 2

def test_top_k_sampling_bounds():
    torch.manual_seed(42)
    # Logits where top 2 are indices 0 and 1, rest are very negative
    logits = torch.tensor([10.0, 9.0, -100.0, -100.0, -100.0])
    for _ in range(10):
        tok = sample_next_token(logits, temperature=1.0, top_k=2)
        assert tok in [0, 1]
