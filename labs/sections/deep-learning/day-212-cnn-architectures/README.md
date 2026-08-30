# Lab: Day 212 -- CNN Architectures

## Lesson
Day number: 212 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: CNN Architectures and ResNet in PyTorch.

## Purpose
Build and test a modular Deep Residual Network (ResNet) architecture in PyTorch. Implement `BasicResidualBlock` with 1x1 projection shortcuts, construct an end-to-end `MiniResNet` classifier with Global Average Pooling, and verify uninhibited gradient backpropagation across deep residual stages.

## Learning objectives
- Implement the `BasicResidualBlock` with residual addition and projection shortcuts.
- Construct `MiniResNet` with stem, residual stages, and adaptive pooling.
- Verify gradient flow through identity shortcut connections.
- Analyze parameter counts and computational scaling in deep vision networks.

## Prerequisites
- Day 211 (Convolutions).
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
- `starter/cnn_architectures_lib.py`: Student scaffold file.
- `examples/cnn_architectures_lib.py`: Complete reference implementation.
- `tests/test_cnn_architectures_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/cnn_architectures_lib.py
```

## What the commands do
- Instantiates a `MiniResNet` model.
- Evaluates forward pass on synthetic 32x32 image tensors.
- Calculates parameter count and checks gradient backpropagation.

## Expected output
```
MiniResNet Demo: Out Shape = torch.Size([2, 10]), Params = 72618
```

## Validation steps
1. Verify that `BasicResidualBlock` executes spatial downsampling correctly.
2. Confirm that all model parameters receive non-zero gradients during backprop.
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
- **Dimension Mismatch on Addition:** Verify shortcut projection layer is used when `stride != 1` or `in_channels != out_channels`.

## Security notes
All neural calculations execute locally in CPU memory without external network calls.

## Extension exercises
1. Implement a ResNet Bottleneck Block and benchmark memory usage.
2. Integrate Squeeze-and-Excitation (SE) channel attention blocks.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** CNN Architectures
- **Day number:** 212 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-212-cnn-architectures
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-212-cnn-architectures` when the site is running.
<!-- generated-links:end -->
