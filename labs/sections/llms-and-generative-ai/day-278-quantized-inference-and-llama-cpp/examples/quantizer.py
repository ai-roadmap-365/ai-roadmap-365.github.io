# INT8 Symmetric Quantizer, Dequantizer, and GGUF Header Parser
import struct
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

class GGUFHeaderParser:
    """Parses binary GGUF file headers."""

    @staticmethod
    def parse_header_bytes(header_bytes: bytes) -> Dict[str, Any]:
        if len(header_bytes) < 16:
            raise ValueError("Header too short (must be >= 16 bytes)")
        
        magic = header_bytes[:4]
        if magic != b"GGUF":
            raise ValueError(f"Invalid GGUF magic bytes: {magic}")

        version, tensor_count, metadata_kv_count = struct.unpack("<III", header_bytes[4:16])
        
        return {
            "magic": "GGUF",
            "version": version,
            "tensor_count": tensor_count,
            "metadata_kv_count": metadata_kv_count
        }

    @staticmethod
    def pack_header(version: int = 3, tensor_count: int = 291, metadata_kv_count: int = 35) -> bytes:
        return b"GGUF" + struct.pack("<III", version, tensor_count, metadata_kv_count)

class SymmetricINT8Quantizer:
    """Performs symmetric linear INT8 quantization and dequantization on tensors."""

    def __init__(self):
        pass

    def quantize_tensor(self, tensor: np.ndarray) -> Tuple[np.ndarray, float]:
        """Quantizes continuous float tensor to signed INT8 [-128, 127]."""
        float_tensor = tensor.astype(np.float32)
        max_abs = float(np.max(np.abs(float_tensor)))
        
        if max_abs == 0.0:
            scale = 1.0
            quantized = np.zeros(float_tensor.shape, dtype=np.int8)
        else:
            scale = max_abs / 127.0
            scaled = float_tensor / scale
            clipped = np.clip(np.round(scaled), -128, 127)
            quantized = clipped.astype(np.int8)

        return quantized, scale

    def dequantize_tensor(self, quantized_tensor: np.ndarray, scale: float) -> np.ndarray:
        """Reconstructs approximate float tensor: x_approx = q * scale."""
        return quantized_tensor.astype(np.float32) * scale

    def compute_mse_distortion(self, original: np.ndarray, reconstructed: np.ndarray) -> float:
        """Computes Mean Squared Error (MSE) between original and dequantized tensor."""
        return float(np.mean((original.astype(np.float32) - reconstructed.astype(np.float32)) ** 2))

    def evaluate_compression(self, original_fp32: np.ndarray, quantized_int8: np.ndarray) -> Dict[str, float]:
        """Calculates memory compression metrics."""
        orig_bytes = original_fp32.nbytes
        quant_bytes = quantized_int8.nbytes + 4 # 4 bytes for float32 scale factor
        reduction = (1.0 - (quant_bytes / orig_bytes)) * 100.0 if orig_bytes > 0 else 0.0
        
        return {
            "original_bytes": float(orig_bytes),
            "quantized_bytes": float(quant_bytes),
            "compression_ratio": float(orig_bytes / quant_bytes) if quant_bytes > 0 else 1.0,
            "reduction_percentage": float(reduction)
        }
