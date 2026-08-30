# Lab: Day 211 -- Convolutions

## Lesson
Day number: 211 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: Convolutions in PyTorch and NumPy.

## Purpose
Build and test a multi-channel 2D convolution engine from scratch in pure NumPy. Verify mathematical equivalence with PyTorch's native `nn.Conv2d`, calculate output spatial dimensions under various strides and paddings, and apply classical Sobel spatial filter kernels.

## Learning objectives
- Implement 2D cross-correlation sliding window operations with multiple input and output channels.
- Implement spatial padding and strided convolution logic.
- Verify bitwise numerical alignment against `torch.nn.functional.conv2d`.
- Apply classical Sobel edge detection kernels to image tensors.

## Prerequisites
- Day 210 (A Disciplined Training Project).
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
PyTorch and NumPy are free and open-source under modified BSD licenses.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/convolutions_lib.py`: Student scaffold file.
- `examples/convolutions_lib.py`: Complete reference implementation.
- `tests/test_convolutions_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/convolutions_lib.py
```

## What the commands do
- Executes a multi-channel 2D convolution across synthetic image tensors.
- Compares NumPy implementation outputs against PyTorch native `F.conv2d`.
- Verifies edge detection responses.

## Expected output
```
2D Conv Demo: Output Shape = (2, 4, 16, 16), Max Diff vs PyTorch = 0.000000e+00
```

## Validation steps
1. Verify that `calculate_conv_output_dim` computes exact spatial resolutions.
2. Confirm that `custom_conv2d_numpy` matches `F.conv2d` within 1e-5 numerical tolerance.
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
- **Dimensions Mismatch:** Verify `(H - K + 2*P) // S + 1` uses integer division.

## Security notes
All calculations run in local system memory on CPU hardware.

## Extension exercises
1. Implement Depthwise Separable Convolution in pure NumPy.
2. Build a Dilated Convolution engine supporting arbitrary dilation factors.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Convolutions
- **Day number:** 211 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-211-convolutions
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-211-convolutions` when the site is running.
<!-- generated-links:end -->
