# Lab: Day 235 -- Experiment Tracking

## Lesson
Day number: 235 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Experiment Tracking, MLOps, and Reproducible Checkpointing.

## Purpose
Build and test a modular experiment tracking and checkpoint versioning library in Python. Implement a crash-safe JSONL experiment logger and construct a Best-$K$ checkpoint retention manager.

## Learning objectives
- Build a structured, atomic JSONL experiment logging engine.
- Implement the 5 pillars of deep learning reproducibility.
- Construct a Best-$K$ model checkpoint retention and pruning manager.
- Verify deterministic tracking of hyperparameter trials and evaluation metrics.

## Prerequisites
- Day 234 (Distributed Training Concepts).
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
Python and standard JSON/OS libraries are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/experiment_tracking_lib.py`: Student scaffold file.
- `examples/experiment_tracking_lib.py`: Complete reference implementation.
- `tests/test_experiment_tracking_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/experiment_tracking_lib.py
```

## What the commands do
- Logs initialization, step, and evaluation events to JSONL.
- Manages model checkpoint saving and pruning.
- Runs unit test assertions.

## Expected output
```
Experiment Demo: Logged to ./test_runs/demo-run-01.jsonl, Active Checkpoints = 2
```

## Validation steps
1. Verify `ExperimentLogger` creates valid JSON Lines files.
2. Confirm `CheckpointManager` preserves exactly the top $K$ lowest validation loss checkpoints.
3. Confirm older, worse checkpoints are pruned from disk.
4. Ensure all unit test assertions pass.

## Tests
Run the test runner script:
```bash
./tests/run_tests.sh
```

## Cleanup
```bash
rm -rf test_runs test_checkpoints
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
```

## Troubleshooting
- **File lock errors:** Ensure file handlers are flushed and closed properly.

## Security notes
Do not log API keys or secrets in experiment configs.

## Extension exercises
1. Build an SQLite experiment storage engine.
2. Integrate Weights & Biases (W&B) into a PyTorch training loop.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Experiment Tracking
- **Day number:** 235 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-235-experiment-tracking
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-235-experiment-tracking` when the site is running.
<!-- generated-links:end -->
