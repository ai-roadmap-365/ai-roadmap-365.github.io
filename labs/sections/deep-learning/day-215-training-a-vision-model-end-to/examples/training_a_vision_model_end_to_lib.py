import torch
import torch.nn as nn
from typing import Tuple, Dict, Any, List

def calculate_topk_accuracy(logits: torch.Tensor, targets: torch.Tensor, k: int = 5) -> float:
    with torch.no_grad():
        k = min(k, logits.size(1))
        _, pred = logits.topk(k, dim=1, largest=True, sorted=True)
        correct = pred.eq(targets.view(-1, 1).expand_as(pred))
        topk_correct = float(correct.sum().item())
        return topk_correct / float(targets.size(0))

def compute_confusion_matrix(preds: torch.Tensor, targets: torch.Tensor, num_classes: int) -> torch.Tensor:
    with torch.no_grad():
        cm = torch.zeros(num_classes, num_classes, dtype=torch.float32)
        for p, t in zip(preds, targets):
            cm[t.item(), p.item()] += 1.0

        # Row normalize
        row_sums = cm.sum(dim=1, keepdim=True)
        row_sums[row_sums == 0] = 1.0
        cm_norm = cm / row_sums
        return cm_norm

def run_vision_training_demo():
    torch.manual_seed(42)
    logits = torch.tensor([
        [2.5, 0.1, 0.3, 0.8, 0.2],
        [0.1, 3.2, 0.4, 0.5, 0.2],
        [0.2, 0.3, 1.1, 2.8, 0.5],
        [0.1, 0.2, 0.3, 0.4, 4.0]
    ])
    targets = torch.tensor([0, 1, 3, 4])

    top1 = calculate_topk_accuracy(logits, targets, k=1)
    top3 = calculate_topk_accuracy(logits, targets, k=3)
    preds = torch.argmax(logits, dim=1)
    cm = compute_confusion_matrix(preds, targets, num_classes=5)

    print(f"Training Demo: Top-1 = {top1:.2f}, Top-3 = {top3:.2f}, CM Diag = {torch.diag(cm).tolist()}")
    return top1, top3, cm

if __name__ == "__main__":
    run_vision_training_demo()
