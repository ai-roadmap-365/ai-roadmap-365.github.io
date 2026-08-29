# Lab: Day 208 -- Dropout, Batch Norm, and Regularization

## Lesson
Day number: 208 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Dropout, Batch Normalization, and Regularization in PyTorch.

## Purpose
Build and test custom implementations of Inverted Dropout and Batch Normalization from scratch in PyTorch. Verify stochastic masking and inverted scaling during training, deterministic identity passing during evaluation, running statistic accumulation, and complete model mode management.

## Learning objectives
- Implement Inverted Dropout with Bernoulli stochastic masking and `1/(1-p)` scaling.
- Implement `CustomBatchNorm1d` tracking mini-batch statistics and running statistics.
- Verify deterministic model execution in `model.eval()` mode.
- Integrate normalization and regularization layers into a deep MLP architecture.

## Prerequisites
- Day 207 (Learning Rate Schedules).
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
- `starter/dropout_batch_norm_and_regularization_lib.py`: Student scaffold file.
- `examples/dropout_batch_norm_and_regularization_lib.py`: Complete reference implementation.
- `tests/test_dropout_batch_norm_and_regularization_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/dropout_batch_norm_and_regularization_lib.py
```

## What the commands do
- Evaluates `RegularizedMLP` forward passes in training versus evaluation modes.
- Verifies stochastic dropout activation during training.
- Confirms bitwise deterministic consistency during evaluation.

## Expected output
```
Regularization Demo: Training Stochastic = True, Eval Deterministic = True
```

## Validation steps
1. Verify that `CustomDropout` produces zero-masked activations during training.
2. Confirm that `CustomBatchNorm1d` updates `running_mean` and `running_var`.
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
- **Outputs Differ in Eval Mode:** Check that `CustomDropout` checks `self.training` before applying the mask.

## Security notes
All calculations run in local system memory on CPU hardware.

## Extension exercises
1. Implement **RMSNorm** and benchmark its memory footprint against LayerNorm.
2. Implement Monte Carlo Dropout uncertainty estimation over 50 test iterations.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Dropout, Batch Norm, and Regularization
- **Day number:** 208 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-208-dropout-batch-norm-and-regularization
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-208-dropout-batch-norm-and-regularization` when the site is running.
<!-- generated-links:end -->
