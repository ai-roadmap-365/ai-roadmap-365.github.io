# Lab: Day 207 -- Learning Rate Schedules

## Lesson
Day number: 207 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Learning Rate Schedules in PyTorch.

## Purpose
Build and test dynamic learning rate scheduling policies in PyTorch. Implement a custom Warmup + Cosine Annealing scheduler using `torch.optim.lr_scheduler.LambdaLR`, verify linear warmup scaling and smooth cosine decay, and ensure checkpoint state persistence.

## Learning objectives
- Implement custom learning rate schedules with `torch.optim.lr_scheduler.LambdaLR`.
- Derive linear warmup formulas for early gradient stabilization.
- Apply half-period cosine decay for late-stage convergence.
- Save and restore scheduler state dictionaries across training runs.

## Prerequisites
- Day 206 (Optimizers: SGD to Adam).
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
- `starter/learning_rate_schedules_lib.py`: Student scaffold file.
- `examples/learning_rate_schedules_lib.py`: Complete reference implementation.
- `tests/test_learning_rate_schedules_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/learning_rate_schedules_lib.py
```

## What the commands do
- Executes a 100-step training simulation with Warmup + Cosine Annealing.
- Logs learning rate values across warmup, peak, and decay phases.
- Verifies smooth mathematical convergence.

## Expected output
```
Scheduler Demo: Start LR = 0.000000, Peak LR = 0.010000, Final LR = 0.000100
```

## Validation steps
1. Verify that learning rate starts at 0.0 and rises linearly to peak at step 20.
2. Confirm that learning rate decays smoothly to `min_lr` at step 100.
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
- **Learning Rate Remains Zero:** Ensure division in warmup uses `float()` to avoid integer truncation in Python.

## Security notes
All scheduling logic runs locally in memory on CPU hardware.

## Extension exercises
1. Implement `CosineAnnealingWarmRestarts` with cyclical period multipliers (T_mult = 2).
2. Add metric-based stepping with `ReduceLROnPlateau`.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Learning Rate Schedules
- **Day number:** 207 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-207-learning-rate-schedules
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-207-learning-rate-schedules` when the site is running.
<!-- generated-links:end -->
