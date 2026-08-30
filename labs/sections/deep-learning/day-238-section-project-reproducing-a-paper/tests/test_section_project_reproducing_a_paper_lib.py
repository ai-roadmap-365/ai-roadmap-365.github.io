import pytest
import torch
from examples.section_project_reproducing_a_paper_lib import (
    ConfigurableTransformer,
    run_single_batch_overfit,
    calculate_multi_seed_aggregate
)

def test_configurable_transformer_forward():
    model_pre = ConfigurableTransformer(use_pre_ln=True)
    model_post = ConfigurableTransformer(use_pre_ln=False)
    x = torch.randint(0, 100, (4, 16))

    out_pre = model_pre(x)
    out_post = model_post(x)
    assert out_pre.shape == (4, 2)
    assert out_post.shape == (4, 2)

def test_single_batch_overfit():
    torch.manual_seed(42)
    model = ConfigurableTransformer(embed_dim=32, num_classes=2, use_pre_ln=True)
    passed = run_single_batch_overfit(model, steps=60)
    assert passed is True

def test_multi_seed_aggregate_metrics():
    res = calculate_multi_seed_aggregate([0.90, 0.92, 0.94])
    assert res["mean"] == 0.92
    assert res["min"] == 0.90
    assert res["max"] == 0.94
