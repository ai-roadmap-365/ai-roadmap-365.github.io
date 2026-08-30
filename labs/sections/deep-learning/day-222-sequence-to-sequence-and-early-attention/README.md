# Lab: Day 222 -- Sequence-to-Sequence and Early Attention

## Lesson
Day number: 222 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Sequence-to-Sequence Models and Early Additive Attention.

## Purpose
Build and test the Bahdanau Additive Attention mechanism from first principles in PyTorch. Implement query-key alignment scoring, compute dynamic context vectors over encoder hidden states, apply padding masks, and verify attention probability distributions.

## Learning objectives
- Implement Bahdanau Additive Attention linear projections and tanh scoring.
- Apply softmax normalization and batch matrix multiplication for dynamic context vector creation.
- Enforce padding masks to eliminate attention leakage onto padding tokens.
- Validate attention alignment properties across variable-length sequence batches.

## Prerequisites
- Day 221 (LSTMs and GRUs).
- Python 3.11+ with PyTorch and NumPy.

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
PyTorch is open-source software maintained by the Linux Foundation under a modified BSD license.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/sequence_to_sequence_and_early_attention_lib.py`: Student scaffold file.
- `examples/sequence_to_sequence_and_early_attention_lib.py`: Complete reference implementation.
- `tests/test_sequence_to_sequence_and_early_attention_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/sequence_to_sequence_and_early_attention_lib.py
```

## What the commands do
- Evaluates Bahdanau attention forward pass over query and key tensors.
- Applies padding masks and computes dynamic context vectors.
- Runs unit test assertions.

## Expected output
```
Attention Demo: Context Shape = torch.Size([2, 8]), Weight Sums = [1.0, 1.0]
```

## Validation steps
1. Verify `BahdanauAttention.forward` outputs a context vector of shape `(batch_size, enc_dim)`.
2. Confirm `attn_weights` sum to 1.0 along the sequence dimension.
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
- **Dimensions mismatch in bmm:** Ensure query is unsqueezed along dimension 1 and weights are unsqueezed along dimension 1 before `torch.bmm`.

## Security notes
All attention matrix operations execute in local process memory.

## Extension exercises
1. Implement Luong multiplicative dot-product attention scoring.
2. Build an attention heatmap visualizer using Matplotlib.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Sequence-to-Sequence and Early Attention
- **Day number:** 222 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-222-sequence-to-sequence-and-early-attention
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-222-sequence-to-sequence-and-early-attention` when the site is running.
<!-- generated-links:end -->
