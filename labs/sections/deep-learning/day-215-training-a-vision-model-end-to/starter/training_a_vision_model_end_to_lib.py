import torch
import torch.nn as nn
from typing import Tuple, Dict, Any, List

def calculate_topk_accuracy(logits: torch.Tensor, targets: torch.Tensor, k: int = 5) -> float:
    # TODO: Calculate Top-K classification accuracy
    pass

def compute_confusion_matrix(preds: torch.Tensor, targets: torch.Tensor, num_classes: int) -> torch.Tensor:
    # TODO: Compute normalized multi-class confusion matrix
    pass
