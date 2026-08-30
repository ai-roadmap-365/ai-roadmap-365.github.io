import torch
import numpy as np
from typing import Tuple, Dict, Any

def apply_mixup(x: torch.Tensor, y_one_hot: torch.Tensor, alpha: float = 0.2) -> Tuple[torch.Tensor, torch.Tensor]:
    batch_size = x.size(0)
    if alpha > 0:
        lam = float(np.random.beta(alpha, alpha))
    else:
        lam = 1.0

    index = torch.randperm(batch_size)
    mixed_x = lam * x + (1 - lam) * x[index]
    mixed_y = lam * y_one_hot + (1 - lam) * y_one_hot[index]
    return mixed_x, mixed_y

def rand_bbox(size, lam):
    W = size[2]
    H = size[3]
    cut_rat = np.sqrt(1.0 - lam)
    cut_w = int(W * cut_rat)
    cut_h = int(H * cut_rat)

    cx = np.random.randint(W)
    cy = np.random.randint(H)

    bbx1 = np.clip(cx - cut_w // 2, 0, W)
    bby1 = np.clip(cy - cut_h // 2, 0, H)
    bbx2 = np.clip(cx + cut_w // 2, 0, W)
    bby2 = np.clip(cy + cut_h // 2, 0, H)

    return bbx1, bby1, bbx2, bby2

def apply_cutmix(x: torch.Tensor, y_one_hot: torch.Tensor, alpha: float = 1.0) -> Tuple[torch.Tensor, torch.Tensor]:
    batch_size = x.size(0)
    if alpha > 0:
        lam = float(np.random.beta(alpha, alpha))
    else:
        lam = 1.0

    index = torch.randperm(batch_size)
    bbx1, bby1, bbx2, bby2 = rand_bbox(x.size(), lam)

    mixed_x = x.clone()
    mixed_x[:, :, bbx1:bbx2, bby1:bby2] = x[index, :, bbx1:bbx2, bby1:bby2]

    # Adjust lambda to exact area ratio
    actual_lam = 1.0 - ((bbx2 - bbx1) * (bby2 - bby1) / (x.size(2) * x.size(3)))
    mixed_y = actual_lam * y_one_hot + (1.0 - actual_lam) * y_one_hot[index]

    return mixed_x, mixed_y

def run_augmentation_demo():
    torch.manual_seed(42)
    np.random.seed(42)

    x = torch.randn(4, 3, 32, 32)
    y_idx = torch.tensor([0, 1, 2, 3])
    y_one_hot = torch.nn.functional.one_hot(y_idx, num_classes=4).float()

    x_mix, y_mix = apply_mixup(x, y_one_hot, alpha=0.2)
    x_cut, y_cut = apply_cutmix(x, y_one_hot, alpha=1.0)

    print(f"Augmentation Demo: MixUp Shape = {x_mix.shape}, CutMix Shape = {x_cut.shape}")
    return x_mix.shape, x_cut.shape

if __name__ == "__main__":
    run_augmentation_demo()
