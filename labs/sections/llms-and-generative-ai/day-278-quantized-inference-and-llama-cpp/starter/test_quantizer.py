import pytest
import numpy as np
from quantizer import GGUFHeaderParser, SymmetricINT8Quantizer

@pytest.fixture
def quantizer():
    return SymmetricINT8Quantizer()

def test_gguf_header_pack_and_parse():
    packed = GGUFHeaderParser.pack_header(version=3, tensor_count=291, metadata_kv_count=35)
    parsed = GGUFHeaderParser.parse_header_bytes(packed)
    assert parsed["magic"] == "GGUF"
    assert parsed["version"] == 3
    assert parsed["tensor_count"] == 291
    assert parsed["metadata_kv_count"] == 35

def test_invalid_gguf_header():
    invalid_bytes = b"GGML" + b"\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    with pytest.raises(ValueError, match="Invalid GGUF"):
        GGUFHeaderParser.parse_header_bytes(invalid_bytes)

def test_symmetric_quantization_roundtrip(quantizer):
    np.random.seed(42)
    original = np.random.randn(128, 128).astype(np.float32) * 2.5
    
    q_tensor, scale = quantizer.quantize_tensor(original)
    assert q_tensor.dtype == np.int8
    assert np.min(q_tensor) >= -128
    assert np.max(q_tensor) <= 127
    
    recon = quantizer.dequantize_tensor(q_tensor, scale)
    mse = quantizer.compute_mse_distortion(original, recon)
    assert mse < 0.001 # Minimal quantization distortion

def test_all_zeros_tensor_quantization(quantizer):
    zeros = np.zeros((10, 10), dtype=np.float32)
    q_tensor, scale = quantizer.quantize_tensor(zeros)
    assert scale == 1.0
    assert np.all(q_tensor == 0)

def test_compression_metrics(quantizer):
    tensor = np.random.randn(256, 256).astype(np.float32)
    q_tensor, scale = quantizer.quantize_tensor(tensor)
    metrics = quantizer.evaluate_compression(tensor, q_tensor)
    
    assert metrics["original_bytes"] == 256 * 256 * 4 # 262,144 bytes
    assert metrics["quantized_bytes"] == 256 * 256 * 1 + 4 # 65,540 bytes
    assert metrics["reduction_percentage"] > 74.0 # ~75% reduction
