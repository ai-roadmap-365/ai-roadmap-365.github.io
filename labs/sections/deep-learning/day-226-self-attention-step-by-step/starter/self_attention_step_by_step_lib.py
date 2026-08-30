import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple, Optional

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        # TODO: Initialize projections for W_q, W_k, W_v, W_o
        pass

    def forward(self, q: torch.Tensor, k: torch.Tensor, v: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        # TODO: Implement multi-head linear projections, scaled attention, and concatenation
        pass

def get_sinusoidal_positional_encoding(seq_len: int, d_model: int) -> torch.Tensor:
    # TODO: Generate sinusoidal positional encoding matrix of shape (1, seq_len, d_model)
    pass
