import torch
import torch.nn as nn
from typing import Tuple, Dict, Any, List

class SimpleBackbone(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(16)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(32)
        self.gap = nn.AdaptiveAvgPool2d((1, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.gap(x)
        return torch.flatten(x, 1)

class TransferVisionModel(nn.Module):
    def __init__(self, num_classes: int = 5, freeze_backbone: bool = True):
        super().__init__()
        self.backbone = SimpleBackbone()
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False

        self.fc = nn.Sequential(
            nn.Linear(32, 16),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(16, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.backbone(x)
        return self.fc(feat)

def build_transfer_learning_model(num_classes: int = 5, freeze_backbone: bool = True) -> nn.Module:
    return TransferVisionModel(num_classes=num_classes, freeze_backbone=freeze_backbone)

def configure_differential_optimizer(model: TransferVisionModel, head_lr: float = 1e-3,
                                     backbone_lr: float = 1e-5) -> torch.optim.Optimizer:
    optimizer = torch.optim.AdamW([
        {"params": [p for p in model.backbone.parameters() if p.requires_grad], "lr": backbone_lr},
        {"params": model.fc.parameters(), "lr": head_lr}
    ], weight_decay=1e-2)
    return optimizer

def run_transfer_demo():
    torch.manual_seed(42)
    model = build_transfer_learning_model(num_classes=5, freeze_backbone=True)
    x = torch.randn(2, 3, 32, 32)
    out = model(x)

    frozen_params = sum(p.numel() for p in model.backbone.parameters() if not p.requires_grad)
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print(f"Transfer Demo: Out = {out.shape}, Frozen = {frozen_params}, Trainable = {trainable_params}")
    return out.shape, frozen_params, trainable_params

if __name__ == "__main__":
    run_transfer_demo()
