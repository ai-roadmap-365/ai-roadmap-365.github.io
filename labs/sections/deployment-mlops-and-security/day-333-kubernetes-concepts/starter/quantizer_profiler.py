"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import numpy as np
from typing import Dict, Any, Tuple

class ModelQuantizerProfiler:

    def __init__(self, bit_width: int=4):
        self.bits = int(bit_width)
        self.q_min = 0
        self.q_max = (1 << self.bits) - 1

    def quantize_tensor(self, weights: np.ndarray) -> Tuple[np.ndarray, float, float]:
        raise NotImplementedError('TASK 1: implement quantize_tensor.')

    def dequantize_tensor(self, q_weights: np.ndarray, scale: float, zero_point: float) -> np.ndarray:
        raise NotImplementedError('TASK 2: implement dequantize_tensor.')

    def compute_quantization_error(self, original: np.ndarray, reconstructed: np.ndarray) -> Dict[str, float]:
        raise NotImplementedError('TASK 3: implement compute_quantization_error.')
if __name__ == '__main__':
    q = ModelQuantizerProfiler(4)
    data = np.array([-1.5, -0.5, 0.0, 0.5, 1.5], dtype=np.float32)
    q_data, s, z = q.quantize_tensor(data)
    rec = q.dequantize_tensor(q_data, s, z)
    print('Metrics:', q.compute_quantization_error(data, rec))
