import torch
import torch.nn as nn
from typing import Tuple, Dict, Any, List

def calculate_iou(box_a: torch.Tensor, box_b: torch.Tensor) -> float:
    # Box format: [x1, y1, x2, y2]
    x1 = max(float(box_a[0]), float(box_b[0]))
    y1 = max(float(box_a[1]), float(box_b[1]))
    x2 = min(float(box_a[2]), float(box_b[2]))
    y2 = min(float(box_a[3]), float(box_b[3]))

    inter_w = max(0.0, x2 - x1)
    inter_h = max(0.0, y2 - y1)
    inter_area = inter_w * inter_h

    area_a = max(0.0, float(box_a[2] - box_a[0])) * max(0.0, float(box_a[3] - box_a[1]))
    area_b = max(0.0, float(box_b[2] - box_b[0])) * max(0.0, float(box_b[3] - box_b[1]))

    union_area = area_a + area_b - inter_area
    if union_area == 0.0:
        return 0.0
    return inter_area / union_area

def apply_nms(boxes: torch.Tensor, scores: torch.Tensor, iou_threshold: float = 0.5) -> torch.Tensor:
    # boxes: (N, 4) in [x1, y1, x2, y2], scores: (N,)
    if boxes.size(0) == 0:
        return torch.empty(0, dtype=torch.long)

    order = torch.argsort(scores, descending=True)
    keep = []

    while order.numel() > 0:
        i = order[0].item()
        keep.append(i)

        if order.numel() == 1:
            break

        # Compute IoU of the picked box with all remaining boxes
        remaining_indices = order[1:]
        ious = torch.tensor([
            calculate_iou(boxes[i], boxes[j]) for j in remaining_indices
        ])

        # Keep boxes with IoU <= threshold
        mask = ious <= iou_threshold
        order = remaining_indices[mask]

    return torch.tensor(keep, dtype=torch.long)

def calculate_dice_loss(pred_probs: torch.Tensor, targets: torch.Tensor, eps: float = 1e-6) -> float:
    # pred_probs: (N, H, W) in [0, 1], targets: (N, H, W) binary
    intersection = (pred_probs * targets).sum()
    cardinality = pred_probs.sum() + targets.sum()
    dice_score = (2.0 * intersection + eps) / (cardinality + eps)
    return float(1.0 - dice_score)

def run_dense_vision_demo():
    box1 = torch.tensor([0.0, 0.0, 10.0, 10.0])
    box2 = torch.tensor([5.0, 0.0, 15.0, 10.0]) # 50% overlap

    iou = calculate_iou(box1, box2)

    boxes = torch.tensor([
        [0.0, 0.0, 10.0, 10.0],
        [1.0, 1.0, 10.0, 10.0], # High overlap duplicate
        [20.0, 20.0, 30.0, 30.0] # Separate object
    ])
    scores = torch.tensor([0.9, 0.7, 0.85])
    keep = apply_nms(boxes, scores, iou_threshold=0.5)

    print(f"Dense Vision Demo: IoU = {iou:.4f}, NMS Kept Indices = {keep.tolist()}")
    return iou, keep

if __name__ == "__main__":
    run_dense_vision_demo()
