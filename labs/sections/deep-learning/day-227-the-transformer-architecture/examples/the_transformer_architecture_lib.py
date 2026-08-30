import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class TransformerEncoderLayer(nn.Module):
    def __init__(self, d_model: int, num_heads: int, d_ffn: Optional[int] = None, dropout: float = 0.1):
        super().__init__()
        if d_ffn is None:
            d_ffn = 4 * d_model
        
        self.norm1 = nn.LayerNorm(d_model)
        self.self_attn = nn.MultiheadAttention(embed_dim=d_model, num_heads=num_heads, dropout=dropout, batch_first=True)
        self.dropout1 = nn.Dropout(dropout)

        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ffn),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ffn, d_model),
            nn.Dropout(dropout)
        )

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Pre-LN Block 1: Attention
        normed_x = self.norm1(x)
        attn_out, _ = self.self_attn(query=normed_x, key=normed_x, value=normed_x, key_padding_mask=mask)
        x = x + self.dropout1(attn_out)

        # Pre-LN Block 2: FFN
        x = x + self.ffn(self.norm2(x))
        return x

def run_transformer_block_demo():
    torch.manual_seed(42)
    layer = TransformerEncoderLayer(d_model=32, num_heads=4, d_ffn=128)
    x = torch.randn(2, 6, 32)
    out = layer(x)

    print(f"Transformer Block Demo: Output Shape = {out.shape}")
    return out

if __name__ == "__main__":
    run_transformer_block_demo()
