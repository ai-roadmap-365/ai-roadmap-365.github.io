# Custom LoRA Linear Layer Implementation in NumPy
import numpy as np
from typing import Tuple, Dict, Any, Optional

class LoRALinear:
    """Low-Rank Adaptation Linear Layer wrapping a frozen base weight matrix."""

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
        self.lora_dropout = lora_dropout
        
        if random_seed is not None:
            np.random.seed(random_seed)

        # 1. Base Weight (Frozen)
        self.weight = np.random.randn(out_features, in_features).astype(np.float32) * 0.02
        self.bias = np.zeros(out_features, dtype=np.float32)
        self.frozen = True

        # 2. LoRA Adapter Matrices
        if self.rank > 0:
            # Matrix A: Gaussian initialization (r x in_features)
            self.lora_A = np.random.randn(rank, in_features).astype(np.float32) * (1.0 / np.sqrt(rank))
            # Matrix B: Zero initialization (out_features x r)
            self.lora_B = np.zeros((out_features, rank), dtype=np.float32)
        else:
            self.lora_A = None
            self.lora_B = None

        self.merged = False

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass: h = x @ W_0^T + (alpha/r) * (x @ A^T) @ B^T + bias"""
        if self.merged or self.rank == 0:
            return x @ self.weight.T + self.bias
        
        # Base forward pass
        base_out = x @ self.weight.T
        
        # LoRA forward pass: (x @ A.T) @ B.T
        lora_out = (x @ self.lora_A.T) @ self.lora_B.T * self.scaling
        
        return base_out + lora_out + self.bias

    def merge_weights(self) -> None:
        """Merges adapter delta (alpha/r) * (B @ A) directly into base weights."""
        if self.merged:
            return
        if self.rank > 0 and self.lora_A is not None and self.lora_B is not None:
            delta_w = (self.lora_B @ self.lora_A) * self.scaling
            self.weight += delta_w
            self.merged = True

    def unmerge_weights(self) -> None:
        """Subtracts adapter delta from base weights to restore unmerged state."""
        if not self.merged:
            return
        if self.rank > 0 and self.lora_A is not None and self.lora_B is not None:
            delta_w = (self.lora_B @ self.lora_A) * self.scaling
            self.weight -= delta_w
            self.merged = False

    def count_parameters(self) -> Dict[str, int]:
        """Calculates frozen base parameters vs trainable LoRA parameters."""
        base_params = self.weight.size + self.bias.size
        lora_params = 0
        if self.rank > 0 and self.lora_A is not None and self.lora_B is not None:
            lora_params = self.lora_A.size + self.lora_B.size
        
        return {
            "base_parameters": base_params,
            "trainable_lora_parameters": lora_params,
            "total_parameters": base_params + lora_params,
            "trainable_percentage": (lora_params / base_params) * 100.0 if base_params > 0 else 0.0
        }
