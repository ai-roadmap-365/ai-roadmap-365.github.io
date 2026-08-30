import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

class BiLSTMAttentionSentiment(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int, hidden_dim: int, num_classes: int = 2):
        super().__init__()
        # TODO: Initialize embedding, LSTM, attention projections, and classifier
        pass

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor]:
        # TODO: Compute BiLSTM states, attention weights, pooled document vector, and logits
        pass

    def explain_tokens(self, x: torch.Tensor, target_class: int = 1) -> Tuple[torch.Tensor, torch.Tensor]:
        # TODO: Compute token attribution saliency via input embedding gradients
        pass
