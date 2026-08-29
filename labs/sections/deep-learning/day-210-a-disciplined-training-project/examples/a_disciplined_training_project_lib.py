import os
import random
import numpy as np
import torch
import torch.nn as nn
from dataclasses import dataclass, asdict
from torch.utils.data import DataLoader
from typing import Dict, Any, Tuple, Optional

@dataclass
class TrainingConfig:
    in_features: int = 16
    hidden_dim: int = 32
    num_classes: int = 2
    learning_rate: float = 0.01
    batch_size: int = 16
    max_epochs: int = 20
    patience: int = 3
    min_delta: float = 1e-3
    seed: int = 42

def seed_everything(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

class EarlyStopping:
    def __init__(self, patience: int = 3, min_delta: float = 1e-3):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float("inf")
        self.early_stop = False
        self.best_state_dict = None

    def __call__(self, val_loss: float, model: nn.Module) -> bool:
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.best_state_dict = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            self.counter = 0
            return True
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
            return False

class PyTorchTrainer:
    def __init__(self, model: nn.Module, optimizer: torch.optim.Optimizer,
                 criterion: nn.Module, config: TrainingConfig):
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.config = config
        self.early_stopping = EarlyStopping(patience=config.patience, min_delta=config.min_delta)
        self.history = {"train_loss": [], "val_loss": [], "val_acc": []}

    def train_epoch(self, train_loader: DataLoader) -> float:
        self.model.train()
        total_loss = 0.0
        total_samples = 0
        for x, y in train_loader:
            self.optimizer.zero_grad()
            logits = self.model(x)
            loss = self.criterion(logits, y)
            loss.backward()
            self.optimizer.step()

            bs = x.size(0)
            total_loss += loss.item() * bs
            total_samples += bs
        return total_loss / max(total_samples, 1)

    def evaluate(self, val_loader: DataLoader) -> Tuple[float, float]:
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total_samples = 0
        with torch.no_grad():
            for x, y in val_loader:
                logits = self.model(x)
                loss = self.criterion(logits, y)
                bs = x.size(0)
                total_loss += loss.item() * bs
                preds = torch.argmax(logits, dim=1)
                correct += int((preds == y).sum().item())
                total_samples += bs
        val_loss = total_loss / max(total_samples, 1)
        val_acc = correct / max(total_samples, 1)
        return val_loss, val_acc

    def fit(self, train_loader: DataLoader, val_loader: DataLoader) -> Dict[str, Any]:
        for epoch in range(1, self.config.max_epochs + 1):
            t_loss = self.train_epoch(train_loader)
            v_loss, v_acc = self.evaluate(val_loader)

            self.history["train_loss"].append(t_loss)
            self.history["val_loss"].append(v_loss)
            self.history["val_acc"].append(v_acc)

            self.early_stopping(v_loss, self.model)
            if self.early_stopping.early_stop:
                if self.early_stopping.best_state_dict is not None:
                    self.model.load_state_dict(self.early_stopping.best_state_dict)
                break

        return self.history

def run_trainer_demo():
    seed_everything(42)
    config = TrainingConfig(in_features=8, hidden_dim=16, num_classes=2, max_epochs=10, patience=2)
    model = nn.Sequential(
        nn.Linear(config.in_features, config.hidden_dim),
        nn.ReLU(),
        nn.Linear(config.hidden_dim, config.num_classes)
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    criterion = nn.CrossEntropyLoss()

    trainer = PyTorchTrainer(model, optimizer, criterion, config)

    # Synthetic data loaders
    x_t, y_t = torch.randn(64, 8), torch.randint(0, 2, (64,))
    x_v, y_v = torch.randn(32, 8), torch.randint(0, 2, (32,))
    train_loader = DataLoader(list(zip(x_t, y_t)), batch_size=16)
    val_loader = DataLoader(list(zip(x_v, y_v)), batch_size=16)

    history = trainer.fit(train_loader, val_loader)
    stopped_early = trainer.early_stopping.early_stop
    best_loss = trainer.early_stopping.best_loss

    print(f"Trainer Demo: Stopped Early = {stopped_early}, Best Val Loss = {best_loss:.4f}")
    return stopped_early, best_loss

if __name__ == "__main__":
    run_trainer_demo()
