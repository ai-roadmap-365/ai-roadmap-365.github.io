import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List

class EmbeddingBagClassifier(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int, num_classes: int):
        super().__init__()
        # TODO: Initialize nn.EmbeddingBag with mode="mean" and linear head
        pass

    def forward(self, text_indices: torch.Tensor, offsets: torch.Tensor = None) -> torch.Tensor:
        # TODO: Compute mean document representation and logits
        pass

class TextCNN(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int, num_classes: int,
                 num_filters: int = 16, filter_sizes: List[int] = [2, 3]):
        super().__init__()
        # TODO: Initialize embedding, parallel Conv1d layers, and linear head
        pass

    def forward(self, text_indices: torch.Tensor) -> torch.Tensor:
        # TODO: Apply convolutions, 1-max pooling, and classification head
        pass
