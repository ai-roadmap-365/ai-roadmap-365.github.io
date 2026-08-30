import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional

class BahdanauAttention(nn.Module):
    def __init__(self, enc_dim: int, dec_dim: int, attn_dim: int):
        super().__init__()
        self.W_query = nn.Linear(dec_dim, attn_dim, bias=False)
        self.U_keys = nn.Linear(enc_dim, attn_dim, bias=False)
        self.v_att = nn.Linear(attn_dim, 1, bias=False)

    def forward(self, query: torch.Tensor, keys: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        # query: (Batch, dec_dim)
        # keys: (Batch, seq_len, enc_dim)
        proj_query = self.W_query(query).unsqueeze(1) # (Batch, 1, attn_dim)
        proj_keys = self.U_keys(keys) # (Batch, seq_len, attn_dim)

        energy = self.v_att(torch.tanh(proj_query + proj_keys)).squeeze(2) # (Batch, seq_len)

        if mask is not None:
            energy = energy.masked_fill(mask == 0, -1e9)

        attn_weights = F.softmax(energy, dim=1) # (Batch, seq_len)
        context = torch.bmm(attn_weights.unsqueeze(1), keys).squeeze(1) # (Batch, enc_dim)

        return context, attn_weights

def run_attention_demo():
    torch.manual_seed(42)
    attn = BahdanauAttention(enc_dim=8, dec_dim=16, attn_dim=12)
    
    query = torch.randn(2, 16)
    keys = torch.randn(2, 5, 8)
    mask = torch.tensor([[1, 1, 1, 0, 0], [1, 1, 1, 1, 0]])

    context, weights = attn(query, keys, mask=mask)
    weight_sum = weights.sum(dim=1).tolist()

    print(f"Attention Demo: Context Shape = {context.shape}, Weight Sums = {weight_sum}")
    return context, weights

if __name__ == "__main__":
    run_attention_demo()
