import torch
import torch.nn as nn
from typing import Tuple

class SimpleRNNModel(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, num_classes: int):
        super().__init__()
        # TODO: Initialize W_xh, W_hh, and W_hy linear projections
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # TODO: Unroll sequence across time and return logits from final hidden state
        pass

def clip_gradient_norm(parameters, max_norm: float = 1.0) -> float:
    # TODO: Compute and clip global gradient norm
    pass
