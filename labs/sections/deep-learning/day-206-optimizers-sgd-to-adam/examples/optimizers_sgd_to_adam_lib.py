import torch
from torch.optim import Optimizer
from typing import Tuple, Dict, Any

class CustomAdamW(Optimizer):
    def __init__(self, params, lr: float = 1e-3, betas: Tuple[float, float] = (0.9, 0.999),
                 eps: float = 1e-8, weight_decay: float = 1e-2):
        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            lr = group['lr']
            beta1, beta2 = group['betas']
            eps = group['eps']
            wd = group['weight_decay']

            for p in group['params']:
                if p.grad is None:
                    continue
                grad = p.grad

                state = self.state[p]
                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    state['exp_avg_sq'] = torch.zeros_like(p, memory_format=torch.preserve_format)

                exp_avg = state['exp_avg']
                exp_avg_sq = state['exp_avg_sq']
                state['step'] += 1
                t = state['step']

                # Decoupled weight decay
                if wd != 0.0:
                    p.mul_(1.0 - lr * wd)

                # Update moments
                exp_avg.mul_(beta1).add_(grad, alpha=1.0 - beta1)
                exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1.0 - beta2)

                # Bias corrections
                bias_correction1 = 1.0 - (beta1 ** t)
                bias_correction2 = 1.0 - (beta2 ** t)
                step_size = lr / bias_correction1
                denom = (exp_avg_sq.sqrt() / (bias_correction2 ** 0.5)).add_(eps)

                p.addcdiv_(exp_avg, denom, value=-step_size)

        return loss

def optimize_rosenbrock(steps: int = 20) -> Tuple[float, float]:
    torch.manual_seed(42)
    # Rosenbrock function: f(x, y) = (1 - x)^2 + 100 * (y - x^2)^2
    param = torch.tensor([-1.0, 2.0], requires_grad=True)
    optimizer = CustomAdamW([param], lr=0.1, weight_decay=0.0)

    initial_loss = float(((1.0 - param[0])**2 + 100.0 * (param[1] - param[0]**2)**2).item())

    for _ in range(steps):
        optimizer.zero_grad()
        loss = (1.0 - param[0])**2 + 100.0 * (param[1] - param[0]**2)**2
        loss.backward()
        optimizer.step()

    final_loss = float(loss.item())
    print(f"Rosenbrock Demo: Initial Loss = {initial_loss:.4f}, Final Loss = {final_loss:.4f}")
    return initial_loss, final_loss

if __name__ == "__main__":
    optimize_rosenbrock()
