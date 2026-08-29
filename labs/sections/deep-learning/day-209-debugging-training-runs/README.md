# Lab: Day 209 -- Debugging Training Runs

## Lesson
Day number: 209 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Debugging Training Runs in PyTorch.

## Purpose
Build and test a comprehensive neural network debugging suite in PyTorch. Implement the single-batch overfitting sanity test, derive and implement custom gradient norm clipping, and diagnose gradient vanishing/explosion pathologies.

## Learning objectives
- Implement the single-batch overfitting sanity check to verify computational graph correctness.
- Implement gradient norm calculation and clipping from scratch.
- Verify bitwise gradient alignment with `torch.nn.utils.clip_grad_norm_`.
- Apply diagnostic protocols for hunting NaNs and uncalibrated initial losses.

## Prerequisites
- Day 208 (Dropout, Batch Norm, and Regularization).
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
- `starter/debugging_training_runs_lib.py`: Student scaffold file.
- `examples/debugging_training_runs_lib.py`: Complete reference implementation.
- `tests/test_debugging_training_runs_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/debugging_training_runs_lib.py
```

## What the commands do
- Executes a single-batch overfit diagnostic test on a multi-layer model.
- Evaluates gradient norm scaling and clipping.
- Verifies mathematical gradient integrity.

## Expected output
```
Debugging Demo: Single-Batch Overfit Passed = True, Raw Norm = 14.82, Clipped Norm = 1.00
```

## Validation steps
1. Verify that single-batch overfitting drives cross-entropy loss below 0.01.
2. Confirm that `custom_clip_grad_norm` scales gradients to exactly `max_norm`.
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
- **Overfit Test Fails to Reach 100%:** Ensure `optimizer.zero_grad()` is called before `loss.backward()`.

## Security notes
All debugging routines execute in local memory on CPU hardware.

## Extension exercises
1. Implement forward/backward hooks that log activation sparsity across layers.
2. Build an automated learning rate finder tracking loss derivatives.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Debugging Training Runs
- **Day number:** 209 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-209-debugging-training-runs
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-209-debugging-training-runs` when the site is running.
<!-- generated-links:end -->
