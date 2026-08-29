# Lab: Day 198 -- Activation Functions

## Lesson
Day number: 198 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Activation Functions and Numerical Gradient Checking.

## Purpose
Build a complete, vectorized, high-performance `ActivationEngine` in pure NumPy. You will implement Sigmoid, Tanh, ReLU, Leaky ReLU, GeLU, and numerically stable Softmax, derive analytical gradients, perform central finite-difference gradient checks, and analyze vanishing gradient behavior across deep layers.

## Learning objectives
- Implement Sigmoid, Tanh, ReLU, Leaky ReLU, GeLU, and Softmax forward functions.
- Compute analytical derivatives for each activation function.
- Execute numerical gradient checking to verify derivative precision.
- Prevent floating-point overflow in Softmax with maximum subtraction.

## Prerequisites
- Calculus (derivatives, chain rule).
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
- `starter/activation_functions_lib.py`: Student scaffold file.
- `examples/activation_functions_lib.py`: Complete reference implementation.
- `tests/test_activation_functions_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/activation_functions_lib.py
```

## What the commands do
- Executes forward activations and analytical derivatives.
- Verifies numerical gradient checks against finite differences.
- Evaluates numerically stable Softmax on extreme logits.

## Expected output
```
Activation Demo: Sigmoid Relative Error = 1.2415e-11, Stable Softmax Sum = 1.0000
```

## Validation steps
1. Verify that numerical gradient check error is less than `1e-5` for all activations.
2. Confirm that Softmax does not return `NaN` or `inf` on logits of `5000.0`.
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
- **Numerical Gradient Discontinuity:** For ReLU, evaluate away from the non-differentiable cusp `z = 0.0`.

## Security notes
All mathematical computations execute locally in process memory.

## Extension exercises
1. Implement the **SELU (Scaled Exponential Linear Unit)** activation.
2. Code the **Mish** activation function and compute its analytical gradient.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Activation Functions
- **Day number:** 198 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-198-activation-functions
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-198-activation-functions` when the site is running.
<!-- generated-links:end -->
