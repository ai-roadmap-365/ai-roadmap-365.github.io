# Lab: Day 236 -- Quantization and Distillation

## Lesson
Day number: 236 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Model Compression, Symmetric INT8 Quantization, and Knowledge Distillation.

## Purpose
Build and test a modular model compression and knowledge distillation engine in PyTorch. Implement symmetric linear INT8 quantization and dequantization functions, and construct Hinton's temperature-softened Knowledge Distillation loss module.

## Learning objectives
- Implement linear symmetric INT8 quantization and dequantization functions.
- Calculate exact quantization scale factors $S = \max(|x|) / 127$.
- Build Hinton's Knowledge Distillation loss module combining softened KL-Divergence and hard Cross-Entropy.
- Verify student model gradient propagation across temperature scales.

## Prerequisites
- Day 235 (Experiment Tracking).
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
- `starter/quantization_and_distillation_lib.py`: Student scaffold file.
- `examples/quantization_and_distillation_lib.py`: Complete reference implementation.
- `tests/test_quantization_and_distillation_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/quantization_and_distillation_lib.py
```

## What the commands do
- Quantizes sample float tensors into 8-bit signed integers.
- Reconstructs floating-point approximations via dequantization.
- Computes Knowledge Distillation loss across teacher and student logits.
- Runs unit test assertions.

## Expected output
```
Quantization Demo: Scale = 0.0200, Quantized = [-127, 0, 64, 127], KD Loss = 1.8420
```

## Validation steps
1. Verify `quantize_symmetric_int8` clamps outputs to $[-127, 127]$.
2. Confirm `dequantize_symmetric_int8` reconstructs original values within rounding error bounds.
3. Confirm `KnowledgeDistillationLoss` multiplies soft loss by $\tau^2$.
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
- **Negative scale factor:** Ensure scale uses absolute maximum $\max(|x|)$.

## Security notes
All compression computations execute locally in process memory.

## Extension exercises
1. Implement asymmetric UINT8 quantization with non-zero zero point.
2. Build a simulated 4-bit weight linear layer.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Quantization and Distillation
- **Day number:** 236 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-236-quantization-and-distillation
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-236-quantization-and-distillation` when the site is running.
<!-- generated-links:end -->
