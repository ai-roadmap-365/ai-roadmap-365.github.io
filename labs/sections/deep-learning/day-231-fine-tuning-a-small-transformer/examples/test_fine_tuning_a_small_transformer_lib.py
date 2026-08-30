import pytest
import torch
import torch.nn as nn
from examples.fine_tuning_a_small_transformer_lib import create_llrd_parameter_groups, EarlyStopping

def test_llrd_parameter_groups():
    model = nn.Sequential(
        nn.Linear(8, 8),
        nn.LayerNorm(8),
        nn.Linear(8, 2)
    )
    groups = create_llrd_parameter_groups(model, base_lr=1e-4)
    assert len(groups) > 0
    # Check that biases have zero weight decay
    for g in groups:
        if "bias" in g["name"]:
            assert g["weight_decay"] == 0.0

def test_early_stopping():
    stopper = EarlyStopping(patience=2)
    assert not stopper(1.0)
    assert not stopper(1.1)
    assert stopper(1.2) # Patience reached
