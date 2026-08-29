# Lab: Day 206 -- Optimizers: SGD to Adam

## Lesson
Day number: 206 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Optimizers from SGD to AdamW in PyTorch.

## Purpose
Build and test a custom implementation of the `AdamW` optimizer from scratch in PyTorch. Derive and implement first moment momentum tracking, second moment curvature scaling, initial step bias corrections, and decoupled weight decay, verifying bitwise precision against PyTorch's native `torch.optim.AdamW`.

## Learning objectives
- Subclass `torch.optim.Optimizer` implementing the `@torch.no_grad()` `step()` method.
- Implement decoupled weight decay updates.
- Apply bias corrections to first and second moment moving averages.
- Benchmark optimizer convergence on non-convex loss surfaces.

## Prerequisites
- Day 204-205 (PyTorch autograd, nn.Module, Datasets, DataLoaders).
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
- `starter/optimizers_sgd_to_adam_lib.py`: Student scaffold file.
- `examples/optimizers_sgd_to_adam_lib.py`: Complete reference implementation.
- `tests/test_optimizers_sgd_to_adam_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/optimizers_sgd_to_adam_lib.py
```

## What the commands do
- Optimizes the non-convex Rosenbrock objective function.
- Compares custom AdamW against standard optimizer baselines.
- Verifies exact numerical gradient step convergence.

## Expected output
```
Rosenbrock Demo: Initial Loss = 104.0000, Final Loss = 0.0314
```

## Validation steps
1. Verify that `CustomAdamW` reduces quadratic loss monotonically.
2. Confirm that `CustomAdamW` matches `torch.optim.AdamW` within `1e-6` numerical tolerance.
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
- **Diverging Updates:** Check that `step_size` divides by `bias_correction1` and `denom` uses `sqrt(v_hat) + eps`.

## Security notes
All optimization routines run in local memory on CPU hardware.

## Extension exercises
1. Implement the **Lion Optimizer** (Google 2023) using the `torch.sign` update rule.
2. Add per-parameter group learning rates and weight decays.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Optimizers: SGD to Adam
- **Day number:** 206 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-206-optimizers-sgd-to-adam
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-206-optimizers-sgd-to-adam` when the site is running.
<!-- generated-links:end -->
