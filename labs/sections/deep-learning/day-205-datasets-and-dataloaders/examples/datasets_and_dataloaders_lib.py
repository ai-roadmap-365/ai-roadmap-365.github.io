import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple, Dict, Any

class RaggedSequenceDataset(Dataset):
    def __init__(self, num_samples: int = 200, min_len: int = 5, max_len: int = 25):
        super().__init__()
        self.num_samples = num_samples
        torch.manual_seed(42)
        self.samples = [
            (torch.randint(1, 100, (torch.randint(min_len, max_len + 1, (1,)).item(),)).float(),
             torch.randint(0, 2, (1,)).item())
            for _ in range(num_samples)
        ]

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        return self.samples[idx]

def dynamic_padding_collate(batch: List[Tuple[torch.Tensor, int]]) -> Dict[str, torch.Tensor]:
    sequences = [item[0] for item in batch]
    labels = torch.tensor([item[1] for item in batch], dtype=torch.long)
    lengths = torch.tensor([len(s) for s in sequences], dtype=torch.long)

    max_len = int(lengths.max().item())
    batch_size = len(batch)

    padded_inputs = torch.zeros(batch_size, max_len, dtype=torch.float32)
    attention_mask = torch.zeros(batch_size, max_len, dtype=torch.float32)

    for i, seq in enumerate(sequences):
        seq_len = len(seq)
        padded_inputs[i, :seq_len] = seq
        attention_mask[i, :seq_len] = 1.0

    return {
        "inputs": padded_inputs,
        "mask": attention_mask,
        "lengths": lengths,
        "labels": labels
    }

def run_dataloader_demo():
    dataset = RaggedSequenceDataset(num_samples=100, min_len=5, max_len=20)
    loader = DataLoader(
        dataset=dataset,
        batch_size=16,
        shuffle=True,
        collate_fn=dynamic_padding_collate,
        drop_last=True
    )

    batch_count = 0
    sample_count = 0
    first_shape = None

    for batch in loader:
        if batch_count == 0:
            first_shape = tuple(batch["inputs"].shape)
        batch_count += 1
        sample_count += len(batch["labels"])

    print(f"DataLoader Demo: Processed {sample_count} samples across {batch_count} batches. Batch 0 Shape: {first_shape}")
    return batch_count, sample_count, first_shape

if __name__ == "__main__":
    run_dataloader_demo()
