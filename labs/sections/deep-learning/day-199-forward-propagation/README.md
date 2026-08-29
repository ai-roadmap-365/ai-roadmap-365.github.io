# Lab: Day 199 -- Forward Propagation

## Lesson
Day number: 199 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Multi-Layer Forward Propagation and Activation Caching.

## Purpose
Build a generalized, modular L-Layer Forward Propagation engine in pure NumPy. You will formulate linear affine transformations, manage activation functions across layers, enforce strict matrix dimension contracts, construct forward activation caches, and calculate mini-batch Categorical Cross-Entropy loss.

## Learning objectives
- Implement vectorized dense layer affine transformations `Z = W A_prev + b`.
- Structure modular L-layer forward passes with activation caching.
- Enforce strict matrix dimension contracts across mini-batches.
- Calculate numerically stable Categorical Cross-Entropy (CCE) loss.

## Prerequisites
- Linear algebra (matrix multiplication, broadcasting).
- Python 3.11+ with NumPy.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 512 MB RAM.
- 50 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
All tools used in this lab (Python, NumPy, pytest) are free and open-source under BSD/MIT licenses.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/forward_propagation_lib.py`: Student scaffold file.
- `examples/forward_propagation_lib.py`: Complete reference implementation.
- `tests/test_forward_propagation_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/forward_propagation_lib.py
```

## What the commands do
- Constructs a 3-layer neural network `[784, 128, 64, 10]`.
- Executes forward propagation across a mini-batch of 32 samples.
- Computes initial Categorical Cross-Entropy loss.

## Expected output
```
Forward Demo: Output Shape = (10, 32), Initial CCE Loss = 2.3026
```

## Validation steps
1. Verify that output probabilities sum to 1.0 along the class axis for every sample.
2. Confirm that forward caches store `A_prev`, `Z`, `W`, and `b` with correct dimensions.
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
- **Dimension Mismatch:** Ensure input matrix has shape `(features, batch_size)`.

## Security notes
All tensor calculations execute locally in system RAM.

## Extension exercises
1. Implement **Binary Cross-Entropy (BCE)** loss evaluation.
2. Build an inverted **Dropout** forward pass.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Forward Propagation
- **Day number:** 199 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-199-forward-propagation
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-199-forward-propagation` when the site is running.
<!-- generated-links:end -->
