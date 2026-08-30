import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Dict, Any

class SkipGramNegativeSampling(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int):
        super().__init__()
        # TODO: Initialize target embeddings and context embeddings
        pass

    def forward(self, center_words: torch.Tensor, context_words: torch.Tensor,
                negative_words: torch.Tensor) -> torch.Tensor:
        # TODO: Compute Negative Sampling loss
        pass

def compute_cosine_similarity(v1: torch.Tensor, v2: torch.Tensor) -> float:
    # TODO: Compute cosine similarity between two 1D vectors
    pass
