# Lab: Day 203 -- Training MNIST from Scratch

## Lesson
Day number: 203 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Training MNIST from Scratch in Pure NumPy.

## Purpose
Build and train a complete two-layer neural network on the classic MNIST handwritten digit classification benchmark in pure NumPy. You will normalize and flatten image tensors, construct a `[784, 128, 10]` architecture with He initialization, execute mini-batch SGD with Momentum, evaluate test accuracy reaching $\ge 95\%$, and perform error analysis on misclassified digits.

## Learning objectives
- Preprocess, normalize, and flatten 28x28 grayscale image datasets into 784-D tensors.
- Implement two-layer forward propagation and analytical backpropagation in pure NumPy.
- Train the model using Mini-Batch SGD with Momentum to achieve high classification accuracy.
- Evaluate confusion matrices and identify ambiguous handwritten digit error clusters.

## Prerequisites
- Days 197-202 (Perceptron, Activations, Forward Prop, Backprop, Neural Networks, PyTorch Tensors).
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
- `starter/training_mnist_from_scratch_lib.py`: Student scaffold file.
- `examples/training_mnist_from_scratch_lib.py`: Complete reference implementation.
- `tests/test_training_mnist_from_scratch_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/training_mnist_from_scratch_lib.py
```

## What the commands do
- Generates benchmark digit representations.
- Trains two-layer neural network across mini-batches.
- Evaluates test loss and validation accuracy.

## Expected output
```
MNIST Demo: Final Train Loss = 0.0581, Val Loss = 0.1245, Val Acc = 96.5%
```

## Validation steps
1. Verify that training loss decreases consistently across epochs.
2. Confirm that final accuracy exceeds 95% on held-out test data.
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
- **Loss Exploding or Returning NaN:** Verify pixel normalization divides by `255.0` and cross-entropy adds `1e-15` epsilon.

## Security notes
All training runs locally on CPU memory without external telemetric transmissions.

## Extension exercises
1. Implement **L2 Weight Regularization**.
2. Add a second hidden layer to construct a 3-layer architecture `[784, 256, 64, 10]`.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Training MNIST from Scratch
- **Day number:** 203 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-203-training-mnist-from-scratch
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-203-training-mnist-from-scratch` when the site is running.
<!-- generated-links:end -->
