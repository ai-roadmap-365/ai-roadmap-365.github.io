import torch
import torch.nn as nn
from typing import Tuple, List, Dict, Any

def compute_global_gradient_norm(model: nn.Module) -> float:
    total_norm_sq = 0.0
    for p in model.parameters():
        if p.grad is not None:
            total_norm_sq += float((p.grad.detach() ** 2).sum().item())
    return float(total_norm_sq ** 0.5)

def custom_clip_grad_norm(model: nn.Module, max_norm: float = 1.0) -> float:
    total_norm = compute_global_gradient_norm(model)
    if total_norm > max_norm and total_norm > 0:
        clip_coef = max_norm / (total_norm + 1e-6)
        with torch.no_grad():
            for p in model.parameters():
                if p.grad is not None:
                    p.grad.mul_(clip_coef)
    return total_norm

def single_batch_overfit_test(model: nn.Module, in_features: int = 32,
                              num_classes: int = 10, batch_size: int = 16,
                              max_steps: int = 50) -> bool:
    torch.manual_seed(42)
    x = torch.randn(batch_size, in_features)
    y = torch.randint(0, num_classes, (batch_size,))

    optimizer = torch.optim.AdamW(model.parameters(), lr=0.02)
    criterion = nn.CrossEntropyLoss()

    model.train()
    for step in range(max_steps):
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        custom_clip_grad_norm(model, max_norm=1.0)
        optimizer.step()

        preds = torch.argmax(logits, dim=1)
        acc = float((preds == y).float().mean().item())

        if loss.item() < 0.01 and acc == 1.0:
            return True

    return False

def run_debugging_demo():
    torch.manual_seed(42)
    model = nn.Sequential(
        nn.Linear(32, 64),
        nn.ReLU(),
        nn.Linear(64, 10)
    )
    passed = single_batch_overfit_test(model, in_features=32, num_classes=10, batch_size=16)

    # Test gradient clipping
    x = torch.randn(10, 32)
    y = torch.randint(0, 10, (10,))
    model.zero_grad()
    loss = nn.CrossEntropyLoss()(model(x), y) * 100.0 # Artificially inflate loss
    loss.backward()

    raw_norm = compute_global_gradient_norm(model)
    custom_clip_grad_norm(model, max_norm=1.0)
    clipped_norm = compute_global_gradient_norm(model)

    print(f"Debugging Demo: Single-Batch Overfit Passed = {passed}, Raw Norm = {raw_norm:.2f}, Clipped Norm = {clipped_norm:.2f}")
    return passed, raw_norm, clipped_norm

if __name__ == "__main__":
    run_debugging_demo()
