import pytest
import torch
from examples.training_a_vision_model_end_to_lib import calculate_topk_accuracy, compute_confusion_matrix

def test_topk_accuracy_top1():
    logits = torch.tensor([
        [5.0, 1.0, 0.0],
        [0.0, 5.0, 1.0],
        [1.0, 0.0, 5.0],
        [5.0, 1.0, 0.0]
    ])
    targets = torch.tensor([0, 1, 2, 1]) # Last sample is incorrect (pred 0, true 1)

    top1 = calculate_topk_accuracy(logits, targets, k=1)
    assert top1 == 0.75

def test_topk_accuracy_top2():
    logits = torch.tensor([
        [5.0, 1.0, 0.0],
        [0.0, 5.0, 1.0],
        [1.0, 0.0, 5.0],
        [5.0, 4.0, 0.0]  # Sample 4: rank1=0, rank2=1. True is 1 -> included in Top-2!
    ])
    targets = torch.tensor([0, 1, 2, 1])

    top2 = calculate_topk_accuracy(logits, targets, k=2)
    assert top2 == 1.0

def test_confusion_matrix_diagonal_perfect():
    preds = torch.tensor([0, 1, 2, 0, 1, 2])
    targets = torch.tensor([0, 1, 2, 0, 1, 2])

    cm = compute_confusion_matrix(preds, targets, num_classes=3)
    # Diagonal should all be 1.0
    for i in range(3):
        assert cm[i, i] == 1.0
