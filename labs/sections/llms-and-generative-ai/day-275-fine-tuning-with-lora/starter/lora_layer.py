# Starter: Custom LoRA Linear Layer in NumPy
import numpy as np
from typing import Dict, Optional

class LoRALinear:
    def __init__(
        self,
        in_features: int,
        out_features: int,
        rank: int = 8,
        alpha: float = 16.0,
        lora_dropout: float = 0.0,
        random_seed: Optional[int] = 42
    ):
        self.in_features = in_features
        self.out_features = out_features
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank if rank > 0 else 1.0
        self.weight = np.random.randn(out_features, in_features).astype(np.float32) * 0.02
        self.bias = np.zeros(out_features, dtype=np.float32)
        self.merged = False

    def forward(self, x: np.ndarray) -> np.ndarray:
        return x @ self.weight.T + self.bias

    def merge_weights(self) -> None:
        self.merged = True

    def count_parameters(self) -> Dict[str, int]:
        return {
            "base_parameters": self.weight.size + self.bias.size,
            "trainable_lora_parameters": 0,
            "total_parameters": self.weight.size + self.bias.size,
            "trainable_percentage": 0.0
        }
