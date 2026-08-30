# Lab: Day 226 -- Self-Attention, Step by Step

## Lesson
Day number: 226 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Multi-Head Self-Attention and Positional Encodings.

## Purpose
Build and test the Multi-Head Attention module and Sinusoidal Positional Encoding generator in PyTorch. Implement subspace projections, parallel scaled dot-product attention across multiple heads, tensor recombination, and output linear transformations.

## Learning objectives
- Implement Multi-Head Attention with parallel subspace splitting.
- Generate sinusoidal positional encoding matrices across arbitrary sequence lengths.
- Perform head splitting, transposition, and contiguous tensor reconstruction.
- Verify dimensional compatibility and attention probability normalization.

## Prerequisites
- Day 225 (“Attention Is All You Need”).
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
- `starter/self_attention_step_by_step_lib.py`: Student scaffold file.
- `examples/self_attention_step_by_step_lib.py`: Complete reference implementation.
- `tests/test_self_attention_step_by_step_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/self_attention_step_by_step_lib.py
```

## What the commands do
- Evaluates MultiHeadAttention forward passes over positional-encoded input tensors.
- Verifies output tensor shapes and multi-head probability distributions.
- Runs unit test assertions.

## Expected output
```
MHA Demo: Output Shape = torch.Size([2, 6, 32]), Weights Shape = torch.Size([2, 4, 6, 6])
```

## Validation steps
1. Verify `MultiHeadAttention.forward` outputs a tensor matching `(batch_size, seq_len, d_model)`.
2. Confirm `attn_weights` has shape `(batch_size, num_heads, seq_len, seq_len)`.
3. Ensure sinusoidal positional encodings lie strictly in `[-1.0, 1.0]`.
4. Ensure all unit test assertions pass.

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
- **Non-contiguous error on view:** Call `.contiguous()` before calling `.view(batch_size, -1, self.d_model)`.

## Security notes
All attention calculations execute locally in process memory.

## Extension exercises
1. Implement Rotary Position Embeddings (RoPE) in pure PyTorch.
2. Implement Grouped-Query Attention (GQA).

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Self-Attention, Step by Step
- **Day number:** 226 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-226-self-attention-step-by-step
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-226-self-attention-step-by-step` when the site is running.
<!-- generated-links:end -->
