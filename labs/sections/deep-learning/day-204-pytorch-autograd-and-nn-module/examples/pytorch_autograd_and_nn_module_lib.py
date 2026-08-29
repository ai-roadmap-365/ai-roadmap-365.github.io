import torch
import torch.nn as nn
from typing import Tuple, Dict, Any

class DeepClassifier(nn.Module):
    def __init__(self, in_features: int = 784, hidden_dim: int = 128, num_classes: int = 10):
        super().__init__()
        self.fc1 = nn.Linear(in_features, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.relu(self.fc1(x))
        out = self.fc2(h)
        return out

def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def train_step(model: nn.Module, optimizer: torch.optim.Optimizer, criterion: nn.Module,
               x: torch.Tensor, y: torch.Tensor) -> float:
    model.train()
    optimizer.zero_grad()
    logits = model(x)
    loss = criterion(logits, y)
    loss.backward()
    optimizer.step()
    return float(loss.item())

def evaluate_model(model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> Tuple[float, float]:
    model.eval()
    with torch.no_grad():
        logits = model(x)
        criterion = nn.CrossEntropyLoss()
        loss = float(criterion(logits, y).item())
        preds = torch.argmax(logits, dim=1)
        acc = float((preds == y).float().mean().item())
    return loss, acc

def run_autograd_demo():
    torch.manual_seed(42)
    model = DeepClassifier(in_features=784, hidden_dim=128, num_classes=10)
    num_params = count_parameters(model)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1, momentum=0.9)

    x = torch.randn(32, 784)
    y = torch.randint(0, 10, (32,))

    initial_loss = train_step(model, optimizer, criterion, x, y)
    for _ in range(10):
        final_loss = train_step(model, optimizer, criterion, x, y)

    print(f"DeepClassifier Params: {num_params}, Initial Loss: {initial_loss:.4f}, Final Loss: {final_loss:.4f}")
    return model, initial_loss, final_loss

if __name__ == "__main__":
    run_autograd_demo()
