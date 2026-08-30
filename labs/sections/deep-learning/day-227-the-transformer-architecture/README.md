# Lab: Day 227 -- The Transformer Architecture

## Lesson
Day number: 227 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Full Transformer Architecture and Pre-LN Blocks.

## Purpose
Build and test the complete `TransformerEncoderLayer` featuring Pre-LN Layer Normalization, Multi-Head Self-Attention, Position-Wise Feedforward Networks (FFN) with 4x dimension expansion and GELU activations, and unscaled identity residual streams in PyTorch.

## Learning objectives
- Implement the Pre-LN Transformer block architecture.
- Construct the Position-Wise Feedforward Network with GELU activation and 4x hidden expansion.
- Verify uninhibited identity residual gradient flow across stacked layers.
- Verify dimensional consistency across multi-layer Transformer pipelines.

## Prerequisites
- Day 226 (Self-Attention, Step by Step).
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
- `starter/the_transformer_architecture_lib.py`: Student scaffold file.
- `examples/the_transformer_architecture_lib.py`: Complete reference implementation.
- `tests/test_the_transformer_architecture_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/the_transformer_architecture_lib.py
```

## What the commands do
- Executes forward passes through the Pre-LN Transformer encoder layer.
- Tests residual gradient flow backpropagation.
- Runs unit test assertions.

## Expected output
```
Transformer Block Demo: Output Shape = torch.Size([2, 6, 32])
```

## Validation steps
1. Verify `TransformerEncoderLayer.forward` outputs a tensor matching `(batch_size, seq_len, d_model)`.
2. Confirm input tensor gradients are non-zero after backpropagation.
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
- **Residual connection dimension error:** Ensure `d_model` remains constant across all attention projections and FFN output layers.

## Security notes
All neural computations execute in local process memory.

## Extension exercises
1. Implement a SwiGLU gated feedforward layer.
2. Implement RMSNorm as a replacement for LayerNorm.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The Transformer Architecture
- **Day number:** 227 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-227-the-transformer-architecture
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-227-the-transformer-architecture` when the site is running.
<!-- generated-links:end -->
