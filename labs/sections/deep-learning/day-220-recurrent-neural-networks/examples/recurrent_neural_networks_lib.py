import torch
import torch.nn as nn
import math
from typing import Tuple

class SimpleRNNModel(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, num_classes: int):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.W_xh = nn.Linear(input_dim, hidden_dim)
        self.W_hh = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.W_hy = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (Batch, Seq_Len, input_dim)
        batch_size, seq_len, _ = x.size()
        h_t = torch.zeros(batch_size, self.hidden_dim, device=x.device)

        for t in range(seq_len):
            x_t = x[:, t, :]
            h_t = torch.tanh(self.W_xh(x_t) + self.W_hh(h_t))

        logits = self.W_hy(h_t)
        return logits

def clip_gradient_norm(parameters, max_norm: float = 1.0) -> float:
    params = [p for p in parameters if p.grad is not None]
    if not params:
        return 0.0
    total_norm = torch.norm(torch.stack([torch.norm(p.grad.detach(), 2) for p in params]), 2).item()
    clip_coef = max_norm / (total_norm + 1e-6)
    if clip_coef < 1.0:
        for p in params:
            p.grad.detach().mul_(clip_coef)
    return total_norm

def run_rnn_demo():
    torch.manual_seed(42)
    model = SimpleRNNModel(input_dim=4, hidden_dim=8, num_classes=2)
    x = torch.randn(2, 5, 4) # Batch=2, Seq=5, Dim=4
    logits = model(x)
    
    loss = logits.sum()
    loss.backward()
    norm = clip_gradient_norm(model.parameters(), max_norm=1.0)

    print(f"RNN Demo: Logits Shape = {logits.shape}, Grad Norm = {norm:.4f}")
    return logits.shape, norm

if __name__ == "__main__":
    run_rnn_demo()
