import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class TransformerEncoderLayer(nn.Module):
    def __init__(self, d_model: int, num_heads: int, d_ffn: Optional[int] = None, dropout: float = 0.1):
        super().__init__()
        # TODO: Initialize Pre-LN norms, MultiheadAttention, and FFN with 4x expansion
        pass

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # TODO: Implement Pre-LN attention block and Pre-LN FFN block with residual streams
        pass
