import torch
import math
from torch.optim.lr_scheduler import LambdaLR
from typing import List, Tuple, Dict, Any

def create_warmup_cosine_scheduler(optimizer: torch.optim.Optimizer,
                                    warmup_steps: int,
                                    total_steps: int,
                                    min_lr_ratio: float = 0.01) -> LambdaLR:
    def lr_lambda(current_step: int) -> float:
        if current_step < warmup_steps:
            return float(current_step) / float(max(1, warmup_steps))
        progress = float(current_step - warmup_steps) / float(max(1, total_steps - warmup_steps))
        cosine_decay = 0.5 * (1.0 + math.cos(math.pi * progress))
        return min_lr_ratio + (1.0 - min_lr_ratio) * cosine_decay

    return LambdaLR(optimizer, lr_lambda)

def run_scheduler_demo():
    w = torch.tensor([1.0], requires_grad=True)
    base_lr = 0.01
    optimizer = torch.optim.SGD([w], lr=base_lr)
    total_steps = 100
    warmup_steps = 20

    scheduler = create_warmup_cosine_scheduler(
        optimizer, warmup_steps=warmup_steps, total_steps=total_steps, min_lr_ratio=0.01
    )

    lrs = []
    for step in range(total_steps + 1):
        current_lr = scheduler.get_last_lr()[0]
        lrs.append(current_lr)
        optimizer.zero_grad()
        loss = w ** 2
        loss.backward()
        optimizer.step()
        scheduler.step()

    print(f"Scheduler Demo: Start LR = {lrs[0]:.6f}, Peak LR = {lrs[20]:.6f}, Final LR = {lrs[-1]:.6f}")
    return lrs

if __name__ == "__main__":
    run_scheduler_demo()
