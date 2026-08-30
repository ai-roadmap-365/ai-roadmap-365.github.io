# Lab: Day 225 -- “Attention Is All You Need”

## Lesson
Day number: 225 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Scaled Dot-Product Attention from First Principles.

## Purpose
Build and test the foundational Scaled Dot-Product Attention mechanism from first principles in PyTorch. Implement batched matrix multiplication, 1/sqrt(d_k) variance scaling, causal and padding masking, softmax normalization, and value aggregation.

## Learning objectives
- Implement vectorized Scaled Dot-Product Attention in PyTorch.
- Apply 1/sqrt(d_k) scaling to stabilize dot-product variance to 1.0.
- Apply causal lower-triangular masks to prevent look-ahead information leakage.
- Verify softmax probability distributions and output dimensions across multi-dimensional batch tensors.

## Prerequisites
- Day 224 (A Sentiment Analysis Project).
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
- `starter/attention_is_all_you_need_lib.py`: Student scaffold file.
- `examples/attention_is_all_you_need_lib.py`: Complete reference implementation.
- `tests/test_attention_is_all_you_need_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/attention_is_all_you_need_lib.py
```

## What the commands do
- Executes Scaled Dot-Product Attention over 4D Query, Key, and Value tensors.
- Verifies causal masking and probability distribution rows.
- Runs unit test assertions.

## Expected output
```
Scaled Attention Demo: Output Shape = torch.Size([2, 4, 6, 16]), Weights Shape = torch.Size([2, 4, 6, 6])
```

## Validation steps
1. Verify `ScaledDotProductAttention.forward` outputs a tensor matching `(..., Seq_Q, d_v)`.
2. Confirm `attn_weights` sum to 1.0 along the last dimension.
3. Ensure upper-triangular masked positions evaluate to 0.0.
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
- **Matrix dimension mismatch:** Use `k.transpose(-2, -1)` to transpose only the last two dimensions of key tensor $K$.

## Security notes
All attention matrix multiplications execute in local memory.

## Extension exercises
1. Implement Multi-Query Attention (MQA) sharing Key/Value heads.
2. Implement an online tiled attention kernel.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** “Attention Is All You Need”
- **Day number:** 225 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-225-attention-is-all-you-need
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-225-attention-is-all-you-need` when the site is running.
<!-- generated-links:end -->
