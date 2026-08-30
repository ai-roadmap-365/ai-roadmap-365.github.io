import torch
import torch.nn as nn
from typing import Tuple

class CustomLSTMCell(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        # TODO: Initialize linear projections for forget, input, candidate, output gates
        pass

    def forward(self, x_t: torch.Tensor, states: Tuple[torch.Tensor, torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        # TODO: Compute LSTM gating equations and return (h_t, C_t)
        pass

class CustomGRUCell(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        # TODO: Initialize linear projections for reset, update, and candidate states
        pass

    def forward(self, x_t: torch.Tensor, h_prev: torch.Tensor) -> torch.Tensor:
        # TODO: Compute GRU equations and return h_t
        pass
