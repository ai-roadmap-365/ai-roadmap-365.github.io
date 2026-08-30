# Lab: Day 232 -- GPUs and AI Hardware

## Lesson
Day number: 232 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: AI Hardware, GPU Architecture, and the Roofline Model.

## Purpose
Build and test a modular hardware performance analysis and Arithmetic Intensity calculation suite in PyTorch. Implement GEMM FLOP formulas, compute memory traffic across precision modes, and determine the machine balance ridge point for hardware acceleration.

## Learning objectives
- Calculate GEMM floating-point operation counts and memory transfer footprints.
- Compute Arithmetic Intensity across FP32 and FP16 numerical representations.
- Calculate hardware machine balance to diagnose memory-bandwidth vs compute bounds.
- Verify hardware performance calculations against theoretical limits.

## Prerequisites
- Day 231 (Fine-Tuning a Small Transformer).
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
PyTorch is open-source software maintained by the Linux Foundation under a modified BSD license.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/gpus_and_ai_hardware_lib.py`: Student scaffold file.
- `examples/gpus_and_ai_hardware_lib.py`: Complete reference implementation.
- `tests/test_gpus_and_ai_hardware_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/gpus_and_ai_hardware_lib.py
```

## What the commands do
- Calculates Arithmetic Intensity across FP16 and FP32 precision modes.
- Computes machine balance ridge points.
- Runs unit test assertions.

## Expected output
```
Hardware Demo: FP16 Intensity = 170.67 FLOPs/Byte, Balance = 125.0
```

## Validation steps
1. Verify `compute_gemm_intensity` calculates $2 	imes N^3$ FLOPs.
2. Confirm FP16 yields $2	imes$ higher arithmetic intensity than FP32 for identical matrix dimensions.
3. Confirm `calculate_machine_balance` correctly divides peak TFLOPs by peak bandwidth.
4. Ensure all unit test assertions pass.

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
- **Division by zero in intensity:** Ensure matrix size $N > 0$ and `dtype_bytes > 0`.

## Security notes
All performance benchmarks execute locally in process memory.

## Extension exercises
1. Implement a Roofline Model visualization plot using Matplotlib.
2. Profile PyTorch matrix multiplication using `torch.profiler`.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** GPUs and AI Hardware
- **Day number:** 232 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-232-gpus-and-ai-hardware
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-232-gpus-and-ai-hardware` when the site is running.
<!-- generated-links:end -->
