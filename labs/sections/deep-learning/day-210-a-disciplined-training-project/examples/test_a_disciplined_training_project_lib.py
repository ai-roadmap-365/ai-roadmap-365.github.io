import pytest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from examples.a_disciplined_training_project_lib import (
    TrainingConfig, seed_everything, EarlyStopping, PyTorchTrainer
)

def test_seed_everything_deterministic():
    seed_everything(42)
    t1 = torch.randn(10)
    seed_everything(42)
    t2 = torch.randn(10)
    assert torch.equal(t1, t2)

def test_early_stopping_patience_and_restore():
    model = nn.Linear(4, 2)
    stopper = EarlyStopping(patience=2, min_delta=1e-3)

    assert stopper(1.0, model) == True # Best: 1.0
    assert stopper.counter == 0

    assert stopper(0.95, model) == True # Best: 0.95
    assert stopper.counter == 0

    assert stopper(0.96, model) == False # Worse (count 1)
    assert stopper.counter == 1
    assert stopper.early_stop == False

    assert stopper(0.97, model) == False # Worse (count 2 -> early stop!)
    assert stopper.counter == 2
    assert stopper.early_stop == True

def test_pytorch_trainer_fit_and_metrics():
    seed_everything(42)
    config = TrainingConfig(in_features=4, hidden_dim=8, num_classes=2, max_epochs=5, patience=3)
    model = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 2))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()

    trainer = PyTorchTrainer(model, optimizer, criterion, config)

    x = torch.randn(32, 4)
    y = torch.randint(0, 2, (32,))
    train_loader = DataLoader(list(zip(x, y)), batch_size=8)
    val_loader = DataLoader(list(zip(x, y)), batch_size=8)

    history = trainer.fit(train_loader, val_loader)
    assert len(history["train_loss"]) > 0
    assert len(history["val_loss"]) == len(history["train_loss"])
    assert len(history["val_acc"]) == len(history["train_loss"])
