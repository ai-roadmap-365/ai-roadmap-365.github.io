import torch
import torch.nn as nn
from typing import Tuple, Dict, Any, List

def build_transfer_learning_model(num_classes: int = 5, freeze_backbone: bool = True) -> nn.Module:
    # TODO: Build modular model with frozen backbone and custom classifier head
    pass

def configure_differential_optimizer(model: nn.Module, head_lr: float = 1e-3,
                                     backbone_lr: float = 1e-5) -> torch.optim.Optimizer:
    # TODO: Configure PyTorch optimizer with differential layer-wise learning rates
    pass
