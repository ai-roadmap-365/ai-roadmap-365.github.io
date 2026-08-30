import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

def quantize_symmetric_int8(tensor: torch.Tensor) -> Tuple[torch.Tensor, float]:
    alpha = tensor.abs().max().item()
    scale = alpha / 127.0 if alpha > 0 else 1.0
    q_tensor = torch.clamp(torch.round(tensor / scale), -127, 127).to(torch.int8)
    return q_tensor, scale

def dequantize_symmetric_int8(q_tensor: torch.Tensor, scale: float) -> torch.Tensor:
    return q_tensor.to(torch.float32) * scale

class KnowledgeDistillationLoss(nn.Module):
    def __init__(self, temperature: float = 4.0, alpha: float = 0.7):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.kl_div = nn.KLDivLoss(reduction="batchmean")
        self.ce_loss = nn.CrossEntropyLoss()

    def forward(self, student_logits: torch.Tensor, teacher_logits: torch.Tensor,
                targets: torch.Tensor) -> torch.Tensor:
        tau = self.temperature
        soft_student = F.log_softmax(student_logits / tau, dim=-1)
        soft_teacher = F.softmax(teacher_logits / tau, dim=-1)

        soft_loss = self.kl_div(soft_student, soft_teacher) * (tau ** 2)
        hard_loss = self.ce_loss(student_logits, targets)

        return self.alpha * soft_loss + (1.0 - self.alpha) * hard_loss

def run_compression_demo():
    x = torch.tensor([-2.54, 0.0, 1.27, 2.54], dtype=torch.float32)
    q, s = quantize_symmetric_int8(x)
    x_hat = dequantize_symmetric_int8(q, s)

    kd = KnowledgeDistillationLoss(temperature=4.0, alpha=0.7)
    s_log = torch.randn(2, 4)
    t_log = torch.randn(2, 4)
    y = torch.tensor([0, 2])
    loss = kd(s_log, t_log, y)

    print(f"Quantization Demo: Scale = {s:.4f}, Quantized = {q.tolist()}, KD Loss = {loss.item():.4f}")
    return q, loss.item()

if __name__ == "__main__":
    run_compression_demo()
