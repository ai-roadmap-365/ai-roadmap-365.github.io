# Day 333 Lab: Edge Deployment and Quantization

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Kubernetes Concepts
- **Day number:** 333 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-333-kubernetes-concepts
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-333-kubernetes-concepts` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Model Quantizer and Memory Profiler in Python calculating affine scale factors, zero points, 4-bit integer quantization, and reconstruction distortion metrics.

## Learning objectives
- Calculate affine scale and zero-point parameters.
- Quantize continuous float32 arrays into 4-bit integers.
- Reconstruct dequantized floating-point approximations.
- Compute Mean Squared Error (MSE) and Signal-to-Noise Ratio (SNR).

## Prerequisites
- Python 3.10+ installed
- pytest, numpy installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, pytest, numpy

## Free and open-source options
- Python Standard Library, Pytest, NumPy

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/quantizer_profiler.py`: Starter implementation skeleton
- `examples/quantizer_profiler.py`: Verified reference implementation
- `tests/test_quantizer_profiler.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/quantizer_profiler.py
```

## What the commands do
- Executes 4-bit quantization, dequantization reconstruction, and error evaluation.

## Expected output
```text
All 5 checks passed 100% with zero errors.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Correct scale factor and zero point derivation
- Quantization clipping within [0, 15] bounds
- Dequantization reconstruction fidelity
- Handling constant uniform tensors
- Compression ratio calculation

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure zero point is rounded to integer and clamped.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement per-channel quantization.

## Navigation
Day number: 333 of 365
