import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class GPTDecoderLayer(nn.Module):
    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        # TODO: Initialize Pre-LN layers, causal MultiheadAttention, and FFN
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # TODO: Implement causal transformer block with residual streams
        pass

class MiniatureGPT(nn.Module):
    def __init__(self, vocab_size: int = 200, d_model: int = 32,
                 num_layers: int = 2, num_heads: int = 2):
        super().__init__()
        # TODO: Initialize embeddings, decoder stack, and tied language model head
        pass

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        # TODO: Pass input through causal decoder and compute vocabulary logits
        pass

    @torch.no_grad()
    def generate(self, prompt_ids: torch.Tensor, max_new_tokens: int = 5,
                 temperature: float = 1.0) -> torch.Tensor:
        # TODO: Autoregressive token-by-token generation loop
        pass
