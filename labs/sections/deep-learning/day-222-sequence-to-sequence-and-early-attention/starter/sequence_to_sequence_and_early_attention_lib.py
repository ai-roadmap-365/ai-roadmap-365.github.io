import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional

class BahdanauAttention(nn.Module):
    def __init__(self, enc_dim: int, dec_dim: int, attn_dim: int):
        super().__init__()
        # TODO: Initialize query projection, keys projection, and v_att vector
        pass

    def forward(self, query: torch.Tensor, keys: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        # TODO: Compute additive energy, softmax weights, and dynamic context vector
        pass
