import torch
import math
from torch.optim.lr_scheduler import LambdaLR
from typing import List, Tuple, Dict, Any

def create_warmup_cosine_scheduler(optimizer: torch.optim.Optimizer,
                                    warmup_steps: int,
                                    total_steps: int,
                                    min_lr_ratio: float = 0.01) -> LambdaLR:
    # TODO: Implement Warmup + Cosine Decay LambdaLR scheduler
    pass
