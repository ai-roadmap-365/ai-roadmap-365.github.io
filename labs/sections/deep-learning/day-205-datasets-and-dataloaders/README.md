# Lab: Day 205 -- Datasets and DataLoaders

## Lesson
Day number: 205 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Datasets and DataLoaders in PyTorch.

## Purpose
Build and test high-throughput PyTorch data loading pipelines. Subclass `torch.utils.data.Dataset`, implement custom `collate_fn` functions for dynamic sequence padding, configure `DataLoader` parameters, and evaluate batching throughput.

## Learning objectives
- Subclass `torch.utils.data.Dataset` implementing `__len__` and `__getitem__`.
- Implement dynamic sequence padding and mask construction in a custom `collate_fn`.
- Configure `DataLoader` options including batch size, shuffling, and dropped remnants.
- Verify pipeline correctness with automated unit test assertions.

## Prerequisites
- Day 204 (PyTorch: autograd and nn.Module).
- Python 3.11+ with PyTorch.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 1 GB RAM.
- 100 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
PyTorch is free and open-source under the modified BSD license.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/datasets_and_dataloaders_lib.py`: Student scaffold file.
- `examples/datasets_and_dataloaders_lib.py`: Complete reference implementation.
- `tests/test_datasets_and_dataloaders_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/datasets_and_dataloaders_lib.py
```

## What the commands do
- Instantiates a ragged-sequence dataset.
- Executes dynamic batch collation and padding.
- Iterates across mini-batches verifying batch shapes.

## Expected output
```
DataLoader Demo: Processed 96 samples across 6 batches. Batch 0 Shape: (16, 20)
```

## Validation steps
1. Verify that `RaggedSequenceDataset` returns valid tuples of `(Tensor, int)`.
2. Confirm that `dynamic_padding_collate` pads each batch to its local maximum length.
3. Ensure all unit test assertions pass.

## Tests
Run the test runner script:
```bash
./tests/run_tests.sh
```

## Cleanup
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
```

## Troubleshooting
- **Shape Mismatch Error:** Ensure `collate_fn` stacks inputs along `dim=0`.

## Security notes
All data loading runs locally in memory without remote network transmissions.

## Extension exercises
1. Implement an `IterableDataset` with multi-worker partition sharding.
2. Add random token masking inside `__getitem__` for self-supervised pre-training.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Datasets and DataLoaders
- **Day number:** 205 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-205-datasets-and-dataloaders
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-205-datasets-and-dataloaders` when the site is running.
<!-- generated-links:end -->
