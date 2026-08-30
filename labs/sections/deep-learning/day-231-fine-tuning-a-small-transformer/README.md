# Lab: Day 231 -- Fine-Tuning a Small Transformer

## Lesson
Day number: 231 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Fine-Tuning Small Transformers, LLRD, and Regularization.

## Purpose
Build and test a modular fine-tuning parameter configuration and regularization suite in PyTorch. Implement the Layer-wise Learning Rate Decay (LLRD) parameter group builder, construct decoupled weight decay mappings, and implement early stopping patience monitors.

## Learning objectives
- Implement Layer-wise Learning Rate Decay (LLRD) parameter grouping.
- Enforce decoupled zero weight decay on bias and normalization layers.
- Construct the EarlyStopping regularization callback.
- Verify optimization parameter stability and learning rate assignments.

## Prerequisites
- Day 230 (Hugging Face Transformers in Practice).
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
- `starter/fine_tuning_a_small_transformer_lib.py`: Student scaffold file.
- `examples/fine_tuning_a_small_transformer_lib.py`: Complete reference implementation.
- `tests/test_fine_tuning_a_small_transformer_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/fine_tuning_a_small_transformer_lib.py
```

## What the commands do
- Generates LLRD optimizer parameter groups across network layers.
- Tests early stopping convergence tracking.
- Runs unit test assertions.

## Expected output
```
FineTune Demo: Created 6 Parameter Groups
```

## Validation steps
1. Verify `create_llrd_parameter_groups` produces parameter groups for each active layer.
2. Confirm biases and LayerNorm parameters receive `weight_decay == 0.0`.
3. Confirm `EarlyStopping` triggers when validation loss fails to improve after patience steps.
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
- **Missing parameters in optimizer:** Ensure all model parameters with `requires_grad=True` are captured in the parameter groups.

## Security notes
All optimization routines execute locally in process memory.

## Extension exercises
1. Implement a Knowledge Distillation loss module.
2. Export a PyTorch transformer to ONNX Runtime format.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Fine-Tuning a Small Transformer
- **Day number:** 231 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-231-fine-tuning-a-small-transformer
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-231-fine-tuning-a-small-transformer` when the site is running.
<!-- generated-links:end -->
