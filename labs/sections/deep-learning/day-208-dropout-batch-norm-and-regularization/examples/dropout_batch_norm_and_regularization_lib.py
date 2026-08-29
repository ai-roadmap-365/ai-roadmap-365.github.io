import torch
import torch.nn as nn
from typing import Tuple, Dict, Any

class CustomDropout(nn.Module):
    def __init__(self, p: float = 0.5):
        super().__init__()
        self.p = p

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not self.training or self.p == 0.0:
            return x
        # Inverted dropout: sample Bernoulli mask and scale by 1 / (1 - p)
        mask = (torch.rand_like(x) > self.p).float()
        return (x * mask) / (1.0 - self.p)

class CustomBatchNorm1d(nn.Module):
    def __init__(self, num_features: int, eps: float = 1e-5, momentum: float = 0.1):
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum

        self.gamma = nn.Parameter(torch.ones(num_features))
        self.beta = nn.Parameter(torch.zeros(num_features))

        self.register_buffer('running_mean', torch.zeros(num_features))
        self.register_buffer('running_var', torch.ones(num_features))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.training:
            mean = x.mean(dim=0)
            var = x.var(dim=0, unbiased=False)

            # Update running stats
            with torch.no_grad():
                self.running_mean = (1.0 - self.momentum) * self.running_mean + self.momentum * mean
                self.running_var = (1.0 - self.momentum) * self.running_var + self.momentum * var

            x_hat = (x - mean) / torch.sqrt(var + self.eps)
        else:
            x_hat = (x - self.running_mean) / torch.sqrt(self.running_var + self.eps)

        return self.gamma * x_hat + self.beta

class RegularizedMLP(nn.Module):
    def __init__(self, in_features: int = 784, hidden_dim: int = 128, num_classes: int = 10, p: float = 0.5):
        super().__init__()
        self.fc1 = nn.Linear(in_features, hidden_dim)
        self.bn1 = CustomBatchNorm1d(hidden_dim)
        self.relu = nn.ReLU()
        self.drop = CustomDropout(p=p)
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.drop(self.relu(self.bn1(self.fc1(x))))
        return self.fc2(h)

def run_regularization_demo():
    torch.manual_seed(42)
    model = RegularizedMLP(in_features=32, hidden_dim=16, num_classes=2, p=0.5)
    x = torch.randn(10, 32)

    model.train()
    out1 = model(x)
    out2 = model(x)
    is_stochastic = not torch.equal(out1, out2)

    model.eval()
    with torch.no_grad():
        out3 = model(x)
        out4 = model(x)
    is_deterministic = torch.equal(out3, out4)

    print(f"Regularization Demo: Training Stochastic = {is_stochastic}, Eval Deterministic = {is_deterministic}")
    return is_stochastic, is_deterministic

if __name__ == "__main__":
    run_regularization_demo()
