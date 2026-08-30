import torch
import torch.nn as nn
from typing import Tuple, Dict, Any

class BasicResidualBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()
        # TODO: Implement Residual Block with 1x1 projection shortcut
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        pass

class MiniResNet(nn.Module):
    def __init__(self, num_classes: int = 10):
        super().__init__()
        # TODO: Implement MiniResNet architecture with stem, stages, GAP, and classifier
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        pass
