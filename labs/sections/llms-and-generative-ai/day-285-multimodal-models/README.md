# Day 285 Lab: Multimodal Models & CLIP InfoNCE Loss

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Multimodal Models
- **Day number:** 285 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-285-multimodal-models
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-285-multimodal-models` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Vision-Language foundation pipeline in Python and NumPy implementing symmetric CLIP InfoNCE contrastive loss, zero-shot image classification, and MLP multimodal projection.

## Learning objectives
- Implement symmetric InfoNCE loss for batch multimodal alignment.
- Build an MLP Multimodal Projector with GELU activation.
- Execute zero-shot image-text classification.
- Calculate patch token grid geometries.

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
- `starter/multimodal_models.py`: Starter implementation skeleton
- `examples/multimodal_models.py`: Verified reference implementation
- `tests/test_multimodal_models.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/multimodal_models.py
```

## What the commands do
- Evaluates InfoNCE loss and zero-shot classification math.

## Expected output
```text
[CLIP INFONCE] Loss = 0.124 on aligned batch.
[ZERO-SHOT] Top prediction: 'cat' (Confidence: 98.4%)
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- InfoNCE loss minimization on aligned pairs
- Cross-entropy symmetry along rows and columns
- Zero-shot cosine softmax classification
- MLP projector shape transformation

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Check that `temperature` scale is applied before computing exponents.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement visual bounding box coordinate denormalization `[ymin, xmin, ymax, xmax] -> pixels`.

## Navigation
Day number: 285 of 365
