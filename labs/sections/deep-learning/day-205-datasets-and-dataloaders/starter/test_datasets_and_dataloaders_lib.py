import pytest
import torch
from examples.datasets_and_dataloaders_lib import RaggedSequenceDataset, dynamic_padding_collate, DataLoader

def test_ragged_dataset_len_and_getitem():
    ds = RaggedSequenceDataset(num_samples=50, min_len=4, max_len=15)
    assert len(ds) == 50
    seq, label = ds[0]
    assert isinstance(seq, torch.Tensor)
    assert isinstance(label, int)
    assert 4 <= len(seq) <= 15
    assert label in (0, 1)

def test_dynamic_padding_collate_function():
    batch = [
        (torch.tensor([1.0, 2.0, 3.0]), 0),
        (torch.tensor([4.0, 5.0]), 1),
        (torch.tensor([6.0, 7.0, 8.0, 9.0]), 0),
    ]
    collated = dynamic_padding_collate(batch)
    assert collated["inputs"].shape == (3, 4)
    assert collated["mask"].shape == (3, 4)
    assert collated["labels"].shape == (3,)
    # Verify padding positions are zero
    assert collated["inputs"][1, 2] == 0.0
    assert collated["mask"][1, 2] == 0.0
    assert collated["mask"][2, 3] == 1.0

def test_dataloader_iteration_and_batching():
    ds = RaggedSequenceDataset(num_samples=64, min_len=5, max_len=10)
    loader = DataLoader(ds, batch_size=16, shuffle=False, collate_fn=dynamic_padding_collate)
    batches = list(loader)
    assert len(batches) == 4
    for b in batches:
        assert b["inputs"].shape[0] == 16
        assert b["mask"].shape[0] == 16
        assert b["labels"].shape[0] == 16

def test_dataloader_drop_last():
    ds = RaggedSequenceDataset(num_samples=35, min_len=5, max_len=10)
    loader_drop = DataLoader(ds, batch_size=16, drop_last=True, collate_fn=dynamic_padding_collate)
    assert len(list(loader_drop)) == 2
