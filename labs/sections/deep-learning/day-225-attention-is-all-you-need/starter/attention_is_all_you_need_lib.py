import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple, Optional

class ScaledDotProductAttention(nn.Module):
    def __init__(self, dropout: float = 0.0):
        super().__init__()
        # TODO: Initialize dropout
        pass

    def forward(self, q: torch.Tensor, k: torch.Tensor, v: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        # TODO: Implement Q @ K.T / sqrt(d_k), apply mask, softmax, and @ V
        pass
