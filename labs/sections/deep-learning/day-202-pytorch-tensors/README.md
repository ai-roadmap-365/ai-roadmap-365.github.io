# Lab: Day 202 -- PyTorch Tensors

## Lesson
Day number: 202 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: PyTorch Tensors, Strides, and Autograd Mechanics.

## Purpose
Master multidimensional tensor manipulation, memory contiguity contracts, hardware device abstraction, and dynamic automatic differentiation. You will evaluate tensor memory layouts, test stride modifications across views and permutations, and verify analytical gradients against Autograd computational graph passes.

## Learning objectives
- Manipulate multidimensional tensors, shapes, strides, and memory buffers.
- Enforce the contiguity contract when reshaping permuted tensors.
- Implement device-agnostic code running on CPU, Apple Silicon MPS, and NVIDIA CUDA.
- Verify Autograd automatic differentiation against exact analytical derivatives.

## Prerequisites
- Days 199-201 (Forward Prop, Backprop, Neural Networks).
- Python 3.11+ with NumPy and PyTorch (CPU-only wheel supported).

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
All tools used in this lab (Python, NumPy, PyTorch CPU, pytest) are free and open-source under BSD/MIT/Apache licenses.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```
*Note on PyTorch Installation:* To install PyTorch CPU-only wheels on constrained environments:
`pip install torch --extra-index-url https://download.pytorch.org/whl/cpu`

## File structure
- `starter/pytorch_tensors_lib.py`: Student scaffold file.
- `examples/pytorch_tensors_lib.py`: Complete reference implementation.
- `tests/test_pytorch_tensors_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/pytorch_tensors_lib.py
```

## What the commands do
- Executes tensor memory stride evaluations.
- Computes forward and backward autograd gradient simulations.
- Verifies numerical gradient precision.

## Expected output
```
PyTorch Tensors Demo: Output Z shape = (2, 2), dW shape = (2, 2)
```

## Validation steps
1. Verify that non-contiguous transposed tensors are safely flattened via contiguous memory buffers.
2. Confirm that analytical gradients match numerical finite differences to `1e-6` precision.
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
- **Non-Contiguous Error:** Call `.contiguous()` before `.view()` when modifying tensor dimensions.

## Security notes
All tensor calculations execute locally without external network transmission.

## Extension exercises
1. Implement **Higher-Order Gradients (Hessian-Vector Products)**.
2. Benchmark tensor performance across CPU, MPS, and CUDA devices.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** PyTorch Tensors
- **Day number:** 202 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-202-pytorch-tensors
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-202-pytorch-tensors` when the site is running.
<!-- generated-links:end -->
