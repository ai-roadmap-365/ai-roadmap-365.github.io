# Day 278 Lab: INT8 Quantizer and GGUF Parser

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Quantized Inference and llama.cpp
- **Day number:** 278 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-278-quantized-inference-and-llama-cpp
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-278-quantized-inference-and-llama-cpp` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an INT8 symmetric tensor quantizer, dequantizer, and binary GGUF header parser from scratch in Python and NumPy.

## Learning objectives
- Parse binary GGUF header structs (magic bytes, version, tensor counts).
- Implement symmetric linear INT8 quantization ($q = 	ext{round}(x / s)$).
- Calculate Mean Squared Error (MSE) reconstruction distortion.
- Compute memory reduction and compression ratios.

## Prerequisites
- Python 3.10+ installed
- NumPy and pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, numpy, pytest

## Free and open-source options
- Python Standard Library, NumPy

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/quantizer.py`: Starter implementation skeleton
- `examples/quantizer.py`: Verified reference implementation
- `tests/test_quantizer.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/quantizer.py
```

## What the commands do
- Packs and validates GGUF binary headers and quantizes 2D float tensors to INT8.

## Expected output
```text
[GGUF] Magic: GGUF | Version: 3 | Tensors: 291
[QUANT] Compressed 262,144 bytes to 65,540 bytes (75.0% reduction) | MSE: 0.00042
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- GGUF binary header packing and unpacking
- INT8 range clamping $[-128, 127]$
- Reconstruction MSE distortion $< 0.001$
- Zero-tensor safety

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Check that scale factor uses `max(|x|) / 127.0`.

## Security notes
Runs completely offline on local CPU using standard NumPy arrays.

## Extension exercises
Implement asymmetric affine quantization with integer zero-point offsets.

## Navigation
Day number: 278 of 365
