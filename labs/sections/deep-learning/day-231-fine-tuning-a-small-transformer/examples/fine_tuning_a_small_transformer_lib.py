import torch
import torch.nn as nn
from typing import List, Dict, Any

def create_llrd_parameter_groups(
    model: nn.Module,
    base_lr: float = 5e-5,
    decay_rate: float = 0.85,
    weight_decay: float = 0.01
) -> List[Dict[str, Any]]:
    no_decay = ["bias", "LayerNorm.weight", "layer_norm.weight"]
    optimizer_grouped_parameters = []

    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        
        is_no_decay = any(nd in name for nd in no_decay)
        wd = 0.0 if is_no_decay else weight_decay

        # Calculate layer-specific learning rate
        if "classifier" in name or "head" in name:
            lr = base_lr * 2.0
        elif "layer.1" in name or "layers.1" in name:
            lr = base_lr
        elif "layer.0" in name or "layers.0" in name:
            lr = base_lr * decay_rate
        else:
            lr = base_lr * (decay_rate ** 2)

        optimizer_grouped_parameters.append({
            "params": [param],
            "lr": lr,
            "weight_decay": wd,
            "name": name
        })

    return optimizer_grouped_parameters

class EarlyStopping:
    def __init__(self, patience: int = 2, min_delta: float = 0.0):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float('inf')
        self.counter = 0
        self.early_stop = False

    def __call__(self, val_loss: float) -> bool:
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        return self.early_stop

def run_finetune_demo():
    model = nn.Sequential(
        nn.Linear(16, 16),
        nn.LayerNorm(16),
        nn.Linear(16, 2)
    )
    groups = create_llrd_parameter_groups(model, base_lr=5e-5)
    print(f"FineTune Demo: Created {len(groups)} Parameter Groups")
    return groups

if __name__ == "__main__":
    run_finetune_demo()
