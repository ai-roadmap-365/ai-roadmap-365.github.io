import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple, Optional

class ScaledDotProductAttention(nn.Module):
    def __init__(self, dropout: float = 0.0):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

    def forward(self, q: torch.Tensor, k: torch.Tensor, v: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        # q: (..., Seq_Q, d_k)
        # k: (..., Seq_K, d_k)
        # v: (..., Seq_K, d_v)
        d_k = q.size(-1)
        scale = 1.0 / math.sqrt(d_k)

        scores = torch.matmul(q, k.transpose(-2, -1)) * scale

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        output = torch.matmul(attn_weights, v)
        return output, attn_weights

def run_attention_demo():
    torch.manual_seed(42)
    attn = ScaledDotProductAttention()
    q = torch.randn(2, 4, 6, 16)
    k = torch.randn(2, 4, 6, 16)
    v = torch.randn(2, 4, 6, 16)

    out, weights = attn(q, k, v)
    print(f"Scaled Attention Demo: Output Shape = {out.shape}, Weights Shape = {weights.shape}")
    return out, weights

if __name__ == "__main__":
    run_attention_demo()
