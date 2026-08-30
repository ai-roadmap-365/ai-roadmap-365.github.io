import pytest
import numpy as np
from lora_layer import LoRALinear

def test_lora_initialization_zero_delta():
    layer = LoRALinear(in_features=128, out_features=256, rank=8, alpha=16.0, random_seed=42)
    x = np.random.randn(4, 128).astype(np.float32)
    
    # At step 0, B=0, so LoRA output must be bit-exact equal to base linear forward
    out = layer.forward(x)
    expected_base = x @ layer.weight.T + layer.bias
    np.testing.assert_allclose(out, expected_base, rtol=1e-5, atol=1e-6)

def test_parameter_counts_and_reduction():
    # 4096 -> 4096 projection (like Llama self-attention)
    layer = LoRALinear(in_features=4096, out_features=4096, rank=8, alpha=16.0)
    counts = layer.count_parameters()
    
    assert counts["base_parameters"] == 4096 * 4096 + 4096 # 16,781,312
    # LoRA A: 8 * 4096 = 32,768 | LoRA B: 4096 * 8 = 32,768 -> Total: 65,536
    assert counts["trainable_lora_parameters"] == 65536
    assert counts["trainable_percentage"] < 0.4 # Less than 0.4% of base

def test_lora_forward_with_trained_weights():
    layer = LoRALinear(in_features=64, out_features=32, rank=4, alpha=8.0, random_seed=42)
    # Simulate trained non-zero B matrix
    layer.lora_B = np.random.randn(32, 4).astype(np.float32) * 0.1
    
    x = np.random.randn(2, 64).astype(np.float32)
    out = layer.forward(x)
    
    # Calculate manual forward
    manual_base = x @ layer.weight.T + layer.bias
    manual_lora = (x @ layer.lora_A.T) @ layer.lora_B.T * (8.0 / 4.0)
    np.testing.assert_allclose(out, manual_base + manual_lora, rtol=1e-5, atol=1e-6)

def test_weight_merging_bit_exactness():
    layer = LoRALinear(in_features=64, out_features=32, rank=4, alpha=8.0, random_seed=42)
    layer.lora_B = np.random.randn(32, 4).astype(np.float32) * 0.1
    
    x = np.random.randn(5, 64).astype(np.float32)
    out_before_merge = layer.forward(x)
    
    # Merge weights offline
    layer.merge_weights()
    assert layer.merged is True
    
    out_after_merge = layer.forward(x)
    # Merged single matrix multiplication must be bit-exact to dual-path computation
    np.testing.assert_allclose(out_before_merge, out_after_merge, rtol=1e-5, atol=1e-6)

def test_unmerge_weights_reversibility():
    layer = LoRALinear(in_features=32, out_features=16, rank=4, alpha=8.0, random_seed=42)
    layer.lora_B = np.random.randn(16, 4).astype(np.float32) * 0.1
    
    initial_w = layer.weight.copy()
    layer.merge_weights()
    assert not np.array_equal(layer.weight, initial_w)
    
    layer.unmerge_weights()
    assert layer.merged is False
    np.testing.assert_allclose(layer.weight, initial_w, rtol=1e-5, atol=1e-6)

def test_zero_rank_pass_through():
    layer = LoRALinear(in_features=32, out_features=16, rank=0)
    counts = layer.count_parameters()
    assert counts["trainable_lora_parameters"] == 0
    x = np.random.randn(2, 32).astype(np.float32)
    out = layer.forward(x)
    np.testing.assert_allclose(out, x @ layer.weight.T + layer.bias)
