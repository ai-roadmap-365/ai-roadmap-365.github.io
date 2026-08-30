import pytest
import numpy as np
from examples.quantizer_profiler import ModelQuantizerProfiler

def test_quantize_and_dequantize_bounds():
    quantizer = ModelQuantizerProfiler(bit_width=4)
    weights = np.linspace(-2.0, 2.0, 100, dtype=np.float32)
    
    q_weights, scale, zero_point = quantizer.quantize_tensor(weights)
    assert np.min(q_weights) >= 0
    assert np.max(q_weights) <= 15
    assert scale > 0
    
    reconstructed = quantizer.dequantize_tensor(q_weights, scale, zero_point)
    metrics = quantizer.compute_quantization_error(weights, reconstructed)
    assert metrics["mse_error"] < 0.05
    assert metrics["compression_ratio"] == 8.0

def test_constant_weight_array():
    quantizer = ModelQuantizerProfiler(bit_width=4)
    weights = np.ones(50, dtype=np.float32) * 3.5
    
    q_weights, scale, zero_point = quantizer.quantize_tensor(weights)
    assert len(q_weights) == 50
    assert scale == 1.0

def test_8bit_quantization_fidelity():
    quantizer = ModelQuantizerProfiler(bit_width=8)
    weights = np.random.randn(200).astype(np.float32)
    
    q_weights, scale, zero_point = quantizer.quantize_tensor(weights)
    assert np.max(q_weights) <= 255
    
    reconstructed = quantizer.dequantize_tensor(q_weights, scale, zero_point)
    metrics = quantizer.compute_quantization_error(weights, reconstructed)
    assert metrics["mse_error"] < 0.001
    assert metrics["compression_ratio"] == 4.0

def test_snr_calculation():
    quantizer = ModelQuantizerProfiler(bit_width=4)
    weights = np.sin(np.linspace(0, 10, 500)).astype(np.float32)
    
    q_weights, s, z = quantizer.quantize_tensor(weights)
    rec = quantizer.dequantize_tensor(q_weights, s, z)
    metrics = quantizer.compute_quantization_error(weights, rec)
    assert metrics["snr_db"] > 15.0

def test_zero_point_clamping():
    quantizer = ModelQuantizerProfiler(bit_width=4)
    weights = np.array([100.0, 101.0, 102.0], dtype=np.float32)
    q_weights, s, z = quantizer.quantize_tensor(weights)
    assert 0 <= z <= 15
