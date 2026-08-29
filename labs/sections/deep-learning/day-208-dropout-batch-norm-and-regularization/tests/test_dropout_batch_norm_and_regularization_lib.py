import pytest
import torch
from examples.dropout_batch_norm_and_regularization_lib import CustomDropout, CustomBatchNorm1d, RegularizedMLP

def test_custom_dropout_training_vs_eval():
    drop = CustomDropout(p=0.5)
    x = torch.ones(100, 100)

    drop.train()
    out_train = drop(x)
    # Check that approx 50% are zero and surviving elements are 2.0
    zero_ratio = (out_train == 0.0).float().mean().item()
    assert 0.40 <= zero_ratio <= 0.60
    assert torch.isclose(out_train.mean(), torch.tensor(1.0), atol=0.1)

    drop.eval()
    out_eval = drop(x)
    assert torch.equal(out_eval, x)

def test_custom_batchnorm_train_eval_statistics():
    bn = CustomBatchNorm1d(num_features=4, momentum=0.5)
    x = torch.tensor([[1.0, 2.0, 3.0, 4.0],
                      [5.0, 6.0, 7.0, 8.0]])

    bn.train()
    out_train = bn(x)
    assert out_train.shape == (2, 4)
    # Output should have approximately zero mean along batch dim
    assert torch.allclose(out_train.mean(dim=0), torch.zeros(4), atol=1e-4)

    # Check that running stats were updated
    assert not torch.equal(bn.running_mean, torch.zeros(4))

    # In eval mode, running stats should be used
    bn.eval()
    out_eval = bn(x)
    assert out_eval.shape == (2, 4)

def test_regularized_mlp_forward_modes():
    model = RegularizedMLP(in_features=20, hidden_dim=10, num_classes=2, p=0.5)
    x = torch.randn(8, 20)

    model.train()
    y1 = model(x)
    y2 = model(x)
    assert not torch.equal(y1, y2)

    model.eval()
    with torch.no_grad():
        y3 = model(x)
        y4 = model(x)
    assert torch.equal(y3, y4)
