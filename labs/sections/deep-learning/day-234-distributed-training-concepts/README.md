# Lab: Day 234 -- Distributed Training Concepts

## Lesson
Day number: 234 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Distributed Training Architectures, Ring-AllReduce, and ZeRO Memory Sharding.

## Purpose
Build and test a modular distributed training simulation engine in Python. Implement Ring-AllReduce collective communication mechanics and calculate ZeRO memory sharding budgets across GPU cluster ranks.

## Learning objectives
- Implement the 2-phase Ring-AllReduce algorithm (Scatter-Reduce and All-Gather).
- Calculate per-GPU VRAM memory requirements across ZeRO-1, ZeRO-2, and ZeRO-3 / FSDP stages.
- Analyze collective communication bandwidth efficiency.
- Verify exact mathematical aggregation across simulated multi-GPU processes.

## Prerequisites
- Day 233 (Mixed Precision and Performance).
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
- `starter/distributed_training_concepts_lib.py`: Student scaffold file.
- `examples/distributed_training_concepts_lib.py`: Complete reference implementation.
- `tests/test_distributed_training_concepts_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/distributed_training_concepts_lib.py
```

## What the commands do
- Simulates Ring-AllReduce across multi-rank tensor arrays.
- Computes ZeRO memory partition budgets.
- Runs unit test assertions.

## Expected output
```
Distributed Demo: Reduced Sum = [3.0, 3.0, 3.0, 3.0], 70B on 64 GPUs ZeRO-3 = 17.5 GB
```

## Validation steps
1. Verify `simulate_ring_allreduce` outputs the exact sum across all ranks.
2. Confirm ZeRO-3 divides total 16 bytes/param by cluster GPU count $P$.
3. Confirm ZeRO-1 shards only the 12 bytes/param optimizer states.
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
- **Length mismatch in Ring-AllReduce:** Ensure tensor array length is evenly divisible by number of ranks.

## Security notes
All collective communication simulations execute locally in process memory.

## Extension exercises
1. Implement a Pipeline Parallelism 1F1B bubble simulator.
2. Build a Tensor Parallel column/row linear layer in PyTorch.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Distributed Training Concepts
- **Day number:** 234 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-234-distributed-training-concepts
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-234-distributed-training-concepts` when the site is running.
<!-- generated-links:end -->
