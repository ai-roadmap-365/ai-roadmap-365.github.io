import pytest
import torch
from examples.beyond_classification_detection_and_segmentation_lib import calculate_iou, apply_nms, calculate_dice_loss

def test_calculate_iou_exact():
    box1 = torch.tensor([0.0, 0.0, 10.0, 10.0])
    box2 = torch.tensor([0.0, 0.0, 10.0, 10.0])
    assert calculate_iou(box1, box2) == 1.0

def test_calculate_iou_disjoint():
    box1 = torch.tensor([0.0, 0.0, 10.0, 10.0])
    box2 = torch.tensor([20.0, 20.0, 30.0, 30.0])
    assert calculate_iou(box1, box2) == 0.0

def test_apply_nms_suppression():
    boxes = torch.tensor([
        [0.0, 0.0, 10.0, 10.0],
        [1.0, 1.0, 10.0, 10.0], # Overlapping duplicate
        [50.0, 50.0, 60.0, 60.0] # Separate object
    ])
    scores = torch.tensor([0.95, 0.80, 0.88])
    keep = apply_nms(boxes, scores, iou_threshold=0.5)

    assert keep.tolist() == [0, 2]

def test_dice_loss_perfect():
    mask = torch.ones(2, 16, 16)
    loss = calculate_dice_loss(mask, mask)
    assert abs(loss) < 1e-4
