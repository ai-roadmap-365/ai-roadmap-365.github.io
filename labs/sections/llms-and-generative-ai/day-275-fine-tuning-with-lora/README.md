# Day 275 Lab: Custom LoRA Linear Layer in NumPy

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Fine-Tuning with LoRA
- **Day number:** 275 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-275-fine-tuning-with-lora
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-275-fine-tuning-with-lora` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a custom Low-Rank Adaptation (LoRA) linear layer from scratch in Python and NumPy, implementing low-rank matrix decomposition, parameter reduction accounting, and zero-overhead offline weight merging.

## Learning objectives
- Implement low-rank decomposition matrices ($A$ and $B$) with Gaussian and zero initializations.
- Compute scaling factors ($\alpha / r$) and forward pass activations.
- Verify zero delta updates at step zero.
- Implement offline weight merging ($W_{\text{merged}} = W_0 + \Delta W$) and verify bit-exact output parity.

## Prerequisites
- Python 3.10+ installed
- NumPy and pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, numpy, pytest

## Free and open-source options
- Python Standard Library, NumPy

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/lora_layer.py`: Starter implementation skeleton
- `examples/lora_layer.py`: Verified reference implementation
- `tests/test_lora_layer.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/lora_layer.py
```

## What the commands do
- Executes forward pass across 4096-dimension linear projections with rank-8 adapters.
- Measures parameter counts and performs offline weight merging.

## Expected output
```text
[LORA] Base: 16,777,216 | LoRA Trainable: 65,536 (0.39%)
[MERGE] Merged delta into base weights bit-exactly.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Zero delta output at step zero initialization
- 99.6% parameter reduction on 4096x4096 projections
- Bit-exact output agreement between LoRA dynamic forward pass and merged weight forward pass
- Weight unmerge reversibility

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
If matrix multiplication fails, check tensor shapes: $A$ is $(r, d_{\text{in}})$, $B$ is $(d_{\text{out}}, r)$.

## Security notes
Runs entirely offline on local CPU using standard NumPy tensors.

## Extension exercises
Add support for quantization-aware simulated 4-bit NormalFloat weights.

## Navigation
Day number: 275 of 365
