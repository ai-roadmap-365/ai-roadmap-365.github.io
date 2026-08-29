import torch
import torch.nn as nn
from typing import Tuple, Dict, Any

class CustomDropout(nn.Module):
    def __init__(self, p: float = 0.5):
        super().__init__()
        self.p = p

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # TODO: Implement Inverted Dropout
        pass

class CustomBatchNorm1d(nn.Module):
    def __init__(self, num_features: int, eps: float = 1e-5, momentum: float = 0.1):
        super().__init__()
        # TODO: Initialize gamma, beta, running_mean, running_var
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # TODO: Implement BatchNorm forward pass for train and eval modes
        pass
