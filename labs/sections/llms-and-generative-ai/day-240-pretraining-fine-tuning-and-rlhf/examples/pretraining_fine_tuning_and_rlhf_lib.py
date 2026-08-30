import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple

def compute_bradley_terry_probability(reward_chosen: float, reward_rejected: float) -> float:
    # P(y_w > y_l) = 1 / (1 + exp(-(r_w - r_l))) = sigmoid(r_w - r_l)
    diff = reward_chosen - reward_rejected
    return float(1.0 / (1.0 + math.exp(-diff)))

def compute_dpo_loss(
    policy_chosen_logp: torch.Tensor,
    policy_rejected_logp: torch.Tensor,
    ref_chosen_logp: torch.Tensor,
    ref_rejected_logp: torch.Tensor,
    beta: float = 0.1
) -> Tuple[torch.Tensor, torch.Tensor]:
    pi_logratios = policy_chosen_logp - policy_rejected_logp
    ref_logratios = ref_chosen_logp - ref_rejected_logp

    logits = beta * (pi_logratios - ref_logratios)
    loss = -F.logsigmoid(logits).mean()

    # Implicit reward margin: beta * (log(pi_w/ref_w) - log(pi_l/ref_l))
    implicit_margin = (beta * (policy_chosen_logp - ref_chosen_logp) - 
                       beta * (policy_rejected_logp - ref_rejected_logp))

    return loss, implicit_margin

def run_alignment_demo():
    bt_prob = compute_bradley_terry_probability(2.4, -1.2)
    
    # Simulated sequence log-probabilities (batch of 2)
    pol_chosen = torch.tensor([-12.4, -10.2])
    pol_rejected = torch.tensor([-18.2, -16.5])
    ref_chosen = torch.tensor([-12.3, -10.1])
    ref_rejected = torch.tensor([-14.1, -13.0])

    loss, margin = compute_dpo_loss(pol_chosen, pol_rejected, ref_chosen, ref_rejected, beta=0.1)

    print(f"Alignment Demo: BT Prob = {bt_prob:.3f}, DPO Loss = {loss.item():.4f}, Mean Margin = {margin.mean().item():.4f}")
    return bt_prob, loss.item(), margin.mean().item()

if __name__ == "__main__":
    run_alignment_demo()
