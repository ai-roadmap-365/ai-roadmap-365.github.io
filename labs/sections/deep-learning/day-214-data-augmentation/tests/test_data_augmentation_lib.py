import pytest
import torch
from examples.data_augmentation_lib import apply_mixup, apply_cutmix

def test_mixup_convex_combination():
    x = torch.ones(4, 3, 16, 16)
    y_one_hot = torch.eye(4)

    x_mix, y_mix = apply_mixup(x, y_one_hot, alpha=0.5)

    assert x_mix.shape == (4, 3, 16, 16)
    assert y_mix.shape == (4, 4)
    # Every row in y_mix must sum to 1.0
    for row in y_mix:
        assert torch.isclose(torch.sum(row), torch.tensor(1.0), atol=1e-5)

def test_cutmix_bounding_box_patch():
    x = torch.zeros(4, 3, 16, 16)
    x[0] = 1.0 # Sample 0 is all 1s
    y_one_hot = torch.eye(4)

    x_cut, y_cut = apply_cutmix(x, y_one_hot, alpha=1.0)

    assert x_cut.shape == (4, 3, 16, 16)
    assert y_cut.shape == (4, 4)
    for row in y_cut:
        assert torch.isclose(torch.sum(row), torch.tensor(1.0), atol=1e-5)
