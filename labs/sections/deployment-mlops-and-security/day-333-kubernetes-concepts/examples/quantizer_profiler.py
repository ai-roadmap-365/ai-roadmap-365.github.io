import numpy as np
from typing import Dict, Any, Tuple

class ModelQuantizerProfiler:
    def __init__(self, bit_width: int = 4):
        self.bits = int(bit_width)
        self.q_min = 0
        self.q_max = (1 << self.bits) - 1
        
    def quantize_tensor(self, weights: np.ndarray) -> Tuple[np.ndarray, float, float]:
        w_min = float(np.min(weights))
        w_max = float(np.max(weights))
        
        if w_min == w_max:
            return np.zeros_like(weights, dtype=np.uint8), 1.0, 0.0
            
        scale = (w_max - w_min) / float(self.q_max - self.q_min)
        zero_point = round(-w_min / scale)
        zero_point = max(self.q_min, min(zero_point, self.q_max))
        
        quantized = np.round(weights / scale) + zero_point
        quantized = np.clip(quantized, self.q_min, self.q_max).astype(np.uint8)
        
        return quantized, scale, float(zero_point)

    def dequantize_tensor(self, q_weights: np.ndarray, scale: float, zero_point: float) -> np.ndarray:
        return (q_weights.astype(np.float32) - zero_point) * scale

    def compute_quantization_error(self, original: np.ndarray, reconstructed: np.ndarray) -> Dict[str, float]:
        mse = float(np.mean((original - reconstructed) ** 2))
        snr_db = float(10 * np.log10(np.mean(original ** 2) / (mse + 1e-9)))
        return {
            "mse_error": round(mse, 6),
            "snr_db": round(snr_db, 2),
            "compression_ratio": round(32.0 / self.bits, 2)
        }

if __name__ == "__main__":
    q = ModelQuantizerProfiler(4)
    data = np.array([-1.5, -0.5, 0.0, 0.5, 1.5], dtype=np.float32)
    q_data, s, z = q.quantize_tensor(data)
    rec = q.dequantize_tensor(q_data, s, z)
    print("Metrics:", q.compute_quantization_error(data, rec))
