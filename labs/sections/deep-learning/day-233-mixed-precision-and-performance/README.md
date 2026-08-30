# Lab: Day 233 -- Mixed Precision and Performance

## Lesson
Day number: 233 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Mixed Precision Training, Floating-Point Formats, and Loss Scaling.

## Purpose
Build and test a modular mixed-precision simulation and VRAM memory profiling engine in Python. Implement precision memory allocation calculations for AdamW training states and construct a dynamic loss scaling engine with overflow detection.

## Learning objectives
- Calculate exact static GPU VRAM memory requirements for mixed-precision training.
- Implement the dynamic loss scaling algorithm with backoff and growth intervals.
- Analyze floating-point precision trade-offs across FP32, FP16, BF16, and FP8.
- Verify numerical stability safeguards during training execution.

## Prerequisites
- Day 232 (GPUs and AI Hardware).
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
- `starter/mixed_precision_and_performance_lib.py`: Student scaffold file.
- `examples/mixed_precision_and_performance_lib.py`: Complete reference implementation.
- `tests/test_mixed_precision_and_performance_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/mixed_precision_and_performance_lib.py
```

## What the commands do
- Calculates VRAM memory footprints across model parameter scales.
- Simulates dynamic loss scaling adjustments.
- Runs unit test assertions.

## Expected output
```
Mixed Precision Demo: 7B Model Static VRAM = 104.31 GB, Scale after overflow = 32768.0
```

## Validation steps
1. Verify `calculate_adamw_vram_gb` allocates 16 bytes per model parameter.
2. Confirm `MockDynamicLossScaler` halves scale upon overflow detection.
3. Confirm `MockDynamicLossScaler` doubles scale after successful steps reach `growth_interval`.
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
- **Scale overflow:** Ensure scale factors remain within positive finite bounds ($S > 1.0$).

## Security notes
All performance benchmarks execute locally in process memory.

## Extension exercises
1. Profile `torch.compile` speedup on a Transformer encoder block.
2. Implement an FP8 simulated quantizer.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Mixed Precision and Performance
- **Day number:** 233 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-233-mixed-precision-and-performance
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-233-mixed-precision-and-performance` when the site is running.
<!-- generated-links:end -->
