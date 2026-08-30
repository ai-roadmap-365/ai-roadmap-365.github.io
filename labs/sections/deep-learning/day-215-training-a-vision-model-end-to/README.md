# Lab: Day 215 -- Training a Vision Model End to End

## Lesson
Day number: 215 of 365.
Course: Course05-SS01 (Deep Learning - Neural Networks).
Topic: End-to-End Vision Training and Evaluation in PyTorch.

## Purpose
Build and test an industrial-grade Computer Vision training and evaluation library in PyTorch. Implement Top-1 and Top-K classification accuracy evaluators, construct normalized confusion matrix calculators, and verify metric correctness against multi-class logit distributions.

## Learning objectives
- Calculate Top-1 and Top-K classification accuracy from raw model logits.
- Compute normalized multi-class confusion matrices.
- Analyze per-class recall and pairwise misclassification patterns.
- Implement robust evaluation routines without gradient memory leaks.

## Prerequisites
- Day 214 (Data Augmentation).
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
- `starter/training_a_vision_model_end_to_lib.py`: Student scaffold file.
- `examples/training_a_vision_model_end_to_lib.py`: Complete reference implementation.
- `tests/test_training_a_vision_model_end_to_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/training_a_vision_model_end_to_lib.py
```

## What the commands do
- Evaluates Top-1 and Top-3 accuracy on synthetic logit distributions.
- Computes normalized confusion matrix diagonal.
- Runs validation test suite.

## Expected output
```
Training Demo: Top-1 = 1.00, Top-3 = 1.00, CM Diag = [1.0, 1.0, 1.0, 1.0, 1.0]
```

## Validation steps
1. Confirm `calculate_topk_accuracy` accurately counts Top-1 and Top-K inclusion.
2. Confirm `compute_confusion_matrix` normalizes rows to sum to 1.0.
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
- **Accuracy greater than 1.0:** Verify division by float `targets.size(0)`.

## Security notes
All training metrics execute in local system memory without external telemetry.

## Extension exercises
1. Implement Exponential Moving Average (EMA) weight tracking.
2. Implement an automated Early Stopping class restoring best checkpoint weights.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Training a Vision Model End to End
- **Day number:** 215 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-215-training-a-vision-model-end-to
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-215-training-a-vision-model-end-to` when the site is running.
<!-- generated-links:end -->
