# Lab: Day 200 -- Backpropagation

## Lesson
Day number: 200 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Backpropagation and Gradient Checking.

## Purpose
Build a fully vectorized, modular `BackpropEngine` in pure NumPy. You will derive and implement the four fundamental equations of backpropagation, propagate error residuals through activation layers, evaluate exact parameter gradients, and verify gradient accuracy using numerical gradient checking.

## Learning objectives
- Formulate and code output error residuals `dZ^[L] = A^[L] - Y`.
- Implement upstream gradient propagation `dA^[l-1] = (W^[l])^T dZ^[l]`.
- Calculate parameter gradients `dW^[l]` and `db^[l]` across mini-batches.
- Validate analytical gradients against numerical finite differences to `1e-7` tolerance.

## Prerequisites
- Multivariable calculus (partial derivatives, chain rule).
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
- `starter/backpropagation_lib.py`: Student scaffold file.
- `examples/backpropagation_lib.py`: Complete reference implementation.
- `tests/test_backpropagation_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/backpropagation_lib.py
```

## What the commands do
- Executes a 2-layer network forward pass.
- Sweeps backward computing exact gradients `dW` and `db`.
- Validates parameter shapes and gradient checks.

## Expected output
```
Backprop Demo: dW2 Shape = (3, 16), dW1 Shape = (16, 8)
```

## Validation steps
1. Verify that `dW` and `db` shapes match parameter matrices for all layers.
2. Confirm that relative error between analytical and numerical gradients is less than `1e-6`.
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
- **Gradient Shape Inversion:** Ensure `np.dot(dZ, A_prev.T)` is used for weight gradients.

## Security notes
All derivative calculus executes locally without network access.

## Extension exercises
1. Implement **L2 Weight Regularization** gradients.
2. Code backward propagation for **Leaky ReLU** and **Tanh**.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Backpropagation
- **Day number:** 200 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-200-backpropagation
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-200-backpropagation` when the site is running.
<!-- generated-links:end -->
