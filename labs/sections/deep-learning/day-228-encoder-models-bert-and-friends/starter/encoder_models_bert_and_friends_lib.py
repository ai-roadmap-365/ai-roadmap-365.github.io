import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class BERTMaskedLM(nn.Module):
    def __init__(self, vocab_size: int = 1000, d_model: int = 32,
                 num_layers: int = 2, num_heads: int = 4):
        super().__init__()
        # TODO: Initialize token embeddings, positional embeddings, transformer, and MLM head
        pass

    def forward(self, input_ids: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # TODO: Add embeddings, pass through transformer encoder, and compute MLM logits
        pass
