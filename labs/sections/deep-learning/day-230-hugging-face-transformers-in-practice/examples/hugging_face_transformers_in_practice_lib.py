import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Any

class MockDataCollatorWithPadding:
    def __init__(self, pad_token_id: int = 0):
        self.pad_token_id = pad_token_id

    def __call__(self, batch: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        max_len = max(len(item["input_ids"]) for item in batch)
        
        batch_input_ids = []
        batch_attention_mask = []
        batch_labels = []

        for item in batch:
            ids = item["input_ids"]
            pad_len = max_len - len(ids)
            
            padded_ids = ids + [self.pad_token_id] * pad_len
            attn_mask = [1] * len(ids) + [0] * pad_len
            
            batch_input_ids.append(padded_ids)
            batch_attention_mask.append(attn_mask)
            if "label" in item:
                batch_labels.append(item["label"])

        res = {
            "input_ids": torch.tensor(batch_input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(batch_attention_mask, dtype=torch.long)
        }
        if batch_labels:
            res["labels"] = torch.tensor(batch_labels, dtype=torch.long)
        return res

def compute_classification_metrics(predictions: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
    accuracy = float(np.mean(predictions == labels))
    tp = float(np.sum((predictions == 1) & (labels == 1)))
    fp = float(np.sum((predictions == 1) & (labels == 0)))
    fn = float(np.sum((predictions == 0) & (labels == 1)))

    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-8)

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }

def run_hf_demo():
    collator = MockDataCollatorWithPadding(pad_token_id=0)
    sample_batch = [
        {"input_ids": [101, 2054, 102], "label": 1},
        {"input_ids": [101, 1037, 3899, 2003, 102], "label": 0}
    ]
    batch = collator(sample_batch)
    print(f"HF Demo: Collated Batch Shape = {batch['input_ids'].shape}")
    return batch

if __name__ == "__main__":
    run_hf_demo()
