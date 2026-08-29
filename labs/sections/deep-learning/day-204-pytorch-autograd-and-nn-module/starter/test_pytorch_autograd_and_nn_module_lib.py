import pytest
import torch
import torch.nn as nn
from examples.pytorch_autograd_and_nn_module_lib import DeepClassifier, count_parameters, train_step, evaluate_model

def test_deep_classifier_structure_and_parameters():
    model = DeepClassifier(in_features=784, hidden_dim=128, num_classes=10)
    assert count_parameters(model) == 101770
    assert isinstance(model.fc1, nn.Linear)
    assert isinstance(model.fc2, nn.Linear)

def test_forward_pass_output_shape():
    model = DeepClassifier(in_features=784, hidden_dim=128, num_classes=10)
    x = torch.randn(16, 784)
    out = model(x)
    assert out.shape == (16, 10)
    assert out.grad_fn is not None

def test_training_step_reduces_loss():
    torch.manual_seed(42)
    model = DeepClassifier(in_features=32, hidden_dim=16, num_classes=4)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    criterion = nn.CrossEntropyLoss()

    x = torch.randn(20, 32)
    y = torch.randint(0, 4, (20,))

    loss_start = train_step(model, optimizer, criterion, x, y)
    for _ in range(15):
        loss_end = train_step(model, optimizer, criterion, x, y)

    assert loss_end < loss_start

def test_state_dict_serialization():
    model1 = DeepClassifier(in_features=10, hidden_dim=8, num_classes=2)
    sd = model1.state_dict()
    assert 'fc1.weight' in sd
    assert 'fc2.bias' in sd

    model2 = DeepClassifier(in_features=10, hidden_dim=8, num_classes=2)
    model2.load_state_dict(sd)
    assert torch.equal(model1.fc1.weight, model2.fc1.weight)
