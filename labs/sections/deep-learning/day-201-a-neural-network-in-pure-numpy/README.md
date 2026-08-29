# Lab: Day 201 -- A Neural Network in Pure NumPy

## Lesson
Day number: 201 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Complete Neural Network Engine in Pure NumPy.

## Purpose
Build a complete, standalone, object-oriented `NeuralNetwork` in pure NumPy. You will integrate He parameter initialization, forward caching, analytical backpropagation, mini-batch shuffling, and SGD with Momentum, training the network to solve complex non-linear classification manifolds (Two Moons).

## Learning objectives
- Implement He and Xavier parameter initialization breaking symmetry.
- Integrate modular forward passes, activation functions, and backpropagation.
- Code Mini-Batch SGD with Momentum parameter update dynamics.
- Train the network on non-linear datasets and achieve > 90% classification accuracy.

## Prerequisites
- Days 197-200 (Perceptron, Activations, Forward Prop, Backprop).
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
- `starter/a_neural_network_in_pure_numpy_lib.py`: Student scaffold file.
- `examples/a_neural_network_in_pure_numpy_lib.py`: Complete reference implementation.
- `tests/test_a_neural_network_in_pure_numpy_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/a_neural_network_in_pure_numpy_lib.py
```

## What the commands do
- Generates synthetic Two Moons dataset.
- Trains a 3-layer neural network `[2, 16, 8, 2]`.
- Evaluates classification accuracy and loss convergence.

## Expected output
```
Pure NumPy Demo: Final Loss = 0.0245, Accuracy = 99.2%
```

## Validation steps
1. Verify that training loss decreases across epochs.
2. Confirm that final classification accuracy exceeds 90% on the Two Moons dataset.
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
- **Accuracy Stuck at 50%:** Ensure learning rate is sufficiently large (`lr >= 0.05`) and activations are non-linear.

## Security notes
All training runs locally on CPU memory without external telemetric transmissions.

## Extension exercises
1. Implement **Learning Rate Decay**.
2. Code the **Adam** optimization algorithm in pure NumPy.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Neural Network in Pure NumPy
- **Day number:** 201 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-201-a-neural-network-in-pure-numpy
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-201-a-neural-network-in-pure-numpy` when the site is running.
<!-- generated-links:end -->
