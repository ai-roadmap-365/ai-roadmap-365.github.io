# Lab: Day 197 -- The Perceptron

## Lesson
Day number: 197 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: The Artificial Perceptron and Linear Separability.

## Purpose
Build Frank Rosenblatt's classic Artificial Perceptron and a two-layer Multi-Layer Perceptron (MLP) from scratch in pure NumPy. You will implement the Perceptron Learning Rule, train on linearly separable boolean logic gates (AND, OR), analyze the geometric failure on XOR parity, and solve XOR using a two-layer network.

## Learning objectives
- Implement the Perceptron dot-product and Heaviside step activation math.
- Code the Perceptron Learning Rule for weight and bias adaptation.
- Verify finite-step convergence on linearly separable datasets.
- Construct a two-layer MLP that resolves the non-linear XOR parity problem.

## Prerequisites
- Linear algebra (dot products, vector addition).
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
- `starter/the_perceptron_lib.py`: Student scaffold file.
- `examples/the_perceptron_lib.py`: Complete reference implementation.
- `tests/test_the_perceptron_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/the_perceptron_lib.py
```

## What the commands do
- Trains Perceptron on AND gate truth table.
- Evaluates weight updates across epochs.
- Verifies classification convergence.

## Expected output
```
Perceptron Demo: AND Gate Predictions = [0, 0, 0, 1], Epochs = 6
```

## Validation steps
1. Verify that the Perceptron achieves 100% accuracy on AND and OR gates.
2. Confirm that `solve_xor_with_two_layers` achieves 100% accuracy across all 4 XOR states.
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
- **Infinite Loop on XOR:** Ensure `max_epochs` is finite because XOR is linearly non-separable.

## Security notes
All neural computations execute strictly on local CPU memory.

## Extension exercises
1. Implement **Adaline (Adaptive Linear Neuron)** using LMS gradient updates.
2. Solve **3-Input Parity** (`x1 ^ x2 ^ x3`) using a 2-layer network.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The Perceptron
- **Day number:** 197 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-197-the-perceptron
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-197-the-perceptron` when the site is running.
<!-- generated-links:end -->
